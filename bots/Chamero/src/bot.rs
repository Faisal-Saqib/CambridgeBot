// Per-champion state and the turn loop. Behaviour lives in sibling modules:
// nav (movement), fight (champion combat), farm (camps, squad, capture),
// bank (tributes) and heal (retreat and recovery).
//
// Camps keep their damage while asleep and never chase, so a hurt champion
// can always step out of range, heal at spawn and come back. The real cost of
// a dangerous camp is therefore HP, paid back as trips to spawn; target
// scoring prices that in.
use crate::comm::Comm;
use crate::kb::{camp_design, Kb};
use crate::log;
use crate::shop;
use crate::util::{cheb, me};
use cambc::{AbilityInfo, Bitboard, Camp, CampType, Champion, ChampionState, ChampionType, Result, Team, Vec2};

#[derive(Clone)]
pub struct Enemy {
    pub ch: Champion,
    pub pos: Vec2,
    pub hp: f32,
    pub max_hp: f32,
    pub gems: u32,
    pub range: i32,
    pub dps: f32,
    pub on_spawn: bool,
    pub idx: usize,
}

#[derive(Clone)]
pub struct Ally {
    pub ch: Champion,
    pub pos: Vec2,
    pub hp: f32,
    pub max_hp: f32,
    pub melee: bool,
    pub dps: f32,
    pub kind: ChampionType,
}

#[derive(Clone)]
pub struct LiveCamp {
    pub camp: Camp,
    pub pos: Vec2,
    pub hp: f32,
    pub kind: CampType,
    pub awake: bool,
}

/// Strength and Focus multipliers giving damage per round, with spells
/// averaged over their cooldowns; cached per champion type.
fn dps_model(ch: &Champion) -> (f32, f32) {
    static mut CACHE: [Option<(f32, f32)>; 16] = [None; 16];
    let Ok(kind) = ch.champion_name() else { return (1.12, 0.22) };
    let k = (kind as usize).min(15);
    // SAFETY: bots run single-threaded.
    if let Some(m) = unsafe { CACHE[k] } {
        return m;
    }
    let (mut s, mut f) = (1.0f32, 0.0f32);
    for ab in ch.abilities() {
        let Ok(Some(info)) = ab.info() else { continue };
        let cd = |p: &cambc::AbilityProperties| p.max_cooldown.max(1) as f32;
        match info {
            AbilityInfo::AttackReset(a) => s += 1.0 / cd(&a.properties),
            AbilityInfo::Damage(a) => f += a.modifier / cd(&a.properties),
            AbilityInfo::Cc(a) => f += a.modifier / cd(&a.properties),
            AbilityInfo::AoeDamage(a) => f += a.modifier * 1.5 / cd(&a.properties),
            AbilityInfo::Dash(a) => f += a.modifier * 1.5 / cd(&a.properties),
            _ => {}
        }
    }
    if ch.passive().ok() == Some(cambc::PassiveType::SplashAttack) {
        s += 0.5;
    }
    unsafe { CACHE[k] = Some((s, f)) };
    (s, f)
}

/// Damage per round of a visible champion: basic attacks plus spells.
pub fn champion_dps(ch: &Champion) -> f32 {
    let (ms, mf) = dps_model(ch);
    ch.strength().unwrap_or(40.0) * ms + ch.focus().unwrap_or(100.0) * mf
}

