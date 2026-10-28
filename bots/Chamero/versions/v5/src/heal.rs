// Retreating and recovering HP at spawn.
use crate::bot::Bot;
use crate::log;
use crate::util::{cheb, me};
use cambc::Result;

impl Bot {
    /// Returns true if this turn was spent retreating or healing.
    pub fn heal(&mut self, at_spawn: bool) -> Result<bool> {
        let frac = self.frac();
        if at_spawn {
            if self.healing && frac >= 0.97 {
                self.healing = false;
            }
            if frac < 0.9 || self.healing {
                // Spawn heals at turn end; hit anything that comes in reach meanwhile.
                if let Some(e) = self.enemies.iter().filter(|e| cheb(e.pos, self.pos) <= self.range).min_by(|a, b| a.hp.partial_cmp(&b.hp).unwrap()).cloned() {
                    self.cast_offensive_on_champion(&e)?;
                    self.basic_attack(&e.ch, e.pos)?;
                }
                return Ok(true);
            }
            return Ok(false);
        }
        let threats = self.camp_threats();
        let mut incoming = 0.0f32;
        let mut escape = 0;
        for t in &threats {
            let d = cheb(t.0, self.pos);
            if d <= t.1 {
                incoming += t.2;
                // Out of reach, or behind the nearest ally: camps hit the
                // nearest champion, so it takes over once we are further.
                let shield = self.allies.iter().map(|a| cheb(a.pos, t.0)).min().unwrap_or(99) + 1;
                escape = escape.max(((t.1 + 1).min(shield) - d).max(0));
            }
        }
        let enemy_near = self.enemies.iter().any(|e| !e.on_spawn && cheb(e.pos, self.pos) <= e.range + 2)
            || (self.taken > 0.5 && threats.is_empty());
        let careful = self.recent_deaths() >= 3;
        // Enemy champions that could have hit us: the fight logic owns those
        // decisions (it knows whether teammates are holding the line).
        let enemy_reach = self.enemies.iter().any(|e| !e.on_spawn && cheb(e.pos, self.pos) <= e.range + 1);
        if !self.healing {
            // Leave a camp while we can still walk out of range: every step out
            // costs a hit. Only the camp's current target takes hits.
            let targeted = self.taken > 0.5 && !enemy_reach;
            // Armour cuts camp hits; what we just took is the better guess.
            let per_turn = if targeted { incoming.min(self.taken * 1.2) } else { 0.0 };
            let low = frac < 0.15
                || (!enemy_reach && frac < 0.2)
                || self.hp < per_turn * (escape as f32 + 1.0) + 40.0
                || (!enemy_near && frac < if careful { 0.45 } else { 0.3 } && self.capture_on.is_none());
            if !low {
                return Ok(false);
            }
            log!(self, "retreat hp {:.0}/{:.0} incoming {} gems {}", self.hp, self.max_hp, incoming, self.gems);
            self.healing = true;
            self.capture_on = None;
            self.flee_best = u16::MAX;
            self.flee_stall = 0;
        }
        self.use_shield();
        if enemy_near || incoming > 0.0 {
            // Fleeing can circle when enemies sit on the way home; if it makes
            // no progress and nothing is hitting us, gamble on a recall.
            let home = self.kb.dist(self.kb.spawn_field(), self.pos)?;
            if home < self.flee_best {
                self.flee_best = home;
                self.flee_stall = 0;
            } else {
                self.flee_stall += 1;
            }
            if self.flee_stall >= 3 && self.taken <= 0.5 && incoming <= 0.0 && home > 2 {
                if me().recall().is_ok() {
                    log!(self, "recall (flee stalled)");
                    self.flee_stall = 0;
                    return Ok(true);
                }
            }
            let moved = self.flee(&threats)?;
            if !moved && self.taken > 0.0 {
                log!(self, "flee failed: moved {} threats {:?} occ {:?}", self.moved, threats, crate::util::DIRS.iter().map(|d| self.free(self.pos + *d)).collect::<Vec<_>>());
            }
            return Ok(true);
        }
        // Bank on the way if an altar is right here.
        if self.gems > 0 {
            if let Some((a, d)) = self.nearest_altar()? {
                if d <= 3 {
                    let altar = self.kb.altars[a];
                    if cheb(self.pos, altar) <= 1 {
                        me().submit_gems(altar).ok();
                    } else {
                        self.step_field(self.kb.altar_field(a))?;
                    }
                    return Ok(true);
                }
            }
        }
        let spawn_key = self.kb.spawn_field();
        let d = self.kb.dist(spawn_key, self.pos)?;
        // Out of every known threat's reach (camps do not chase): recall
        // here rather than walk home past them.
        if self.hit_round + 1 >= self.round && threats.is_empty() {
            // Hit by something unknown: get further away before recalling.
            self.step_home_safe(&threats)?;
        } else if d > 6 {
            if me().recall().is_ok() {
                log!(self, "recall");
            }
        } else {
            self.step_home_safe(&threats)?;
        }
        Ok(true)
    }

    /// Step toward spawn, never into a known threat's reach.
    fn step_home_safe(&mut self, threats: &[(cambc::Vec2, i32, f32)]) -> Result<bool> {
        let key = self.kb.spawn_field();
        self.kb.ensure_field(key)?;
        let field = self.kb.fields[key].take().unwrap();
        let cur = self.kb.lookup(&field, self.pos)?;
        let threats = threats.to_vec();
        let r = self.step_by(|s, p| {
            let home = s.kb.lookup(&field, p).unwrap_or(crate::kb::NO_DIST);
            let exposed = threats.iter().any(|t| cheb(t.0, p) <= t.1);
            if home >= cur && p != s.pos {
                return f32::MAX;
            }
            home as f32 + if exposed { 1000.0 } else { 0.0 }
        });
        self.kb.fields[key] = Some(field);
        r
    }
}
