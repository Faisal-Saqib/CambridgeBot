// Camp farming. Each champion claims a camp group in shared memory and
// clears it together, which keeps dangerous camps cheap (damage taken falls
// with team damage) and keeps champions together for fights. Around harmless
// targets (gem and gold clusters) the squad spreads over neighbouring
// clusters. One champion captures each cleared group; the rest move on.
use crate::bot::{Bot, LiveCamp};
use crate::kb::{camp_design, NO_DIST};
use crate::log;
use crate::comm::SLOTS;
use crate::util::{cheb, me};
use cambc::{AbilityInfo, CampGroupState, ChampionType, Result};


impl Bot {
    /// Alive camps of a group currently in vision; also refreshes HP memory.
    pub fn live_camps(&mut self, g: usize) -> Vec<LiveCamp> {
        let mut out = Vec::new();
        let n = self.kb.groups[g].camps.len();
        for i in 0..n {
            let sp = self.kb.groups[g].camps[i].0;
            if !self.visible(sp) {
                continue;
            }
            let camp = self.kb.groups[g].cg.camps()[i].clone();
            let Ok(st) = camp.state() else { continue };
            if st.is_dead() {
                self.camp_hp[g][i] = 0.0;
                continue;
            }
            let hp = camp.health().unwrap_or(0.0);
            self.camp_hp[g][i] = hp;
            out.push(LiveCamp { pos: camp.position().unwrap_or(sp), kind: camp.kind(), awake: st.is_awake(), camp, hp });
        }
        out
    }

    /// Expected tank damage for clearing the remaining dangerous camps of g.
    pub fn group_damage(&self, g: usize, dps: f32) -> f32 {
        let grp = &self.kb.groups[g];
        let mut dangerous: Vec<(f32, f32)> = grp
            .camps
            .iter()
            .enumerate()
            .filter_map(|(i, c)| {
                let d = camp_design(c.1);
                let hp = self.camp_hp[g][i];
                (d.dmg > 0.0 && hp > 0.0).then_some((d.dmg, hp))
            })
            .collect();
        dangerous.sort_by(|a, b| (b.0 / b.1).partial_cmp(&(a.0 / a.1)).unwrap());
        let mut remaining: f32 = dangerous.iter().map(|d| d.0).sum();
        let mut total = 0.0;
        for (dmg, hp) in dangerous {
            total += remaining * hp / dps;
            remaining -= dmg;
        }
        total
    }

    fn group_value(&self, g: usize) -> f32 {
        let grp = &self.kb.groups[g];
        let gold_w = if self.round < 300 { 0.15 } else if self.round < 800 { 0.08 } else { 0.03 };
        grp.gems as f32 + grp.gold as f32 * gold_w
    }

    fn harmless(&self, g: usize) -> bool {
        self.kb.groups[g].danger_dps <= 0.0
    }

    fn claimants(&self, g: usize) -> usize {
        (0..SLOTS).filter(|&s| s != self.slot && self.comm.claim_of(s) == Some(g)).count()
    }

    fn reachable(&mut self, g: usize) -> Result<Option<f32>> {
        let center = self.kb.groups[g].center;
        if self.kb.fields[g].is_none() && crate::util::fuel() > self.kb.field_cost() + 25_000 {
            self.kb.ensure_field(g)?;
        }
        let d = self.kb.dist_or_estimate(g, self.pos, center)?;
        Ok((d != NO_DIST).then_some(d as f32))
    }

