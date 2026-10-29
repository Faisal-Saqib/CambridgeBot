// Altars reachable only by killing the camp beside them (a Monolith on
// boss-battle and guardians). Banking alone there means breaching alone and
// dying, so the team hoards gems, gathers, kills that one camp together and
// then banks as usual.
use crate::bot::Bot;
use crate::comm::{GATE_ASSAULT, GATE_OPEN};
use crate::log;
use crate::util::cheb;
use cambc::Vec2;

/// Round after which we attack the gate ourselves if nobody has opened it.
const GATE_ASSAULT_ROUND: u32 = 500;

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
        // Chamero: wait much longer (was round 200 or 60 gems). Against top
        // teams our early assaults fed the monolith 4-9 camp deaths a game and
        // lost the carried gems; they wait, kill it late (rounds 470-720) and
        // tribute 200-865 at once. The gate ward shows us when it falls.
        if flags == 0 && self.round >= GATE_ASSAULT_ROUND {
            log!(self, "gate assault on");
            flags = GATE_ASSAULT;
        }
        self.comm.set_gate_flags(flags).ok();
        if flags & GATE_OPEN != 0 {
            return None;
        }
        best.map(|b| b.1)
    }

    /// Chamero: keep a ward on the gate camp. Vision is not shared and a
    /// group's state needs vision, so the team never noticed when the enemy
    /// killed the gate (top teams do, then tribute 150-290 gems at once) and
    /// held its gems all game: 0 points on Boss Battle in every top-5 game.
    /// Wards are permanent and camps ignore them, so a champion passing within
    /// 8 tiles drops its ward on the reachable tile nearest the gate; from then
    /// on `gate()` sees the gate die and opens the altar for the whole team.
    pub fn ward_gate(&mut self, gp: Vec2) {
        let me = crate::util::me();
        if cheb(self.pos, gp) > 8 || me.ward_cooldown().unwrap_or(1) > 0 {
            return;
        }
        let watched = me.ward_positions().map_or(false, |ws| ws.iter().any(|w| cheb(*w, gp) <= 5));
        if watched {
            return;
        }
        let Ok(tiles) = me.ward_placement_tiles() else { return };
        let Ok(cands) = tiles.positions() else { return };
        let best = cands
            .into_iter()
            .filter(|p| !self.kb.is_blocked(*p) && !self.occupied.is_set(*p).unwrap_or(true))
            .min_by_key(|p| cheb(*p, gp));
        if let Some(p) = best {
            if cheb(p, gp) <= 5 && me.place_ward(p).unwrap_or(false) {
                log!(self, "ward on gate at {},{} from {},{}", gp.x, gp.y, p.x, p.y);
            }
        }
    }

    pub fn gate_assault(&self) -> bool {
        self.comm.gate_flags() & GATE_ASSAULT != 0
    }
}