pub struct Bot {
    pub kb: Kb,
    pub kind: ChampionType,
    pub slot: usize,
    pub melee: bool,
    pub range: i32,
    pub team: Vec<Champion>,
    pub enemy_team: Vec<Champion>,
    pub alive_count: usize,
    pub respawn_at: Vec<u32>,
    /// Last seen HP of each camp, aligned with `kb.groups[g].camps`.
    pub camp_hp: Vec<Vec<f32>>,
    /// Round each group was last in vision.
    pub group_seen: Vec<u32>,
    pub job: Option<usize>,
    pub job_since: u32,
    pub gate_now: Option<(usize, usize, Vec2)>,
    pub solo: bool,
    pub wait_since: Option<u32>,
    pub capture_on: Option<usize>,
    pub capture_since: u32,
    pub healing: bool,
    pub precompute: Vec<usize>,
    pub gems: u32,
    pub stuck: u32,
    pub altar_block: Vec<u32>,
    pub group_block: Vec<u32>,
    pub prof: [u32; 10],
    pub was_dead: bool,
    pub deaths_seen: Vec<u32>,
    pub alive_flags: Vec<bool>,
    pub death_pos: Option<(Vec2, u32)>,
    pub call_field: Option<(Vec2, crate::kb::Field)>,
    pub enemy_seen_at: Vec<(Vec2, u32)>,
    /// Per enemy (by team index): last position and round seen off their spawn.
    pub last_seen: [Option<(Vec2, u32)>; 6],
    pub last_hp: f32,
    pub hit_round: u32,
    pub taken: f32,
    pub trail: std::collections::VecDeque<String>,
    pub team_center: Option<Vec2>,
    pub plan_origin: Vec2,
    pub none_since: Option<u32>,
    pub last_shop_trip: u32,
    /// Retreat progress: best distance home so far and turns without improving it.
    pub flee_best: u16,
    pub flee_stall: u32,
    pub hold_turns: u32,
    /// Consecutive fight turns in which nobody landed a hit on anyone.
    pub standoff: u32,
    /// Chamero: waiting next to a respawning job camp this turn (not stuck).
    pub waiting: bool,
    // per-turn state
    pub round: u32,
    pub pos: Vec2,
    pub hp: f32,
    pub max_hp: f32,
    pub moved: bool,
    pub attacked: bool,
    pub cast: bool,
    pub occupied: Bitboard,
    pub enemies: Vec<Enemy>,
    pub allies: Vec<Ally>,
    pub comm: Comm,
    pub guard_sequence: u8,
    pub guard_seen: Option<u32>,
}

impl Bot {
    pub fn new() -> Result<Self> {
        let me = me();
        let kb = Kb::new()?;
        let kind = me.champion_name()?;
        let team = cambc::champions(Some(Team::Ally))?;
        let slot = team.iter().position(|c| c == me).unwrap_or(7);
        let range = me.attack_range()?;
        let ngroups = kb.groups.len();
        // Precompute fields nearest-first from spawn; spawn and altars early.
        let start = me.position()?;
        let mut order: Vec<(i32, usize)> = (0..ngroups).map(|g| (cheb(start, kb.groups[g].center), g)).collect();
        order.sort();
        let mut precompute: Vec<usize> = vec![kb.spawn_field()];
        for (i, &(_, g)) in order.iter().enumerate() {
            precompute.push(g);
            if i == 2 {
                for a in 0..kb.altars.len() {
                    precompute.push(kb.altar_field(a));
                }
            }
        }
        for a in 0..kb.altars.len() {
            if !precompute.contains(&kb.altar_field(a)) {
                precompute.push(kb.altar_field(a));
            }
        }
        precompute.reverse(); // popped from the back
        let camp_hp = kb.groups.iter().map(|g| g.camps.iter().map(|c| camp_design(c.1).hp).collect()).collect();
        let nalt = kb.altars.len();
        if crate::util::SCAN && slot == 0 {
            println!("SCAN map {}x{} altars {} groups {} total_gems {} brawl {}", kb.w, kb.h, kb.altars.len(), kb.groups.len(), kb.total_gems, kb.brawl_map);
            for (i, g) in kb.groups.iter().enumerate() {
                println!("SCANG {} gems {} gold {} hp {:.0} dps {:.0} n {} dus {} dthem {} mono {}", i, g.gems, g.gold, g.hp, g.danger_dps, g.camps.len(), cheb(g.center, kb.spawn_center), cheb(g.center, kb.enemy_spawn_center), g.monolith);
            }
        }
        Ok(Self {
            respawn_at: vec![0; ngroups],
            group_block: vec![0; ngroups],
            altar_block: vec![0; nalt],
            camp_hp,
            group_seen: vec![0; ngroups],
            kb,
            kind,
            slot,
            melee: range <= 1,
            range,
            alive_count: team.len(),
            team,
            enemy_team: cambc::champions(Some(Team::Enemy))?,
            job: None,
            job_since: 0,
            gate_now: None,
            solo: false,
            wait_since: None,
            capture_on: None,
            capture_since: 0,
            healing: false,
            precompute,
            gems: 0,
            stuck: 0,
            prof: [0; 10],
            was_dead: false,
            deaths_seen: Vec::new(),
            alive_flags: Vec::new(),
            death_pos: None,
            call_field: None,
            enemy_seen_at: Vec::new(),
            last_seen: [None; 6],
            last_hp: 0.0,
            hit_round: 0,
            taken: 0.0,
            trail: std::collections::VecDeque::new(),
            team_center: None,
            plan_origin: start,
            none_since: None,
            last_shop_trip: 0,
            flee_best: u16::MAX,
            flee_stall: 0,
            hold_turns: 0,
            standoff: 0,
            waiting: false,
            round: 0,
            pos: start,
            hp: 0.0,
            max_hp: 1.0,
            moved: false,
            attacked: false,
            cast: false,
            occupied: Bitboard::new()?,
            enemies: Vec::new(),
            allies: Vec::new(),
            comm: Comm::default(),
            guard_sequence: 0,
            guard_seen: None,
        })
    }