    fn job_score(&mut self, g: usize) -> Result<Option<f32>> {
        let grp = &self.kb.groups[g];
        if grp.gems == 0 && grp.gold == 0 || self.group_block[g] > self.round {
            return Ok(None);
        }
        if let Some((gg, _, _)) = self.gate_now {
            if g == gg {
                return Ok(self.gate_assault().then_some(1e6));
            }
        }
        let claim = self.claimants(g);
        let dangerous = !self.harmless(g);
        // Small teams move as one ball: a lone champion on a 3-pick map is
        // what an aggressive trio farms for kills. (Measured neutral against
        // titan in mirror games; off until it shows a gain.)
        let ball = false;
        // Big harmless blocks take several champions; a lone cluster needs one.
        let harmless_cap = ((self.group_hp(g) / 700.0).ceil() as usize).clamp(1, 5);
        // Caps limit joining; a champion already on the job keeps it.
        let joining = self.job != Some(g);
        // A jackpot takes the whole team: no join cap.
        let jackpot = self.kb.jackpot(g);
        if !ball && !jackpot && joining && ((!dangerous && claim >= harmless_cap) || claim >= 4) {
            return Ok(None);
        }
        let center = grp.center;
        let Some(travel) = self.reachable(g)? else { return Ok(None) };
        let wait = (self.respawn_at[g] as f32 - self.round as f32 - travel).max(0.0);
        if wait > 25.0 {
            return Ok(None);
        }
        let n = (claim + 1) as f32;
        let p = self.my_dps();
        let clear = self.group_hp(g) / (p * n);
        let dmg = self.group_damage(g, p * n);
        // Each HP bar spent costs a trip home: recall plus the walk back.
        let back = self.kb.dist_or_estimate(g, self.kb.spawn_center, center)? as f32;
        let bar = (self.max_hp * 0.6).max(300.0);
        let heal_time = dmg / bar * (6.0 + back);
        let mut value = self.group_value(g);
        let mut time = travel + wait + clear + heal_time / n + 6.0;
        if !dangerous {
            // Harmless neighbours can be chained one after another.
            let mut chained = 0;
            for h in 0..self.kb.groups.len() {
                if h == g || chained >= 6 {
                    continue;
                }
                let o = &self.kb.groups[h];
                if o.danger_dps > 0.0 || cheb(o.center, center) > 5 {
                    continue;
                }
                if self.respawn_at[h] > self.round + travel as u32 || self.claimants(h) > 0 {
                    continue;
                }
                value += self.group_value(h);
                time += cheb(o.center, center) as f32 + self.group_hp(h) / p + 6.0;
                chained += 1;
            }
        }
        let mut score = value / time.max(1.0) / n;
        if ball && claim > 0 {
            // Joining the ball is worth the split reward.
            score *= n * 1.5;
        }
        // Early on, stay off the enemy side of the map.
        let d_us = cheb(center, self.kb.spawn_center) as f32;
        let d_them = cheb(center, self.kb.enemy_spawn_center) as f32;
        if d_them < d_us * 0.7 {
            score *= if self.round < 250 { 0.4 } else { 0.75 };
        }
        // Stay away from where enemies were just seen or where we just died.
        let hot = self.enemy_seen_at.iter().filter(|(q, r)| cheb(*q, center) <= 8 && *r + 40 > self.round).count();
        if hot >= 2 {
            score *= 0.6;
        }
        if let Some((dp, dr)) = self.death_pos {
            if dr + 120 > self.round && cheb(dp, center) <= 8 {
                score *= 0.5;
            }
        }
        if self.job == Some(g) {
            score *= 1.25;
        }
        Ok(Some(score))
    }

    fn choose_job(&mut self) -> Result<Option<usize>> {
        let mut best: Option<(f32, usize)> = None;
        // Nearest first, so a fuel-out still leaves sensible candidates scored.
        let mut order: Vec<(i32, usize)> =
            (0..self.kb.groups.len()).map(|g| (cheb(self.pos, self.kb.groups[g].center), g)).collect();
        order.sort();
        for (_, g) in order {
            if crate::util::fuel() < 12_000 {
                break;
            }
            if let Some(score) = self.job_score(g)? {
                if best.map_or(true, |b| score > b.0) {
                    best = Some((score, g));
                }
            }
        }
        Ok(best.map(|b| b.1))
    }

    fn set_job(&mut self, job: Option<usize>) -> Result<()> {
        if self.job != job {
            if let Some(g) = job {
                let grp = &self.kb.groups[g];
                log!(self, "job -> g{} gems {} gold {} hp {:.0} claim {} at {},{}", g, grp.gems, grp.gold,
                    self.group_hp(g), self.claimants(g), grp.center.x, grp.center.y);
            }
            self.job_since = self.round;
        }
        self.job = job;
        self.comm.set_claim(self.slot, job)
    }

