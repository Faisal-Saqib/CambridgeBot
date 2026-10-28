// Altars reachable only by killing the camp beside them (a Monolith on
// boss-battle and guardians). Banking alone there means breaching alone and
// dying, so the team hoards gems, gathers, kills that one camp together and
// then banks as usual.
use crate::bot::Bot;
use crate::comm::{GATE_ASSAULT, GATE_OPEN};
use crate::log;
use crate::util::cheb;
use cambc::Vec2;

impl Bot {
    /// The gate camp (group, index, position) while every altar is shut.
    pub fn gate(&mut self) -> Option<(usize, usize, Vec2)> {
        if self.kb.gates.is_empty() || self.kb.gates.iter().any(|g| g.is_none()) {
            return None;
        }
        let mut flags = self.comm.gate_flags();
        let mut best: Option<(i32, (usize, usize, Vec2))> = None;
        for a in 0..self.kb.gates.len() {
            let (g, i) = self.kb.gates[a].unwrap();
            let p = self.kb.groups[g].camps[i].0;
            if self.visible(p) {
                let dead = self.kb.groups[g].cg.camps()[i].state().map(|s| s.is_dead()).unwrap_or(false);
                if dead && flags & GATE_OPEN == 0 {
                    log!(self, "gate g{} at {},{} is down", g, p.x, p.y);
                    flags = GATE_OPEN;
                } else if !dead && flags & GATE_OPEN != 0 {
                    flags = 0;
                }
            }
            let d = cheb(p, self.kb.spawn_center);
            if best.map_or(true, |b| d < b.0) {
                best = Some((d, (g, i, p)));
            }
        }
        // Start the assault once there is something worth banking.
        if flags == 0 && (self.round >= 200 || self.gems >= 60) {
            log!(self, "gate assault on");
            flags = GATE_ASSAULT;
        }
        self.comm.set_gate_flags(flags).ok();
        if flags & GATE_OPEN != 0 {
            return None;
        }
        best.map(|b| b.1)
    }

    pub fn gate_assault(&self) -> bool {
        self.comm.gate_flags() & GATE_ASSAULT != 0
    }
}