    pub fn turn(&mut self) -> Result<()> {
        let me = me();
        self.round = cambc::round_number()?;
        self.comm = Comm::read()?;
        // Track teammates' deaths (alive -> dead transitions).
        let alive: Vec<bool> = self.team.iter().map(|c| c.is_alive().unwrap_or(true)).collect();
        if self.alive_flags.len() == alive.len() {
            for (was, now) in self.alive_flags.iter().zip(&alive) {
                if *was && !*now {
                    self.deaths_seen.push(self.round);
                }
            }
        }
        self.alive_count = alive.iter().filter(|a| **a).count().max(1);
        self.alive_flags = alive;
        if !me.is_alive()? {
            if !self.was_dead {
                self.was_dead = true;
                log!(self, "dead with {} gems; last turns: {}", self.gems, self.trail.iter().cloned().collect::<Vec<_>>().join(" | "));
                self.death_pos = Some((self.pos, self.round));
            }
            shop::shop(me, self.kind).ok();
            self.job = None;
            self.solo = false;
            self.comm.set_claim(self.slot, None)?;
            self.capture_on = None;
            self.healing = false;
            self.prof[0] += 1;
            self.report();
            return Ok(());
        }
        self.was_dead = false;
        let state = me.state()?;
        if state.intersects(ChampionState::RECALLING | ChampionState::SUBMITTING_GEMS | ChampionState::TELEPORTING) {
            self.prof[if state.contains(ChampionState::SUBMITTING_GEMS) { 2 } else { 1 }] += 1;
            self.report();
            if state.contains(ChampionState::RECALLING) {
                self.comm.set_claim(self.slot, Some(self.kb.spawn_field()))?;
            }
            if state.contains(ChampionState::SUBMITTING_GEMS) {
                self.pos = me.position()?;
                self.sense()?;
                self.guard_tribute()?;
            }
            self.idle_precompute();
            return Ok(());
        }
        self.pos = me.position()?;
        self.hp = me.health()?;
        self.max_hp = me.max_health()?;
        self.moved = !state.contains(ChampionState::CAN_MOVE);
        self.attacked = !state.contains(ChampionState::CAN_ATTACK);
        self.cast = false;
        self.waiting = false;
        self.gems = me.gem_count()?;
        if self.gems == 0 && self.comm.claim_of(self.slot).map_or(false, |g| g >= self.kb.groups.len() && g < self.kb.spawn_field()) {
            self.comm.set_claim(self.slot, None)?;
        }
        self.taken = (self.last_hp - self.hp).max(0.0);
        if self.taken > 0.5 {
            self.hit_round = self.round;
        }
        self.last_hp = self.hp;
        self.sense()?;
        self.gate_now = self.gate();
        self.guard_update()?;

        let at_spawn = self.kb.spawn.is_set(self.pos)?;
        if at_spawn || self.kind == ChampionType::Tavi {
            shop::shop(me, self.kind).ok();
            self.hp = me.health()?;
            self.max_hp = me.max_health()?;
        }

        self.maybe_shop_trip(at_spawn)?;
        let mut mode = "heal";
        if self.heal(at_spawn)? {
            self.comm.set_claim(self.slot, Some(self.kb.spawn_field()))?;
        } else if self.guard_regroup()? {
            mode = "regroup";
        } else if self.fight_enemies()? {
            mode = "fight";
        } else if self.should_bank()? {
            mode = "bank";
            self.bank()?;
        } else {
            mode = "farm";
            self.farm()?;
        }
        self.support_spells();
        if mode == "fight" {
            if self.attacked || self.cast || self.taken > 0.5 {
                self.standoff = 0;
            } else {
                self.standoff += 1;
            }
        }
        let slot = match mode {
            "heal" => 3,
            "fight" => 4,
            "bank" => 5,
            _ if self.capture_on.is_some() => 6,
            _ if self.attacked || self.cast => 7,
            _ if self.moved => 8,
            _ => 9,
        };
        self.prof[slot] += 1;
        self.report();
        if crate::util::DEBUG {
            let en: Vec<String> = self.enemies.iter().map(|e| format!("{:?}{}hp{:.0}", e.ch.champion_name().ok(), cheb(e.pos, self.pos), e.hp)).collect();
            self.trail.push_back(format!("r{} {} @{},{} hp{:.0} took{:.0} al{} en[{}] job{:?} mv{} at{} fuel{}", self.round, mode, self.pos.x, self.pos.y, self.hp, self.taken, self.allies.len(), en.join(","), self.job, self.moved, self.attacked, cambc::fuel_remaining().unwrap_or(0)));
            if self.trail.len() > 6 {
                self.trail.pop_front();
            }
        }
        // Unstick: nothing happened while travelling.
        let busy = self.moved || self.attacked || self.cast || self.capture_on.is_some() || self.waiting;
        if !busy && (mode == "farm" || mode == "bank") {
            self.stuck += 1;
        } else {
            self.stuck = 0;
        }
        if self.stuck >= 6 {
            self.stuck = 0;
            log!(self, "stuck trail job {:?} fuel {}: {}", self.job, cambc::fuel_remaining().unwrap_or(0), self.trail.iter().cloned().collect::<Vec<_>>().join(" | "));
            if mode == "bank" {
                if let Some((a, _)) = self.nearest_altar()? {
                    log!(self, "stuck: skip altar {}", a);
                    self.altar_block[a] = self.round + 40;
                }
            } else if let Some(g) = self.job {
                // Crowded at the target is fine; stuck far away means no route.
                if self.kb.dist(g, self.pos)? > 6 {
                    log!(self, "stuck: skip g{}", g);
                    self.group_block[g] = self.round + 30;
                    self.job = None;
                    self.solo = false;
                    self.comm.set_claim(self.slot, None)?;
                }
            }
        }
        if crate::util::DEBUG && self.round % 10 == 0 {
            let jd = self.job.map(|g| self.kb.dist_or_estimate(g, self.pos, self.kb.groups[g].center).unwrap_or(0));
            let st = self.job.map(|g| format!("{:?}", self.kb.groups[g].cg.state().ok()));
            log!(self, "tick {} job {:?} dist {:?} state {:?} gems {} cap {:?}", mode, self.job, jd, st, self.gems, self.capture_on);
        }
        if self.round % 50 == 0 {
            log!(self, "status {} hp {:.0}/{:.0} gems {} job {:?} cap {:?} fuel {}", mode, self.hp, self.max_hp,
                self.gems, self.job, self.capture_on, cambc::fuel_remaining().unwrap_or(0));
            log!(self, "guard active {} leader {:?} goal {:?}", self.guard_active(), self.comm.support_leader(), self.guard_goal());
        }
        self.idle_precompute();
        Ok(())
    }

