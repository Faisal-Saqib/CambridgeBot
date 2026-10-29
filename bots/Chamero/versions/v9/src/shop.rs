// Emblem build orders: buy shards of the first unfinished emblem in order.
// The same emblem may appear several times; stats stack, passives do not.
//
// forge: engine 2.0 added Capture (team capture capped at 3 rounds instead
// of 5), Prospector (+25% of our cluster share), Collectors (+1% damage per
// unique emblem family) and others. Top-20 teams buy Monster/Capture/
// Prospector/Collectors on their farmers; v24 never bought any of them.
// Every emblem is 5 shards of its stat, so a useful passive costs only the
// one extra shard of stats that Power would have given.
use cambc::{get_item_enum, Champion, ChampionType as C, ConsumableType, ItemFamily as F, ItemStat as S, Result};

/// Main damage stat for a champion: what its kit scales with.
fn main_stat(kind: C) -> S {
    match kind {
        C::Marcella | C::Cassi | C::Stellar | C::Prism | C::HeartOfRuin => S::Focus,
        _ => S::Strength,
    }
}

/// Opening emblems (one passive each, by priority), then Bruiser for good:
/// 5 shards of the main stat plus one of each other is the most stats per
/// gold, and stats stack across copies.
pub fn build(kind: C) -> Vec<(F, S)> {
    let m = main_stat(kind);
    let opening: Vec<(F, S)> = match kind {
        // Frontline: survive camps first, then farm speed.
        C::Ryth | C::Ren | C::HeartOfRuin => vec![
            (F::Jungle, S::Health),
            (F::Monster, m),
            (F::Capture, m),
            (F::Durability, S::Health),
            (F::Collectors, m),
            (F::Prospector, m),
        ],
        // Fragile casters: one health emblem before damage.
        C::Marcella | C::Cassi | C::Stellar | C::Prism => vec![
            (F::Durability, S::Health),
            (F::Monster, m),
            (F::Capture, m),
            (F::Jungle, S::Health),
            (F::Collectors, m),
            (F::Prospector, m),
        ],
        // Vesper's gold passive compounds with Treasure.
        C::VesperVale => vec![
            (F::Monster, m),
            (F::Capture, m),
            (F::Treasure, m),
            (F::Jungle, S::Health),
            (F::Durability, S::Health),
            (F::Collectors, m),
            (F::Prospector, m),
        ],
        _ => vec![
            (F::Monster, m),
            (F::Capture, m),
            (F::Jungle, S::Health),
            (F::Durability, S::Health),
            (F::Collectors, m),
            (F::Prospector, m),
        ],
    };
    let mut plan = opening;
    for i in 0..30 {
        plan.push((F::Bruiser, if i % 4 == 3 { S::Health } else { m }));
    }
    plan
}

/// Spend gold on the build; returns true if anything was bought.
pub fn shop(me: &Champion, kind: C) -> Result<bool> {
    let mut bought = false;
    let counts = me.item_count()?;
    let mut gold = me.gold_count()?;
    // Chamero: always carry one altar lock (10 gold; top teams all do).
    let lock = &me.consumables()[ConsumableType::AltarLock];
    if lock.count().unwrap_or(1) == 0 && gold >= 10 && me.can_buy_consumable(ConsumableType::AltarLock).unwrap_or(false) {
        if me.buy_consumable(ConsumableType::AltarLock).is_ok() {
            gold -= 10;
            bought = true;
        }
    }
    let plan = build(kind);
    for (i, &(family, stat)) in plan.iter().enumerate() {
        let shard = get_item_enum(family, stat, true);
        let emblem = get_item_enum(family, stat, false);
        // This entry is done if we own as many emblems as it has occurrences so far.
        let occurrences = plan[..=i].iter().filter(|&&x| x == (family, stat)).count() as u32;
        if counts[emblem] >= occurrences {
            continue;
        }
        let need = shard.combine_count()?.saturating_sub(counts[shard]);
        let cost = shard.cost()?;
        let n = need.min(gold / cost);
        if n == 0 {
            break;
        }
        if me.can_buy(shard, n)? {
            me.buy_count(shard, n)?;
            bought = true;
            gold -= n * cost;
        } else {
            break;
        }
        if n < need {
            break;
        }
    }
    Ok(bought)
}

/// Whether the build still has something to buy.
pub fn has_next(me: &Champion, kind: C) -> Result<bool> {
    let counts = me.item_count()?;
    let plan = build(kind);
    for (i, &(family, stat)) in plan.iter().enumerate() {
        let emblem = get_item_enum(family, stat, false);
        let occurrences = plan[..=i].iter().filter(|&&x| x == (family, stat)).count() as u32;
        if counts[emblem] < occurrences {
            return Ok(true);
        }
    }
    Ok(false)
}