    pub fn farm(&mut self) -> Result<()> {
        if let Some(g) = self.capture_on {
            if self.do_capture(g)? {
                return Ok(());
            }
        }
        let job = if self.job.is_none() || self.round % 5 == 0 { self.choose_job()? } else { self.job };
        self.set_job(job)?;
        let Some(g) = job else { return Ok(()) };
        let vis = self.kb.groups[g].camps.iter().any(|c| self.visible(c.0));
        if vis {
            match self.kb.groups[g].cg.state() {
                Ok(CampGroupState::Respawning(c)) => {
                    let at = self.round + c.max(0) as u32;
                    if self.respawn_at[g] + 2 < at {
                        self.reset_camp_hp(g);
                    }
                    self.respawn_at[g] = at;
                    let next = self.choose_job()?;
                    self.set_job(next)?;
                    if let Some(n) = next {
                        if n != g {
                            self.step_field(n)?;
                        } else if self.kb.groups[g].tiles.is_set(self.pos)? {
                            // Occupied spawn tiles stall the whole respawn; walk outwards
                            // (also from the middle of a solid block of tiles).
                            let tiles = self.kb.groups[g].tiles.clone();
                            let c = self.kb.groups[g].center;
                            self.step_by(|_, p| if tiles.is_set(p).unwrap_or(false) { 20.0 - cheb(p, c) as f32 } else { 0.0 })?;
                        }
                    }
                    return Ok(());
                }
                Ok(CampGroupState::RewardAvailable) => {
                    if self.should_capture(g) {
                        self.capture_on = Some(g);
                        self.capture_since = self.round;
                        self.do_capture(g)?;
                    } else {
                        self.respawn_at[g] = self.round + 6 + self.kb.groups[g].respawn as u32;
                        self.reset_camp_hp(g);
                        let next = self.choose_job()?;
                        self.set_job(next)?;
                    }
                    return Ok(());
                }
                _ => {}
            }
        }
        let camps = self.live_camps(g);
        if camps.is_empty() {
            // Camps we believe alive but cannot see (behind a wall or in a
            // bush): walk to the nearest of them instead of standing on the
            // group's tiles, where its field reads zero.
            let hidden = self.kb.groups[g]
                .camps
                .iter()
                .enumerate()
                .filter(|(i, c)| self.camp_hp[g][*i] > 0.0 && !self.visible(c.0))
                .map(|(_, c)| c.0)
                .min_by_key(|p| cheb(*p, self.pos));
            match hidden {
                Some(p) if self.kb.dist(g, self.pos)? <= 3 => {
                    self.step_to(p)?;
                }
                _ => {
                    self.step_field(g)?;
                }
            }
            return Ok(());
        }
        self.fight_camps(g, camps)
    }

    fn ally_on(&self, g: usize) -> bool {
        self.allies.iter().any(|a| self.kb.groups[g].tiles.is_set(a.pos).unwrap_or(false))
    }

    /// The capturer is the nearest of us; Marcella (gold per tributed gem)
    /// takes rewards within 8 tiles.
    fn should_capture(&self, g: usize) -> bool {
        let c = self.kb.groups[g].center;
        let my_d = cheb(self.pos, c);
        // Jackpot: everyone nearby stands on it. The reward is split among
        // the champions present, so no single carrier holds the whole haul,
        // and the team is together for the fight that always follows.
        if self.kb.jackpot(g) && self.kb.dist_or_estimate(g, self.pos, c).unwrap_or(crate::kb::NO_DIST) <= 12 {
            return true;
        }
        if self.ally_on(g) {
            return false;
        }
        let marcella_near = self.allies.iter().any(|a| a.kind == ChampionType::Marcella && cheb(a.pos, c) <= 8 && a.hp > a.max_hp * 0.3);
        if self.kind == ChampionType::Marcella && my_d <= 8 {
            return true;
        }
        if marcella_near {
            return false;
        }
        let my_slot = self.slot;
        !self.allies.iter().any(|a| {
            let d = cheb(a.pos, c);
            let s = self.team.iter().position(|t| *t == a.ch).unwrap_or(9);
            d < my_d || (d == my_d && s < my_slot)
        })
    }

    fn pick_camp_target(&self, camps: &[LiveCamp]) -> usize {
        let splash = self.kind == ChampionType::Varg;
        let mut best = (f32::MAX, 0usize);
        for (i, c) in camps.iter().enumerate() {
            let d = camp_design(c.kind);
            let dist = cheb(self.pos, c.pos) as f32;
            let mut score = if d.dmg > 0.0 { c.hp / d.dmg } else { 1000.0 + c.hp };
            if splash {
                let n = camps.iter().filter(|o| cheb(o.pos, c.pos) <= 1).count() as f32;
                score /= n;
            }
            score += dist * 3.0;
            if score < best.0 {
                best = (score, i);
            }
        }
        best.1
    }