    /// Unspent gold is wasted strength: go home to spend it when it is a
    /// good moment (nothing around, not carrying much, not capturing).
    fn maybe_shop_trip(&mut self, at_spawn: bool) -> Result<()> {
        if self.healing || at_spawn || self.kind == ChampionType::Tavi || self.capture_on.is_some() {
            return Ok(());
        }
        if !self.enemies.is_empty() || self.gems >= 25 || self.round < self.last_shop_trip + 40 {
            return Ok(());
        }
        let gold = me().gold_count()?;
        let home = self.kb.dist(self.kb.spawn_field(), self.pos)? as u32;
        if home == crate::kb::NO_DIST as u32 || home < 6 {
            return Ok(());
        }
        let left = cambc::constants().max_rounds.saturating_sub(self.round);
        if gold >= (150).max(home * 6) && left > 300 && shop::has_next(me(), self.kind)? {
            log!(self, "shop trip with {} gold", gold);
            self.last_shop_trip = self.round;
            self.healing = true;
        }
        Ok(())
    }

    fn report(&self) {
        if self.round % 250 == 0 {
            log!(self, "prof dead {} recall {} tribute {} heal {} pvp {} bank {} capture {} hit {} walk {} idle {}",
                self.prof[0], self.prof[1], self.prof[2], self.prof[3], self.prof[4], self.prof[5],
                self.prof[6], self.prof[7], self.prof[8], self.prof[9]);
        }
    }

