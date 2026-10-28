// Champion versus champion combat: assess the local fight, focus a target,
// call teammates, and fall back when outmatched.
use crate::bot::{Bot, Enemy};
use crate::log;
use crate::util::{cheb, me};
use cambc::{AbilityInfo, Result, Vec2};

/// Aggressive play: take even fights, join teammates' fights from further
/// away and run down hurt enemies instead of waiting to be picked off.
/// (Measured over all 70 maps: 61-79 against titan — even on 3-pick maps,
/// worse on bigger ones where farm time matters. Off.)
const HUNT: bool = false;

/// Fight turns without any hit landed before a standoff is abandoned
/// (0 disables). 8 measured 65-75 against titan over all 70 maps: off.
const STANDOFF_LIMIT: u32 = 0;

impl Bot {
    /// Hunt everywhere when HUNT is set; otherwise only on maps whose gems sit in a
    /// harmless jackpot (the_line): those maps are decided by who wins the brawl
    /// over the jackpot, and an aggressive copy of titan beat every passive variant there.
    pub fn hunting(&self) -> bool {
        HUNT || self.kb.brawl_map
    }

    /// Enemies sitting on their own spawn heal every turn; ignore them unless
    /// they can hit us from there.
    fn relevant(&self, e: &Enemy) -> bool {
        !e.on_spawn || (cheb(e.pos, self.pos) <= e.range && self.taken > 0.5)
    }

    fn target_score(&self, e: &Enemy, focus: Option<usize>) -> f32 {
        let d = cheb(e.pos, self.pos);
        let reach = (d - self.range).max(0) as f32;
        // Cheapest kill first (HP per damage); gem carriers preferred.
        let mut score = e.hp / e.dps.max(10.0) + reach * 4.0;
        score *= 1.0 - (e.gems.min(60) as f32 / 150.0);
        if focus == Some(e.idx) {
            score *= 0.3;
        }
        score
    }

