// Static map knowledge shared by every turn: terrain, camp groups, altars,
// spawn, plus lazily computed static distance fields.
use crate::util::cheb;
use cambc::{Bitboard, CampGroup, CampType, DistanceField, Result, Team, Vec2};

pub const NO_DIST: u16 = DistanceField::UNREACHABLE;

/// A distance field copied into wasm memory. Host `DistanceField::get`
/// calls cost hundreds of fuel each; indexing this costs a handful.
pub struct Field {
    w: i32,
    h: i32,
    d: Vec<u16>,
}

impl Field {
    pub fn from_df(df: &DistanceField) -> Result<Self> {
        Ok(Self { w: df.width(), h: df.height(), d: df.export_linear_buffer()? })
    }

    /// Distance at `p`; off-map tiles read as unreachable.
    #[inline]
    pub fn get(&self, p: Vec2) -> Result<u16> {
        Ok(if p.x < 0 || p.y < 0 || p.x >= self.w || p.y >= self.h { NO_DIST } else { self.d[(p.y * self.w + p.x) as usize] })
    }
}

#[derive(Clone, Copy)]
pub struct CampDesign {
    pub hp: f32,
    pub dmg: f32,
    pub range: i32,
}

pub fn camp_design(kind: CampType) -> CampDesign {
    // Values verified against the 4.0.0 engine (CampStats dump); Golem and
    // Monolith ranges come from the handbook.
    match kind {
        CampType::Wolf => CampDesign { hp: 1350.0, dmg: 20.0, range: 3 },
        CampType::Elk => CampDesign { hp: 2400.0, dmg: 60.0, range: 4 },
        CampType::GemCluster => CampDesign { hp: 120.0, dmg: 0.0, range: 0 },
        CampType::GoldCluster => CampDesign { hp: 120.0, dmg: 0.0, range: 0 },
        CampType::Monolith => CampDesign { hp: 20000.0, dmg: 200.0, range: 5 },
        CampType::Golem => CampDesign { hp: 5000.0, dmg: 120.0, range: 4 },
    }
}

pub struct Group {
    pub cg: CampGroup,
    pub tiles: Bitboard,
    pub camps: Vec<(Vec2, CampType)>,
    pub gems: u32,
    pub gold: u32,
    pub respawn: i32,
    pub hp: f32,
    pub danger_dps: f32,
    pub danger_hp: f32,
    pub max_range: i32,
    pub center: Vec2,
    pub monolith: bool,
}

impl Group {
    /// Damage the tank absorbs while a team of total dps `dps` kills the
    /// dangerous camps one at a time, most dangerous first.
    pub fn expected_damage(&self, dps: f32) -> f32 {
        if dps <= 0.0 {
            return f32::MAX;
        }
        let mut dangerous: Vec<CampDesign> = self
            .camps
            .iter()
            .map(|c| camp_design(c.1))
            .filter(|d| d.dmg > 0.0)
            .collect();
        dangerous.sort_by(|a, b| (b.dmg / b.hp).partial_cmp(&(a.dmg / a.hp)).unwrap());
        let mut remaining_dps: f32 = dangerous.iter().map(|d| d.dmg).sum();
        let mut total = 0.0;
        for d in dangerous {
            total += remaining_dps * d.hp / dps;
            remaining_dps -= d.dmg;
        }
        total
    }
}

pub struct Kb {
    pub w: i32,
    pub h: i32,
    pub area: i32,
    pub blocked: Bitboard,
    /// `blocked` and the map's bushes as plain arrays (no host calls).
    pub blocked_v: Vec<bool>,
    pub bush_v: Vec<bool>,
    /// Static terrain plus every camp tile, for long-range path fields.
    pub path_blocked: Bitboard,
    pub altars: Vec<Vec2>,
    pub spawn: Bitboard,
    pub spawn_tiles: Vec<Vec2>,
    pub spawn_center: Vec2,
    pub enemy_spawn: Bitboard,
    pub enemy_spawn_center: Vec2,
    pub groups: Vec<Group>,
    /// Per altar: the camp (group, index) on its only approach, when every
    /// tile beside the altar is terrain or a camp.
    pub gates: Vec<Option<(usize, usize)>>,
    /// Static fields: groups first, then altars, then our spawn.
    pub fields: Vec<Option<Field>>,
}

