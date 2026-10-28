// Movement: static-field descent, local scoring, dashes and fleeing.
use crate::bot::Bot;
use crate::kb::{Field, NO_DIST};
use crate::util::{cheb, me, DIRS};
use cambc::{AbilityInfo, Bitboard, DistanceField, Result, Vec2};

impl Bot {
    pub fn free(&self, p: Vec2) -> bool {
        !self.kb.is_blocked(p) && !self.occupied.is_set(p).unwrap_or(true)
    }

    /// Move to the free neighbour with the lowest score if it beats staying.
    pub fn step_by(&mut self, mut score: impl FnMut(&Self, Vec2) -> f32) -> Result<bool> {
        if self.moved {
            return Ok(false);
        }
        let here = score(self, self.pos);
        let mut cands: Vec<(f32, Vec2)> = Vec::with_capacity(8);
        for d in DIRS {
            let p = self.pos + d;
            if self.free(p) {
                let s = score(self, p);
                if s < here {
                    cands.push((s, p));
                }
            }
        }
        cands.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        for (_, p) in cands {
            match me().move_absolute(p) {
                Ok(true) => {
                    self.pos = p;
                    self.moved = true;
                    return Ok(true);
                }
                _ => {
                    self.occupied.set(p, true)?;
                }
            }
        }
        Ok(false)
    }

    fn step_on(&mut self, field: &Field, allow_dash: bool) -> Result<bool> {
        let cur = self.kb.lookup(field, self.pos)?;
        if cur == 0 || cur == NO_DIST {
            return Ok(false);
        }
        if allow_dash {
            self.try_dash(field)?;
        }
        let cur = self.kb.lookup(field, self.pos)?;
        let mut vals = [NO_DIST; 8];
        for (i, d) in DIRS.iter().enumerate() {
            let p = self.pos + *d;
            if self.kb.in_bounds(p) {
                vals[i] = field.get(p)?;
            }
        }
        // Prefer staying near the straight line, then equal-distance sidesteps.
        self.step_by(|s, p| {
            if p == s.pos {
                return cur as f32;
            }
            let Some(i) = DIRS.iter().position(|x| *x == p - s.pos) else { return f32::MAX };
            if vals[i] == NO_DIST {
                f32::MAX
            } else if vals[i] < cur {
                vals[i] as f32
            } else if vals[i] == cur {
                cur as f32 - 0.1
            } else {
                f32::MAX
            }
        })
    }

    /// One step down a static field (camp group, altar or spawn).
    pub fn step_field(&mut self, key: usize) -> Result<bool> {
        self.kb.ensure_field(key)?;
        let field = self.kb.fields[key].take().unwrap();
        let r = self.step_on(&field, true);
        self.kb.fields[key] = Some(field);
        r
    }

    /// Walk toward an arbitrary tile using a cached terrain field rooted there.
    pub fn step_to(&mut self, target: Vec2) -> Result<bool> {
        if cheb(target, self.pos) <= 1 || self.moved {
            return Ok(false);
        }
        let fresh = matches!(&self.call_field, Some((p, _)) if *p == target);
        if !fresh {
            if crate::util::fuel() < self.kb.field_cost() + 10_000 {
                // Not enough fuel for a search: greedy step.
                return self.step_by(|_, p| cheb(p, target) as f32);
            }
            let mut roots = Bitboard::new()?;
            roots.set(target, true)?;
            let mut walls = self.kb.blocked.clone();
            walls.set(target, false)?;
            let mut f = DistanceField::new()?;
            let mut vis = Bitboard::new()?;
            f.compute(&walls, &roots, &mut vis, NO_DIST)?;
            self.call_field = Some((target, Field::from_df(&f)?));
        }
        let (p, f) = self.call_field.take().unwrap();
        let r = self.step_on(&f, false);
        self.call_field = Some((p, f));
        r
    }

    /// Dash two tiles along a field when travelling far.
    fn try_dash(&mut self, field: &Field) -> Result<()> {
        // Keep the dash for fights while enemies are about.
        if self.cast || self.moved || !self.enemies.is_empty() {
            return Ok(());
        }
        let cur = field.get(self.pos)?;
        if cur < 6 || cur == NO_DIST {
            return Ok(());
        }
        for ab in me().abilities() {
            if let Ok(Some(AbilityInfo::Dash(_))) = ab.info() {
                if !ab.is_ready().unwrap_or(false) {
                    continue;
                }
                let mut best = (cur, self.pos);
                for dx in -2..=2 {
                    for dy in -2..=2 {
                        let p = self.pos + Vec2::new(dx, dy);
                        if cheb(p, self.pos) != 2 || !self.free(p) {
                            continue;
                        }
                        let v = field.get(p)?;
                        if v + 1 < best.0 {
                            best = (v, p);
                        }
                    }
                }
                if best.1 != self.pos {
                    if let Ok(true) = ab.cast_at(best.1) {
                        self.pos = best.1;
                        self.cast = true;
                    }
                }
                return Ok(());
            }
        }
        Ok(())
    }

