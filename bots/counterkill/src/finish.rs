// Local experiment: an immediate finishing action may precede retreat.
use crate::bot::{Bot, Enemy};
use crate::util::{cheb, me};
use cambc::{AbilityInfo, AbilityTargetMask, BuffKind, BuffPayload, ChampionType, Result};

impl Bot {
    pub fn try_finish_now(&mut self) -> Result<bool> {
        // Preserve heavy carriers and reserve fuel for the ordinary safety path.
        if (self.frac() >= 0.35 && !self.healing) || self.gems >= 15 || self.enemies.is_empty() {
            return Ok(false);
        }
        if crate::util::fuel() < 25_000 {
            return Ok(false);
        }
        let me = me();
        let can_basic = !self.attacked && me.can_attack()? && self.kind != ChampionType::Varg;
        let can_spell = !self.cast && me.can_cast()?;
        // A deliberately conservative heuristic, not an exact damage formula.
        let basic_floor = if can_basic { me.strength()? * 0.75 } else { 0.0 };
        let mut candidates: Vec<Enemy> = self.enemies.iter()
            .filter(|e| e.hp > 0.0 && !e.on_spawn && cheb(e.pos, self.pos) <= 6)
            .cloned().collect();
        candidates.sort_by(|a, b| a.hp.partial_cmp(&b.hp).unwrap_or(std::cmp::Ordering::Equal));
        for enemy in candidates {
            if crate::util::fuel() < 15_000 {
                break;
            }
            // Ren retaliates even when killed. Keep a margin over his 0.2 Focus hit.
            if enemy.ch.champion_name().ok() == Some(ChampionType::Ren) {
                let reflect = enemy.ch.focus().unwrap_or(f32::INFINITY) * 0.25;
                if self.hp <= reflect {
                    continue;
                }
            }
            let d = cheb(enemy.pos, self.pos);
            if can_basic && d <= self.range && basic_floor >= enemy.hp + 1.0 {
                if let Ok(buffs) = enemy.ch.buffs() {
                    let shield = match buffs.get(BuffKind::Shield) {
                        Some(BuffPayload::Shield { value, .. }) => value.max(0.0),
                        _ => 0.0,
                    };
                    let predicted = (basic_floor - shield).max(0.0);
                    if predicted >= enemy.hp + 1.0 && me.attack(&enemy.ch).is_ok() {
                        self.attacked = true;
                        self.trace_finish(&enemy, "basic", predicted);
                        return Ok(true);
                    }
                }
            }
            if !can_spell {
                continue;
            }
            for ab in me.abilities() {
                let Ok(Some(info)) = ab.info() else { continue };
                let (range, properties) = match info {
                    AbilityInfo::Damage(a) if a.modifier > 0.0 => (a.range, a.properties),
                    AbilityInfo::Cc(a) if a.modifier > 0.0 => (a.range, a.properties),
                    _ => continue,
                };
                // Do not add splash/dash/ground targeting or assume a combo.
                if !properties.valid_targets.contains(AbilityTargetMask::ENEMIES)
                    || d as f32 > range
                    || (properties.exclusive_with_movement && self.moved)
                    || !ab.is_ready().unwrap_or(false)
                {
                    continue;
                }
                let Ok(predicted) = ab.damage_amount_against(&enemy.ch) else { continue };
                if predicted >= enemy.hp && ab.cast_on(&enemy.ch).unwrap_or(false) {
                    self.cast = true;
                    self.trace_finish(&enemy, "spell", predicted);
                    return Ok(true);
                }
            }
        }
        Ok(false)
    }

    fn trace_finish(&self, enemy: &Enemy, action: &str, predicted: f32) {
        println!("FINISH_NOW r{} self={:?} hp={} target={} target_hp={} action={} predicted={} killed={}",
            self.round, self.kind, self.hp, enemy.idx, enemy.hp, action, predicted,
            !enemy.ch.is_alive().unwrap_or(true));
    }
}