fn centroid(tiles: &[Vec2]) -> Vec2 {
    let n = tiles.len().max(1) as i32;
    let (sx, sy) = tiles.iter().fold((0, 0), |(x, y), p| (x + p.x, y + p.y));
    Vec2::new(sx / n, sy / n)
}

impl Kb {
    pub fn new() -> Result<Self> {
        let w = cambc::map::width()?;
        let h = cambc::map::height()?;
        let spawn = cambc::map::spawn_region(Team::Ally)?.clone();
        let enemy_spawn = cambc::map::spawn_region(Team::Enemy)?.clone();
        let altars_bb = cambc::map::altars()?;
        let mut blocked = cambc::map::walls()?.clone();
        blocked.union_assign(cambc::map::holes()?)?;
        blocked.union_assign(altars_bb)?;
        blocked.union_assign(&enemy_spawn)?;
        let altars = altars_bb.positions()?;
        let spawn_tiles = spawn.positions()?;
        let spawn_center = centroid(&spawn_tiles);
        let enemy_spawn_center = centroid(&enemy_spawn.positions()?);
        let mut groups = Vec::new();
        for cg in cambc::map::camp_groups()? {
            let camps: Vec<(Vec2, CampType)> =
                cg.camps().iter().map(|c| (c.spawn_position(), c.kind())).collect();
            let mut hp = 0.0;
            let mut danger_dps = 0.0;
            let mut danger_hp = 0.0;
            let mut max_range = 0;
            let mut monolith = false;
            for &(_, k) in &camps {
                let d = camp_design(k);
                hp += d.hp;
                if d.dmg > 0.0 {
                    danger_dps += d.dmg;
                    danger_hp += d.hp;
                }
                max_range = max_range.max(d.range);
                monolith |= k == CampType::Monolith;
            }
            let positions: Vec<Vec2> = camps.iter().map(|c| c.0).collect();
            groups.push(Group {
                tiles: cg.spawn_tiles()?,
                gems: cg.gem_value(),
                gold: cg.gold_value(),
                respawn: cg.max_respawn_timer(),
                center: centroid(&positions),
                cg,
                camps,
                hp,
                danger_dps,
                danger_hp,
                max_range,
                monolith,
            });
        }
        let mut blocked_v = vec![false; (w * h) as usize];
        for p in blocked.positions()? {
            blocked_v[(p.y * w + p.x) as usize] = true;
        }
        let mut bush_v = vec![false; (w * h) as usize];
        for p in cambc::map::bushes()?.positions()? {
            bush_v[(p.y * w + p.x) as usize] = true;
        }
        let mut path_blocked = blocked.clone();
        for g in &groups {
            path_blocked.union_assign(&g.tiles)?;
        }
        let mut gates = Vec::with_capacity(altars.len());
        for &a in &altars {
            let mut open = false;
            let mut gate: Option<(i32, (usize, usize))> = None;
            for dy in -1..=1 {
                for dx in -1..=1 {
                    let p = Vec2::new(a.x + dx, a.y + dy);
                    if (dx == 0 && dy == 0) || p.x < 0 || p.y < 0 || p.x >= w || p.y >= h || blocked.is_set(p)? {
                        continue;
                    }
                    if !path_blocked.is_set(p)? {
                        open = true;
                    }
                    for (g, grp) in groups.iter().enumerate() {
                        if let Some(i) = grp.camps.iter().position(|c| c.0 == p) {
                            let d = cheb(p, spawn_center);
                            if gate.map_or(true, |b| d < b.0) {
                                gate = Some((d, (g, i)));
                            }
                        }
                    }
                }
            }
            gates.push(if open { None } else { gate.map(|g| g.1) });
        }
        let nfields = groups.len() + 2 * altars.len() + 1;
        let mut fields = Vec::with_capacity(nfields);
        fields.resize_with(nfields, || None);
        Ok(Self {
            w,
            h,
            area: w * h,
            blocked,
            blocked_v,
            bush_v,
            path_blocked,
            altars,
            spawn,
            spawn_tiles,
            spawn_center,
            enemy_spawn,
            enemy_spawn_center,
            groups,
            gates,
            fields,
        })
    }