    /// Enemies last seen (off their spawn) near `p` recently enough to still
    /// be around: they walk about a tile a round.
    pub fn enemies_near(&self, p: Vec2, radius: i32, window: u32) -> usize {
        self.last_seen
            .iter()
            .flatten()
            .filter(|(q, r)| *r + window > self.round && cheb(*q, p) <= radius + ((self.round - *r) / 3) as i32)
            .count()
    }

    /// Carrying gems is risky right now: an enemy champion was seen near us in
    /// the last 40 rounds, a teammate died in the last 100, or we are hurt.
    pub fn threatened(&self) -> bool {
        let r = self.round;
        self.frac() < 0.6
            || self.enemy_seen_at.iter().any(|(p, t)| *t + 40 > r && cheb(*p, self.pos) <= 14)
            || self.deaths_seen.iter().any(|&t| t + 100 > r)
    }

    /// Team deaths in the last 150 rounds.
    pub fn recent_deaths(&mut self) -> usize {
        let cutoff = self.round.saturating_sub(150);
        self.deaths_seen.retain(|&r| r >= cutoff);
        self.deaths_seen.len()
    }

    // ---------------------------------------------------------------- sensing

    pub fn sense(&mut self) -> Result<()> {
        let mut occ = cambc::vision::champion_tiles(None)?;
        occ.union_assign(&cambc::vision::camp_tiles()?)?;
        occ.union_assign(&cambc::vision::teleport_tiles()?)?;
        occ.set(self.pos, false)?;
        self.occupied = occ;
        self.enemies.clear();
        for p in cambc::vision::champion_tiles(Some(Team::Enemy))?.positions()? {
            if let Ok(ch) = cambc::vision::champion_at(p) {
                let hp = ch.health().unwrap_or(0.0);
                if hp <= 0.0 {
                    continue;
                }
                let idx = self.enemy_team.iter().position(|c| *c == ch).unwrap_or(99);
                self.enemies.push(Enemy {
                    idx,
                    max_hp: ch.max_health().unwrap_or(1000.0),
                    gems: ch.gem_count().unwrap_or(0),
                    range: ch.attack_range().unwrap_or(1),
                    dps: champion_dps(&ch),
                    on_spawn: self.kb.enemy_spawn.is_set(p).unwrap_or(false),
                    ch,
                    pos: p,
                    hp,
                });
            }
        }
        if !self.enemies.is_empty() {
            let r = self.round;
            let ps: Vec<Vec2> = self.enemies.iter().map(|e| e.pos).collect();
            self.enemy_seen_at.retain(|(_, t)| *t + 60 > r);
            for p in ps {
                self.enemy_seen_at.push((p, r));
            }
            if self.enemy_seen_at.len() > 40 {
                self.enemy_seen_at.drain(0..10);
            }
            for e in &self.enemies {
                if e.idx < 6 && !e.on_spawn {
                    self.last_seen[e.idx] = Some((e.pos, r));
                }
            }
        }
        self.allies.clear();
        for p in cambc::vision::champion_tiles(Some(Team::Ally))?.positions()? {
            if p == self.pos {
                continue;
            }
            if let Ok(ch) = cambc::vision::champion_at(p) {
                self.allies.push(Ally {
                    hp: ch.health().unwrap_or(0.0),
                    max_hp: ch.max_health().unwrap_or(1000.0),
                    melee: ch.attack_range().unwrap_or(1) <= 1,
                    dps: champion_dps(&ch),
                    kind: ch.champion_name().unwrap_or(ChampionType::Ryth),
                    ch,
                    pos: p,
                });
            }
        }
        Ok(())
    }