    /// Champion fights, judged by time to kill: the rounds our nearby side
    /// needs to wipe theirs against the rounds they need for ours.
    pub fn fight_enemies(&mut self) -> Result<bool> {
        let relevant: Vec<Enemy> = self
            .enemies
            .iter()
            .filter(|e| self.relevant(e) && cheb(e.pos, self.pos) <= 10)
            .cloned()
            .collect();
        if relevant.is_empty() || self.taken > 0.5 {
            self.standoff = 0;
        }
        if relevant.is_empty() {
            self.hold_turns = 0;
            return Ok(false);
        }
        let (mut adps, mut ahp) = (self.my_dps(), self.hp);
        for a in self.allies.iter().filter(|a| cheb(a.pos, self.pos) <= 8) {
            adps += a.dps;
            ahp += a.hp;
        }
        let (mut edps, mut ehp, mut threat) = (0.0f32, 0.0f32, 0.0f32);
        for e in &relevant {
            edps += e.dps;
            ehp += e.hp;
            if cheb(e.pos, self.pos) <= e.range + 1 {
                threat += e.dps;
            }
        }
        // Standoff: both sides holding at the edge of range (ranged mirrors
        // stood still for most of a game). When nobody has landed a hit for a
        // while, nothing can reach us and no teammate is in it, go farm.
        let in_their_range = relevant.iter().any(|e| cheb(e.pos, self.pos) <= e.range);
        if STANDOFF_LIMIT > 0 && self.standoff >= STANDOFF_LIMIT && !in_their_range {
            let ally_fighting = relevant
                .iter()
                .any(|e| self.allies.iter().any(|a| cheb(a.pos, e.pos) <= e.range.max(2)));
            if !ally_fighting {
                return Ok(false);
            }
        }
        let nearest = relevant.iter().min_by_key(|e| cheb(e.pos, self.pos)).cloned().unwrap();
        let nearest_d = cheb(nearest.pos, self.pos);
        let careful = self.recent_deaths() >= 3;
        // Chamero: count the enemy group a little wider (was 6): top teams move
        // as a five-champion ball and picked our champions off one by one.
        let theirs = relevant.iter().filter(|e| cheb(e.pos, self.pos) <= 8).count();
        let ours = 1 + self.allies.iter().filter(|a| cheb(a.pos, self.pos) <= 6).count();
        let outnumbered = theirs > ours;
        let we_need = ehp / adps.max(1.0);
        let they_need = ahp / edps.max(1.0);
        let losing = we_need > they_need * if careful { 1.0 } else { 1.3 };
        let bag = self.gems >= 30;
        let clearly_losing = we_need > they_need * if bag { 1.0 } else if careful { 1.3 } else { 1.6 } || outnumbered;
        if nearest_d > 7 {
            // A group coming our way that we cannot fight: leave before it arrives.
            if !losing {
                // Hunt: with the numbers on our side, go take the fight
                // instead of farming until they pick the moment.
                let theirs_wide = relevant.iter().filter(|e| !e.on_spawn).count();
                let ours_wide = 1 + self.allies.iter().filter(|a| cheb(a.pos, self.pos) <= 8).count();
                if self.hunting() && ours_wide >= theirs_wide.max(1) && !bag && self.frac() > 0.5 {
                    let focus = self.comm.focus();
                    if let Some(g) = relevant
                        .iter()
                        .filter(|e| !e.on_spawn)
                        .min_by(|a, b| self.target_score(a, focus).partial_cmp(&self.target_score(b, focus)).unwrap())
                        .cloned()
                    {
                        self.comm.set_focus(Some(g.idx))?;
                        self.attack_champion(&g, &relevant, false)?;
                        return Ok(true);
                    }
                }
                return Ok(false);
            }
            log!(self, "leave: {} enemies at {} (need {:.1} vs {:.1})", relevant.len(), nearest_d, we_need, they_need);
            let threats = self.camp_threats();
            self.flee(&threats)?;
            return Ok(true);
        }
        // Target: the enemy in reach this turn that dies soonest; the team's
        // focus when we can reach it.
        let reach = if self.melee { self.range + 1 } else { self.range };
        let focus = self.comm.focus();
        let target = relevant
            .iter()
            .filter(|e| !e.on_spawn && cheb(e.pos, self.pos) <= reach)
            .min_by(|a, b| self.target_score(a, focus).partial_cmp(&self.target_score(b, focus)).unwrap())
            .cloned();
        if let Some(t) = &target {
            self.comm.set_focus(Some(t.idx))?;
        }
        let can_finish = target.as_ref().map_or(false, |t| t.hp <= me().strength().unwrap_or(0.0) * 1.05);
        let in_danger = self.hp < threat * 2.5 + self.max_hp * 0.1;
        let beside = self.allies.iter().filter(|a| cheb(a.pos, self.pos) <= 3).count();
        let committed = beside >= 1 && !clearly_losing && self.frac() > 0.25;
        // Chamero: leave earlier. Waiting until the nearest enemy was within its
        // range + 2 was too late against dashes and range-4 stuns.
        let mut retreat = (in_danger || (clearly_losing && nearest_d <= nearest.range + 4) || (outnumbered && nearest_d <= 7))
            && !can_finish
            && !committed;
        // Running from an adjacent melee champion only hands it free hits.
        if retreat && nearest.range <= 1 && nearest_d <= 2 && target.as_ref().map_or(false, |t| cheb(t.pos, self.pos) <= self.range) {
            retreat = false;
        }
        if retreat {
            log!(self, "retreat from fight: need {:.1} vs {:.1} danger {} outnumbered {}", we_need, they_need, in_danger, outnumbered);
            if let Some(t) = &target {
                self.cast_offensive_on_champion(t)?;
                self.basic_attack(&t.ch, t.pos)?;
            }
            let threats = self.camp_threats();
            self.flee(&threats)?;
            return Ok(true);
        }
        // Join a teammate's fight: hit the enemy on it.
        if !in_danger && !bag && target.is_none() {
            let join_radius = if self.hunting() { 10 } else { 7 };
            let help = relevant
                .iter()
                .filter(|e| !e.on_spawn && cheb(e.pos, self.pos) <= join_radius)
                .filter(|e| self.allies.iter().any(|a| cheb(a.pos, e.pos) <= e.range.max(2)))
                .min_by_key(|e| if focus == Some(e.idx) { -1 } else { cheb(e.pos, self.pos) })
                .cloned();
            if let Some(h) = help {
                if !clearly_losing {
                    self.attack_champion(&h, &relevant, true)?;
                    log!(self, "join fight on {:?} hp {:.0}", h.ch.champion_name().ok(), h.hp);
                    return Ok(true);
                }
            }
        }
        if let Some(t) = target {
            self.hold_turns = 0;
            self.attack_champion(&t, &relevant, true)?;
            log!(self, "fight {:?} hp {:.0} need {:.1} vs {:.1}", t.ch.champion_name().ok(), t.hp, we_need, they_need);
            return Ok(true);
        }
        // Hunting also runs down a hurt enemy while the fight isn't clearly lost.
        let chase_hurt = self.hunting() && !clearly_losing && !outnumbered && !bag
            && relevant.iter().any(|e| !e.on_spawn && e.hp < e.max_hp * 0.45);
        if (!losing && !outnumbered) || chase_hurt {
            // Engage rather than keep farming while an enemy picks its moment.
            let engage_radius = if self.hunting() { 8 } else { 5 };
            let goal = relevant
                .iter()
                .filter(|e| !e.on_spawn && cheb(e.pos, self.pos) <= engage_radius)
                .min_by(|a, b| self.target_score(a, focus).partial_cmp(&self.target_score(b, focus)).unwrap())
                .cloned();
            if let Some(g) = goal {
                let busy = self.allies.iter().any(|a| cheb(a.pos, g.pos) <= 2);
                let low = g.hp <= me().strength().unwrap_or(0.0) * 2.0;
                // A ranged champion that steps in cannot shoot this turn: let it come.
                if !self.melee && !busy && !low && self.hold_turns < 6 {
                    self.hold_turns += 1;
                    return Ok(true);
                }
                self.hold_turns = 0;
                self.attack_champion(&g, &relevant, false)?;
                return Ok(true);
            }
        }
        Ok(false)
    }

