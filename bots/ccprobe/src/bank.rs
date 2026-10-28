// Tributing gems at altars, including cutting through camps that wall an
// altar in.
use crate::bot::{Bot, LiveCamp};
use crate::kb::NO_DIST;
use crate::log;
use crate::util::{cheb, me, DIRS};
use cambc::{ChampionType, Result, Team};

/// Tribute thresholds (gems carried): anywhere / altar within 15 / within 4.
const BANK_ANY: u32 = 30;
const BANK_NEAR: u32 = 15;
const BANK_CLOSE: u32 = 5;
/// The same when threatened.
const BANK_THREAT_ANY: u32 = 15;
const BANK_THREAT_NEAR: u32 = 8;

impl Bot {
    pub fn nearest_altar(&mut self) -> Result<Option<(usize, u16)>> {
        let mut best: Option<(usize, u16)> = None;
        for a in 0..self.kb.altars.len() {
            if self.altar_block[a] > self.round {
                continue;
            }
            let key = self.kb.altar_field(a);
            let d = self.kb.dist_or_estimate(key, self.pos, self.kb.altars[a])?;
            if d == NO_DIST {
                continue;
            }
            // Altars where enemies were seen recently are worth a detour to avoid.
            let altar = self.kb.altars[a];
            let hot = self.enemy_seen_at.iter().any(|(p, r)| cheb(*p, altar) <= 6 && *r + 40 > self.round);
            let d = if hot { d.saturating_add(12) } else { d };
            if best.map_or(true, |b| d < b.1) {
                best = Some((a, d));
            }
        }
        Ok(best)
    }

    /// Altars reachable only by cutting through camps.
    pub fn nearest_breach_altar(&mut self) -> Result<Option<(usize, u16)>> {
        let mut best: Option<(usize, u16)> = None;
        for a in 0..self.kb.altars.len() {
            let d = self.kb.dist(self.kb.altar_breach_field(a), self.pos)?;
            if d != NO_DIST && best.map_or(true, |b| d < b.1) {
                best = Some((a, d));
            }
        }
        Ok(best)
    }

    pub fn should_bank(&mut self) -> Result<bool> {
        let gems = self.gems;
        if gems == 0 || self.capture_on.is_some() {
            return Ok(false);
        }
        if self.gate_now.is_some() {
            return Ok(false);
        }
        let banked = cambc::global_submitted_gems(Team::Ally)?;
        if banked + gems >= 1000 || self.round > 1900 {
            return Ok(true);
        }
        let d = match self.nearest_altar()? {
            Some((_, d)) => d,
            None => match self.nearest_breach_altar()? {
                Some((_, d)) => d,
                None => return Ok(false),
            },
        };
        // Bank small and often. A death hands every carried gem to the killer:
        // titan's 40-60 gem hauls lost 2,586 gems in 10 games against
        // Ascendance, who tribute 22-54 at a time. Under threat (enemy close
        // recently, a teammate just died, or hurt) carry even less. Marcella
        // earns 2 gold per gem tributed, so she always banks early.
        let (anywhere, near, close) = if self.threatened() || self.kind == ChampionType::Marcella {
            (BANK_THREAT_ANY, BANK_THREAT_NEAR, BANK_CLOSE)
        } else {
            (BANK_ANY, BANK_NEAR, BANK_CLOSE)
        };
        Ok(gems >= anywhere || (gems >= near && d <= 15) || (gems >= close && d <= 4))
    }

    pub fn bank(&mut self) -> Result<()> {
        let altar_choice = self.nearest_altar()?;
        let Some((a, _)) = altar_choice.or(self.nearest_breach_altar()?) else { return Ok(()) };
        let altar = self.kb.altars[a];
        if cheb(self.pos, altar) <= 1 {
            log!(self, "tribute {} gems", self.gems);
            if me().submit_gems(altar).is_err() {
                self.altar_block[a] = self.round + 10;
            }
            return Ok(());
        }
        if altar_choice.is_some() {
            self.step_field(self.kb.altar_field(a))?;
        } else {
            self.breach_towards(a)?;
        }
        if cheb(self.pos, altar) <= 1 && !self.cast {
            me().submit_gems(altar).ok();
        }
        Ok(())
    }

    /// Walk the terrain-only field to an altar, killing camps in the way.
    fn breach_towards(&mut self, a: usize) -> Result<()> {
        let key = self.kb.altar_breach_field(a);
        self.kb.ensure_field(key)?;
        let field = self.kb.fields[key].take().unwrap();
        let cur = field.get(self.pos)?;
        // Blocking camp: the nearest one closer to the altar than we are.
        let mut blocker: Option<(u16, LiveCamp)> = None;
        for cp in cambc::vision::camp_tiles()?.positions()? {
            if cheb(cp, self.pos) > 4 {
                continue;
            }
            let v = field.get(cp)?;
            let key_v = (cheb(cp, self.pos) as u16) * 100 + v;
            if v < cur && blocker.as_ref().map_or(true, |b| key_v < b.0) {
                if let Ok(c) = cambc::vision::camp_at(cp) {
                    blocker = Some((key_v, LiveCamp { pos: cp, hp: c.health().unwrap_or(0.0), kind: c.kind(), awake: c.is_awake().unwrap_or(false), camp: c }));
                }
            }
        }
        let mut vals = [NO_DIST; 8];
        for (i, d) in DIRS.iter().enumerate() {
            let p = self.pos + *d;
            if self.kb.in_bounds(p) {
                vals[i] = field.get(p)?;
            }
        }
        self.kb.fields[key] = Some(field);
        // Only strict progress counts; otherwise cut through the blocker.
        let progressed = self.step_by(|s, p| {
            if p == s.pos {
                return cur as f32;
            }
            let i = DIRS.iter().position(|x| *x == p - s.pos).unwrap_or(0);
            if vals[i] < cur { vals[i] as f32 } else { f32::MAX }
        })?;
        if !progressed {
            if let Some((_, c)) = blocker {
                let rng = self.range;
                let tp = c.pos;
                if cheb(self.pos, tp) > rng {
                    self.step_by(|_, p| (cheb(p, tp) - rng).max(0) as f32)?;
                }
                if self.melee || !self.moved {
                    self.basic_attack(&c.camp, tp)?;
                }
            }
        }
        Ok(())
    }
}
