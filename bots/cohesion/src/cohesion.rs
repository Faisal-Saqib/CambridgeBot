use crate::bot::Bot;
use crate::formation_protocol::{self as protocol, Packet, BANK, HOME, TRAVEL};
use crate::util::{cheb, me};
use cambc::{Champion, ChampionState, ChampionType as C, Result, Vec2};

pub fn priority(team: &[Champion]) -> Vec<usize> {
    let mut order: Vec<_> = (0..team.len()).collect();
    order.sort_by_key(|&s| (match team[s].champion_name().ok() {
        Some(C::Ryth) => 0, Some(C::Marcella) => 1, Some(C::HeartOfRuin) => 2,
        Some(C::Ren) | Some(C::Varg) | Some(C::Issac) => 3, _ => 4,
    }, s));
    order
}
impl Bot {
    pub fn rally(&self) -> Option<Packet> {
        let p = self.comm.packet(); p.fresh(self.round, &self.alive_flags).then_some(p)
    }
    pub fn cohesion_leader(&self) -> bool { self.cohesion_anchor == self.slot }
    pub fn cohesion_start(&mut self, state: ChampionState) -> Result<()> {
        let p = self.comm.packet();
        self.cohesion_anchor = protocol::elect(p, &self.alive_flags, &self.cohesion_order, self.round)
            .unwrap_or(self.slot);
        if self.cohesion_leader() {
            let mode = if self.healing || state.contains(ChampionState::RECALLING) { HOME }
                else if state.contains(ChampionState::SUBMITTING_GEMS)
                    || (p.leader == Some(self.slot) && p.mode == BANK && self.gems > 0) { BANK }
                else { TRAVEL };
            self.comm.publish(self.slot, self.pos, self.round, mode)?;
        }
        Ok(())
    }
    pub fn cohesion_home(&mut self) -> Result<()> {
        if self.rally().map_or(false, |p| p.mode == HOME && p.leader != Some(self.slot)) { return Ok(()); }
        self.cohesion_anchor = self.slot;
        self.comm.publish(self.slot, self.pos, self.round, HOME)?;
        self.comm.set_goal(Some(self.kb.spawn_field()))
    }
    pub fn cohesion_plan(&mut self, at_spawn: bool) -> Result<()> {
        self.cohesion_peers = self.allies.iter().filter(|a| {
            a.hp >= a.max_hp * 0.4 && cheb(a.pos, self.pos) <= 6
                && a.ch.state().map(|s| !s.intersects(ChampionState::RECALLING | ChampionState::TELEPORTING)).unwrap_or(false)
        }).map(|a| a.pos).collect();
        self.cohesion_dps = self.my_dps() + self.allies.iter()
            .filter(|a| self.cohesion_peers.contains(&a.pos))
            .map(|a| a.dps).sum::<f32>();
        if self.rally().map_or(false, |p| p.mode == HOME && p.leader != Some(self.slot)) && !at_spawn {
            self.healing = true;
        }
        if self.healing { self.cohesion_home()?; return Ok(()); }
        if self.gems > 0 && self.should_bank()? {
            let can_lead = self.rally().map_or(true, |p| p.mode == TRAVEL || (p.mode == BANK && p.leader == Some(self.slot)));
            if can_lead {
                if let Some((a, _)) = self.nearest_altar()?.or(self.nearest_breach_altar()?) {
                    self.cohesion_anchor = self.slot;
                    self.comm.publish(self.slot, self.pos, self.round, BANK)?;
                    self.comm.set_goal(Some(self.kb.altar_field(a)))?;
                }
            }
        }
        Ok(())
    }
    pub fn cohesion_altar(&self) -> Option<usize> {
        let p = self.rally()?;
        if p.mode != BANK { return None; }
        let g = p.goal?;
        (0..self.kb.altars.len()).find(|&a| self.kb.altar_field(a) == g)
    }
    pub fn cohesion_job(&self) -> Option<usize> {
        let p = self.rally()?;
        if p.mode != TRAVEL { return None; }
        p.goal.filter(|g| *g < self.kb.groups.len())
    }
    pub fn cohesion_move_allowed(&self, next: Vec2) -> bool {
        if self.healing || self.frac() < 0.35 || self.taken > 0.5 { return true; }
        let here = (self.pos.x,self.pos.y); let next = (next.x,next.y);
        let Some(p) = self.rally() else { return true; };
        if self.gems == 0 && p.mode == BANK {
            if let Some(a) = self.cohesion_altar() {
                let altar = self.kb.altars[a];
                if !protocol::escort_tile_clear(next,(altar.x,altar.y)) { return false; }
            }
        }
        let radius = if self.stuck >= 3 { 4 } else { 3 };
        if p.leader == Some(self.slot) {
            self.cohesion_peers.iter().all(|a| protocol::permits_step_with_radius(here,next,(a.x,a.y),radius))
        } else { protocol::permits_step_with_radius(here,next,p.pos,radius) }
    }
    pub fn cohesion_regroup(&mut self, at_spawn: bool) -> Result<bool> {
        if self.healing || self.frac() < 0.35 { return Ok(false); }
        let Some(p) = self.rally() else { return Ok(false); };
        if p.leader == Some(self.slot) { return Ok(false); }
        if p.mode == HOME && at_spawn { return Ok(true); }
        if self.gems == 0 && p.mode == BANK {
            if let Some(a) = self.cohesion_altar() {
                let altar = self.kb.altars[a];
                if !protocol::escort_tile_clear((self.pos.x,self.pos.y),(altar.x,altar.y)) {
                    self.step_by(|_, q| if protocol::escort_tile_clear((q.x,q.y),(altar.x,altar.y)) { 0.0 } else { 1.0 })?;
                    // A melee escort can still fight after stepping aside.
                    return Ok(false);
                }
            }
        }
        let target = Vec2::new(p.pos.0,p.pos.1);
        if !protocol::needs_regroup((self.pos.x,self.pos.y),p.pos) { return Ok(false); }
        // Preserve ready attacks and the existing combat retreat decision under direct threat.
        if self.enemies.iter().any(|e| !e.on_spawn && cheb(e.pos,self.pos) <= e.range.max(self.range) + 1) {
            return Ok(false);
        }
        self.capture_on = None;
        let stepped = self.step_by(|_, q| cheb(q,target) as f32)?;
        if !stepped { self.step_to(target)?; }
        Ok(true)
    }
    pub fn cohesion_finish(&mut self) -> Result<()> {
        if self.healing { self.cohesion_home()?; }
        if self.comm.packet().leader == Some(self.slot) {
            let mode = if self.healing { HOME }
                else if self.comm.packet().mode == BANK && me().gem_count().unwrap_or(self.gems) > 0 { BANK }
                else { TRAVEL };
            self.comm.publish(self.slot,self.pos,self.round,mode)?;
        }
        Ok(())
    }
}