    /// Step away from threats: walk the shortest path to the best nearby
    /// tile no threat reaches (one-step scoring gets stuck between two camps
    /// or behind a wall), preferring the way home and teammates. Path
    /// searches run on the host; wasm loops over tiles cost too much fuel.
    pub fn flee(&mut self, camps: &[(Vec2, i32, f32)]) -> Result<bool> {
        if self.moved {
            return Ok(false);
        }
        let spawn_key = self.kb.spawn_field();
        self.kb.ensure_field(spawn_key)?;
        let mut danger = Bitboard::new()?;
        for e in self.enemies.iter().filter(|e| !e.on_spawn) {
            danger.draw_chebyshev(e.pos, (e.range + 2) as f32)?;
        }
        for &(c, r, _) in camps {
            danger.draw_chebyshev(c, r as f32)?;
        }
        // Hit by something we cannot see (an enemy in a bush): keep off bushes.
        if self.taken > 0.5 && self.enemies.is_empty() && camps.is_empty() {
            danger.union_assign(cambc::map::bushes()?)?;
        }
        let mut walls = self.kb.blocked.union(&self.occupied)?;
        walls.set(self.pos, false)?;
        let mut here = Bitboard::new()?;
        here.set(self.pos, true)?;
        let mut from_me = DistanceField::new()?;
        let mut reached = Bitboard::new()?;
        from_me.compute(&walls, &here, &mut reached, 7)?;
        let from_me = Field::from_df(&from_me)?;
        reached.intersect_assign(&danger.complement()?)?;
        reached.set(self.pos, false)?;
        // Sorting in wasm is costly: narrow on the host, then partial select.
        let mut near = Bitboard::new()?;
        near.draw_chebyshev(self.pos, 3.0)?;
        let mut cands = reached.intersect(&near)?.positions()?;
        if cands.is_empty() {
            cands = reached.positions()?;
        }
        let pos = self.pos;
        if cands.len() > 10 {
            cands.select_nth_unstable_by_key(9, |p| cheb(*p, pos));
            cands.truncate(10);
        }
        let allies: Vec<Vec2> = self.allies.iter().map(|a| a.pos).collect();
        let mut best: Option<(f32, Vec2)> = None;
        for &p in &cands {
            let d = from_me.get(p)?;
            let home = self.kb.lookup(self.kb.fields[spawn_key].as_ref().unwrap(), p)?;
            if d == NO_DIST || home == NO_DIST {
                continue;
            }
            let near_ally = allies.iter().any(|a| cheb(*a, p) <= 2);
            let cost = d as f32 * 3.0 + home as f32 * 0.3 - if near_ally { 2.0 } else { 0.0 };
            if best.map_or(true, |b| cost < b.0) {
                best = Some((cost, p));
            }
        }
        if let Some((_, t)) = best {
            // Walk the field back from the target to the tile beside us.
            let mut cur = t;
            let mut v = from_me.get(cur)?;
            while v > 1 {
                let Some(nx) = DIRS.iter().map(|d| cur + *d).find(|q| from_me.get(*q).unwrap_or(NO_DIST) == v - 1) else { break };
                cur = nx;
                v -= 1;
            }
            if v == 1 {
                if let Ok(true) = me().move_absolute(cur) {
                    self.pos = cur;
                    self.moved = true;
                    return Ok(true);
                }
            }
        }
        // Nowhere safe in reach: least danger, then the way home.
        let field = self.kb.fields[spawn_key].take().unwrap();
        let r = self.step_by(|_, p| {
            let d = if danger.is_set(p).unwrap_or(true) { 25.0 } else { 0.0 };
            let near_ally = allies.iter().any(|a| cheb(*a, p) <= 2);
            d + field.get(p).unwrap_or(NO_DIST).min(500) as f32 * 0.5 - if near_ally { 3.0 } else { 0.0 }
        });
        self.kb.fields[spawn_key] = Some(field);
        r
    }

    pub fn use_shield(&mut self) {
        if self.cast {
            return;
        }
        for ab in me().abilities() {
            if let Ok(Some(AbilityInfo::Shield(_))) = ab.info() {
                if ab.is_ready().unwrap_or(false) && ab.cast_untargeted().unwrap_or(false) {
                    self.cast = true;
                }
            }
        }
    }
}
