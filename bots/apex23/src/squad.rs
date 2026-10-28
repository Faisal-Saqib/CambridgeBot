// Local melee/ranged partnerships. No team-wide staging or waiting timer.
use crate::bot::Bot;
use crate::util::cheb;
use cambc::{Champion, ChampionState, ChampionType as C, Result};

pub fn formation(team: &[Champion], slot: usize) -> (usize, Vec<usize>) {
    // Champion identity is readable without vision; positions are not.
    let kinds: Vec<_> = team.iter().map(|c| c.champion_name().ok()).collect();
    let find = |kind| kinds.iter().position(|k| *k == Some(kind));
    let mut leaders: Vec<_> = (0..team.len()).collect();
    if let Some(ryth) = find(C::Ryth) {
        for kind in [C::VesperVale, C::Willow] {
            if let Some(i) = find(kind) {
                leaders[i] = ryth;
            }
        }
        if team.len() <= 3 {
            if let Some(i) = find(C::Marcella) {
                leaders[i] = ryth;
            }
        }
    }
    if let (Some(marcella), Some(tavi)) = (find(C::Marcella), find(C::Tavi)) {
        leaders[tavi] = marcella;
    }
    let anchor = leaders.get(slot).copied().unwrap_or(slot);
    let partners = (0..team.len())
        .filter(|&i| i != slot && leaders[i] == anchor)
        .collect();
    (anchor, partners)
}

impl Bot {
    /// Take at most one ordinary step toward a visible anchor. Never wait for
    /// an unseen/dead partner or interrupt a carrier/capture/channel.
    pub fn regroup_partner(&mut self) -> Result<bool> {
        if self.anchor_slot == self.slot || self.moved || self.gems > 0
            || self.capture_on.is_some() || self.healing
            || self.enemies.iter().any(|e| cheb(e.pos, self.pos) <= e.range + 1)
        {
            return Ok(false);
        }
        let Some(anchor) = self.team.get(self.anchor_slot) else { return Ok(false) };
        let Some(ally) = self.allies.iter().find(|a| &a.ch == anchor) else { return Ok(false) };
        if ally.hp <= ally.max_hp * 0.35 || cheb(ally.pos, self.pos) <= 3 {
            return Ok(false);
        }
        let available = ally.ch.state().map(|s| !s.intersects(
            ChampionState::RECALLING | ChampionState::SUBMITTING_GEMS | ChampionState::TELEPORTING
        )).unwrap_or(false);
        if !available {
            return Ok(false);
        }
        let target = ally.pos;
        // Visible, nearby target: a cheap step avoids an expensive field for
        // a target that moves each turn. No progress falls back to normal play.
        self.step_by(|_, p| cheb(p, target) as f32)
    }

    /// Adopt the anchor's live claim for dangerous groups or local pressure.
    /// Preserve the existing affordability, respawn, reachability and cap checks.
    pub fn partner_job(&mut self) -> Result<Option<usize>> {
        if self.anchor_slot == self.slot
            || !self.alive_flags.get(self.anchor_slot).copied().unwrap_or(false)
        {
            return Ok(None);
        }
        let Some(g) = self.comm.claim_of(self.anchor_slot) else { return Ok(None) };
        let Some(group) = self.kb.groups.get(g) else { return Ok(None) };
        if group.danger_dps <= 0.0 && !self.kb.brawl_map && !self.threatened() {
            return Ok(None);
        }
        Ok(self.job_score(g)?.map(|_| g))
    }

    /// Sharing a nearby multi-tile reward keeps partners' hauls small. Do not
    /// wait on a full one-tile region or require a partner outside vision.
    pub fn share_partner_capture(&self, g: usize) -> bool {
        let Some(group) = self.kb.groups.get(g) else { return false };
        if group.camps.len() < 2
            || (group.danger_dps <= 0.0 && !self.kb.brawl_map && !self.threatened())
        {
            return false;
        }
        self.partner_slots.iter().any(|&slot| {
            self.team.get(slot).map_or(false, |partner| self.allies.iter().any(|a| {
                &a.ch == partner && a.hp > 0.0 && cheb(a.pos, self.pos) <= 6
                    && group.tiles.is_set(a.pos).unwrap_or(false)
            }))
        })
    }
}