    fn fight_camps(&mut self, g: usize, camps: Vec<LiveCamp>) -> Result<()> {
        let mut ti = self.pick_camp_target(&camps);
        if let Some((_, _, gp)) = self.gate_now.filter(|x| x.0 == g) {
            let Some(i) = camps.iter().position(|c| c.pos == gp) else {
                self.step_to(gp)?;
                return Ok(());
            };
            // Gather first: whoever arrives alone just eats both Monoliths.
            let awake = camps.iter().any(|c| c.awake);
            let near = 1 + self.allies.iter().filter(|a| cheb(a.pos, gp) <= 9 && a.hp > a.max_hp * 0.8).count();
            let need = self.alive_count.min(3);
            if !awake && near < need && self.round < self.job_since + 60 {
                let d = cheb(self.pos, gp);
                if d > 8 {
                    self.step_to(gp)?;
                } else if d < 7 {
                    self.step_by(|_, p| (7 - cheb(p, gp)).max(0) as f32)?;
                }
                return Ok(());
            }
            ti = i;
        }
        let target = camps[ti].clone();
        let tp = target.pos;
        if self.round % 10 == 0 && self.round > 60 {
            log!(self, "fight_camps g{} n {} target {:?} at {},{} hp {:.0} moved {} attacked {}", g, camps.len(), target.kind, tp.x, tp.y, target.hp, self.moved, self.attacked);
        }
        self.cast_on_camps(&camps, ti)?;
        if cheb(self.pos, tp) <= self.range {
            self.basic_attack(&target.camp, tp)?;
            return Ok(());
        }
        let rng = self.range;
        if self.kb.dist(g, self.pos)? > 4 {
            self.step_field(g)?;
        } else if cheb(self.pos, tp) > rng + 2 {
            self.step_to(tp)?;
        } else {
            self.step_by(|_, p| (cheb(p, tp) - rng).max(0) as f32 * 10.0 + cheb(p, tp) as f32 * 0.01)?;
        }
        if self.melee || !self.moved {
            if cheb(self.pos, tp) <= self.range {
                self.basic_attack(&target.camp, tp)?;
            } else if let Some(c) = camps.iter().find(|c| cheb(self.pos, c.pos) <= self.range).cloned() {
                self.basic_attack(&c.camp, c.pos)?;
            }
        }
        Ok(())
    }

    fn cast_on_camps(&mut self, camps: &[LiveCamp], ti: usize) -> Result<()> {
        if self.cast {
            return Ok(());
        }
        let awake_danger = camps.iter().any(|c| {
            let d = camp_design(c.kind);
            d.dmg > 0.0 && c.awake && cheb(c.pos, self.pos) <= d.range
        });
        for ab in me().abilities() {
            let Ok(Some(info)) = ab.info() else { continue };
            if !ab.is_ready().unwrap_or(false) {
                continue;
            }
            let ok = match info {
                AbilityInfo::Damage(a) if !self.moved => {
                    let c = &camps[ti];
                    cheb(c.pos, self.pos) as f32 <= a.range && ab.cast_on(&c.camp).unwrap_or(false)
                }
                AbilityInfo::Cc(a) if a.modifier > 0.0 || awake_danger => {
                    if a.properties.exclusive_with_movement && self.moved {
                        false
                    } else {
                        let pick = camps
                            .iter()
                            .filter(|c| cheb(c.pos, self.pos) as f32 <= a.range)
                            .max_by(|x, y| camp_design(x.kind).dmg.partial_cmp(&camp_design(y.kind).dmg).unwrap());
                        match pick {
                            Some(c) if camp_design(c.kind).dmg > 0.0 || a.modifier > 0.0 => ab.cast_on(&c.camp).unwrap_or(false),
                            _ => false,
                        }
                    }
                }
                AbilityInfo::AoeDamage(a) if !self.moved => {
                    let mut bestp = None;
                    let mut bestn = 0;
                    for c in camps {
                        if cheb(c.pos, self.pos) as f32 > a.range {
                            continue;
                        }
                        let n = camps.iter().filter(|o| cheb(o.pos, c.pos) as f32 <= a.radius).count();
                        if n > bestn {
                            bestn = n;
                            bestp = Some(c.pos);
                        }
                    }
                    match bestp {
                        Some(p) => ab.cast_at(p).unwrap_or(false),
                        None => false,
                    }
                }
                AbilityInfo::Shield(_) if awake_danger => ab.cast_untargeted().unwrap_or(false),
                _ => false,
            };
            if ok {
                self.cast = true;
                return Ok(());
            }
        }
        Ok(())
    }