    pub fn altar_field(&self, i: usize) -> usize {
        self.groups.len() + i
    }
    pub fn spawn_field(&self) -> usize {
        self.groups.len() + self.altars.len()
    }
    /// Altar field that treats camps as passable (they can be cut through).
    pub fn altar_breach_field(&self, i: usize) -> usize {
        self.groups.len() + self.altars.len() + 1 + i
    }

    /// Approximate fuel cost of one field computation on this map.
    pub fn field_cost(&self) -> u64 {
        (self.area as u64) * 3 + 2000
    }

    fn roots_for(&self, key: usize) -> Result<Bitboard> {
        let mut roots = Bitboard::new()?;
        if key < self.groups.len() {
            roots = self.groups[key].tiles.clone();
        } else if key < self.groups.len() + self.altars.len() {
            roots.set(self.altars[key - self.groups.len()], true)?;
        } else if key == self.spawn_field() {
            roots = self.spawn.clone();
        } else {
            roots.set(self.altars[key - self.spawn_field() - 1], true)?;
        }
        Ok(roots)
    }

    pub fn ensure_field(&mut self, key: usize) -> Result<()> {
        if self.fields[key].is_some() {
            return Ok(());
        }
        let roots = self.roots_for(key)?;
        let mut walls = if key > self.spawn_field() { self.blocked.clone() } else { self.path_blocked.clone() };
        walls.intersect_assign(&roots.complement()?)?;
        let mut field = DistanceField::new()?;
        let mut visited = Bitboard::new()?;
        field.compute(&walls, &roots, &mut visited, NO_DIST)?;
        self.fields[key] = Some(Field::from_df(&field)?);
        Ok(())
    }

    /// Field lookup that treats our own tile as open: standing on a dead
    /// camp's tile (a wall in other fields) reads through the neighbours.
    pub fn lookup(&self, f: &Field, p: Vec2) -> Result<u16> {
        let v = f.get(p)?;
        if v != NO_DIST {
            return Ok(v);
        }
        let mut best = NO_DIST;
        for dx in -1..=1 {
            for dy in -1..=1 {
                let q = p + Vec2::new(dx, dy);
                if (dx, dy) != (0, 0) && self.in_bounds(q) {
                    let w = f.get(q)?;
                    if w != NO_DIST {
                        best = best.min(w + 1);
                    }
                }
            }
        }
        Ok(best)
    }

    /// Distance from `p` to field `key`, computing the field if needed.
    pub fn dist(&mut self, key: usize, p: Vec2) -> Result<u16> {
        self.ensure_field(key)?;
        self.lookup(self.fields[key].as_ref().unwrap(), p)
    }

    /// Distance if the field already exists, otherwise an optimistic estimate.
    pub fn dist_or_estimate(&self, key: usize, p: Vec2, target: Vec2) -> Result<u16> {
        match &self.fields[key] {
            Some(f) => self.lookup(f, p),
            None => Ok((p.chebyshev_distance(target) as f32 * 1.25) as u16),
        }
    }

    pub fn is_blocked(&self, p: Vec2) -> bool {
        !self.in_bounds(p) || self.blocked_v[(p.y * self.w + p.x) as usize]
    }

    pub fn is_bush(&self, p: Vec2) -> bool {
        self.in_bounds(p) && self.bush_v[(p.y * self.w + p.x) as usize]
    }

    pub fn in_bounds(&self, p: Vec2) -> bool {
        p.x >= 0 && p.y >= 0 && p.x < self.w && p.y < self.h
    }
}