    pub fn attack_champion(&mut self, target: &Enemy, others: &[Enemy], _hold: bool) -> Result<()> {
        let tp = target.pos;
        let d = cheb(tp, self.pos);
        if d <= 4 {
            self.cast_offensive_on_champion(target)?;
        }
        if d <= self.range {
            self.basic_attack(&target.ch, tp)?;
            return Ok(());
        }
        let rng = self.range;
        if self.melee {
            self.step_by(|_, p| (cheb(p, tp) - rng).max(0) as f32 * 10.0 + cheb(p, tp) as f32 * 0.1)?;
        } else {
            // Ranged: let enemies walk into range rather than give up the shot,
            // unless the target is fleeing hurt.
            let hold = d <= rng + 1 && target.hp > target.max_hp * 0.35;
            if !hold {
                self.step_by(|_, p| (cheb(p, tp) - rng).max(0) as f32)?;
            }
        }
        if self.melee || !self.moved {
            if cheb(self.pos, tp) <= self.range {
                self.basic_attack(&target.ch, tp)?;
            } else if let Some(o) = others.iter().find(|o| cheb(o.pos, self.pos) <= self.range).cloned() {
                self.basic_attack(&o.ch, o.pos)?;
            }
        }
        Ok(())
    }

    pub fn basic_attack<T: cambc::AttackTarget + ?Sized>(&mut self, t: &T, tp: Vec2) -> Result<()> {
        let me = me();
        if self.attacked || cheb(self.pos, tp) > self.range || !me.can_attack()? {
            return Ok(());
        }
        if me.attack(t).is_ok() {
            self.attacked = true;
            if !self.cast {
                for ab in me.abilities() {
                    if let Ok(Some(AbilityInfo::AttackReset(_))) = ab.info() {
                        if ab.is_ready().unwrap_or(false) && ab.cast_untargeted().unwrap_or(false) {
                            self.cast = true;
                            me.attack(t).ok();
                            break;
                        }
                    }
                }
            }
        }
        Ok(())
    }