    /// Stand on a spawn tile of a cleared group until the reward is captured.
    /// Returns false when there is nothing to do here.
    pub fn do_capture(&mut self, g: usize) -> Result<bool> {
        if self.round - self.capture_since > 40 {
            log!(self, "capture timeout g{}", g);
            self.capture_on = None;
            // Walking away from a contested jackpot for 100 rounds hands the
            // map over; just re-evaluate shortly.
            self.group_block[g] = self.round + if self.kb.jackpot(g) { 5 } else { 100 };
            return Ok(false);
        }
        let tiles_visible = self.kb.groups[g].camps.iter().any(|c| self.visible(c.0));
        if !tiles_visible {
            self.step_field(g)?;
            return Ok(true);
        }
        match self.kb.groups[g].cg.state() {
            Ok(CampGroupState::RewardAvailable) => {}
            Ok(CampGroupState::Respawning(c)) => {
                self.respawn_at[g] = self.round + c.max(0) as u32;
                self.reset_camp_hp(g);
                if self.kb.groups[g].tiles.is_set(self.pos)? {
                    let now = me().gem_count()?;
                    let items = me().item_count()?;
                    let pro = items[cambc::get_item_enum(cambc::ItemFamily::Prospector, cambc::ItemStat::Strength, false)] + items[cambc::get_item_enum(cambc::ItemFamily::Prospector, cambc::ItemStat::Focus, false)];
                    let cap = items[cambc::get_item_enum(cambc::ItemFamily::Capture, cambc::ItemStat::Strength, false)] + items[cambc::get_item_enum(cambc::ItemFamily::Capture, cambc::ItemStat::Focus, false)];
                    println!("CAPTEST r{} g{} value {} before {} now {} took {} prospector {} capture {} allies_on {}", self.round, g, self.kb.groups[g].gems, self.cap_before, now, self.round - self.capture_since, pro, cap, self.allies.iter().filter(|a| self.kb.groups[g].tiles.is_set(a.pos).unwrap_or(false)).count());
                    log!(self, "captured g{} gems now {}", g, me().gem_count()?);
                }
                self.capture_on = None;
                // Step off the spawn tiles so the group can respawn.
                let tiles = self.kb.groups[g].tiles.clone();
                self.step_by(|_, p| if tiles.is_set(p).unwrap_or(false) { 1.0 } else { 0.0 })?;
                return Ok(false);
            }
            _ => {
                self.capture_on = None;
                return Ok(false);
            }
        }
        let on_tile = self.kb.groups[g].tiles.is_set(self.pos)?;
        if self.ally_on(g) && !on_tile && !self.kb.jackpot(g) {
            self.capture_on = None;
            self.respawn_at[g] = self.round + 6 + self.kb.groups[g].respawn as u32;
            return Ok(false);
        }
        // Contested: an enemy stands somewhere on the region (the_line's row
        // is 15 tiles long, so both sides can sit on opposite ends forever).
        // Holding our tile resets nothing — go and remove them.
        let contested = matches!(
            self.kb.groups[g].cg.capture_state().map(|s| s.state),
            Ok(cambc::CampGroupCaptureType::Contested)
        );
        if contested {
            let tiles = &self.kb.groups[g].tiles;
            let c = self.kb.groups[g].center;
            let squatter = self
                .enemies
                .iter()
                .filter(|e| tiles.is_set(e.pos).unwrap_or(false) || cheb(e.pos, c) <= 3)
                .min_by_key(|e| cheb(e.pos, self.pos))
                .cloned();
            if let Some(e) = squatter {
                let others = self.enemies.clone();
                self.attack_champion(&e, &others, false)?;
                return Ok(true);
            }
            // The squatter is out of sight (a long region: both ends can be
            // further apart than vision). Walk toward the part of the region
            // we cannot see instead of holding a tile forever.
            if let Ok(ps) = self.kb.groups[g].tiles.positions() {
                if let Some(far) = ps.into_iter().filter(|p| !self.visible(*p)).max_by_key(|p| cheb(*p, self.pos)) {
                    self.step_to(far)?;
                    return Ok(true);
                }
            }
        }
        if on_tile {
            self.cap_before = self.gems;
        }
        if on_tile {
            // Hold the tile and fight from it.
            if let Some(e) = self.enemies.iter().filter(|e| cheb(e.pos, self.pos) <= 4).min_by(|a, b| a.hp.partial_cmp(&b.hp).unwrap()).cloned() {
                self.cast_offensive_on_champion(&e)?;
                self.basic_attack(&e.ch, e.pos)?;
            }
            return Ok(true);
        }
        let tiles = self.kb.groups[g].tiles.clone();
        let field = self.kb.fields[g].take();
        self.step_by(|_, p| {
            if tiles.is_set(p).unwrap_or(false) {
                -1.0
            } else {
                field.as_ref().map_or(0.0, |f| f.get(p).unwrap_or(NO_DIST) as f32)
            }
        })?;
        self.kb.fields[g] = field;
        Ok(true)
    }
}