    pub fn reset_camp_hp(&mut self, g: usize) {
        for (i, c) in self.kb.groups[g].camps.iter().enumerate() {
            self.camp_hp[g][i] = camp_design(c.1).hp;
        }
    }

    pub fn visible(&self, p: Vec2) -> bool {
        cambc::vision::in_vision(p).unwrap_or(false)
    }

    pub fn group_hp(&self, g: usize) -> f32 {
        self.camp_hp[g].iter().sum()
    }

    pub fn frac(&self) -> f32 {
        self.hp / self.max_hp.max(1.0)
    }

    pub fn my_dps(&self) -> f32 {
        champion_dps(me())
    }

    /// Awake damaging camps: position, range, damage. When something unseen
    /// hit us lately (camps in bushes), every live dangerous camp in reach
    /// counts as awake.
    pub fn camp_threats(&self) -> Vec<(Vec2, i32, f32)> {
        let mut out = Vec::new();
        if self.hit_round + 2 >= self.round && self.round > 0 {
            for (g, grp) in self.kb.groups.iter().enumerate() {
                if cheb(grp.center, self.pos) > 12 {
                    continue;
                }
                for (i, &(p, k)) in grp.camps.iter().enumerate() {
                    let d = camp_design(k);
                    if d.dmg > 0.0 && self.camp_hp[g][i] > 0.0 && cheb(p, self.pos) <= d.range + 1 && !self.visible(p) {
                        out.push((p, d.range, d.dmg));
                    }
                }
            }
        }
        if let Ok(tiles) = cambc::vision::awake_camp_tiles() {
            if let Ok(ps) = tiles.positions() {
                for cp in ps {
                    if let Ok(c) = cambc::vision::camp_at(cp) {
                        let d = camp_design(c.kind());
                        if d.dmg > 0.0 {
                            out.push((cp, d.range, d.dmg));
                        }
                    }
                }
            }
        }
        out
    }

    pub fn idle_precompute(&mut self) {
        let cost = self.kb.field_cost();
        while let Some(&key) = self.precompute.last() {
            if crate::util::fuel() < cost + 15_000 {
                break;
            }
            self.precompute.pop();
            if self.kb.ensure_field(key).is_err() {
                break;
            }
        }
    }
}