    pub fn cast_offensive_on_champion(&mut self, target: &Enemy) -> Result<()> {
        if self.cast {
            return Ok(());
        }
        let d = cheb(target.pos, self.pos);
        for ab in me().abilities() {
            let Ok(Some(info)) = ab.info() else { continue };
            if !ab.is_ready().unwrap_or(false) {
                continue;
            }
            let ok = match info {
                AbilityInfo::Damage(a) if d as f32 <= a.range && !self.moved => ab.cast_on(&target.ch).unwrap_or(false),
                AbilityInfo::Cc(a) if d as f32 <= a.range && (!a.properties.exclusive_with_movement || !self.moved) => {
                    ab.cast_on(&target.ch).unwrap_or(false)
                }
                AbilityInfo::AoeDamage(a) if d as f32 <= a.range && !self.moved => ab.cast_at(target.pos).unwrap_or(false),
                AbilityInfo::Shield(_) if d <= 2 => ab.cast_untargeted().unwrap_or(false),
                AbilityInfo::Dash(a) if a.modifier > 0.0 && d <= 3 && !self.moved => {
                    // Damaging dash (Heart of Ruin): land next to the target.
                    let mut ok = false;
                    for dir in crate::util::DIRS {
                        let p = target.pos + dir;
                        if cheb(p, self.pos) <= 2 && self.free(p) {
                            if ab.cast_at(p).unwrap_or(false) {
                                self.pos = p;
                                ok = true;
                            }
                            break;
                        }
                    }
                    ok
                }
                _ => false,
            };
            if ok {
                self.cast = true;
                return Ok(());
            }
        }
        Ok(())
    }

    /// Heals and shields that help regardless of what else we did this turn.
    pub fn support_spells(&mut self) {
        if self.cast {
            return;
        }
        for ab in me().abilities() {
            let Ok(Some(AbilityInfo::Heal(a))) = ab.info() else { continue };
            if !ab.is_ready().unwrap_or(false) {
                continue;
            }
            let heal = a.modifier * me().focus().unwrap_or(100.0);
            let pick = self
                .allies
                .iter()
                .filter(|al| cheb(al.pos, self.pos) as f32 <= a.range && al.hp > 0.0)
                .max_by(|x, y| (x.max_hp - x.hp).partial_cmp(&(y.max_hp - y.hp)).unwrap());
            if let Some(al) = pick {
                if al.max_hp - al.hp >= heal * 0.6 || al.hp < al.max_hp * 0.4 {
                    if ab.cast_on(&al.ch).unwrap_or(false) {
                        self.cast = true;
                    }
                }
            }
        }
    }

    /// While channelling a tribute, cancel if enemies would kill us first.
    pub fn guard_tribute(&mut self) -> Result<()> {
        let me = me();
        let hp = me.health()?;
        let remaining = me.remaining_channel_time().unwrap_or(1).max(0) as f32 + 1.0;
        let dmg: f32 = self
            .enemies
            .iter()
            .filter(|e| cheb(e.pos, self.pos) <= e.range + 2)
            .map(|e| e.dps)
            .sum();
        let banked = cambc::global_submitted_gems(cambc::Team::Ally).unwrap_or(0);
        if dmg * remaining > hp * 0.9 && banked + self.gems < 1000 {
            self.round = cambc::round_number()?;
            log!(self, "cancel tribute: danger {:.0} vs hp {:.0}", dmg * remaining, hp);
            me.cancel_submit_gems().ok();
        }
        Ok(())
    }
}
