// Emblem build orders: buy shards of the first unfinished emblem in order.
// The same emblem may appear several times; stats stack, passives do not.
use cambc::{get_item_enum, Champion, ChampionType as C, ItemFamily as F, ItemStat as S, Result};

const FIGHTER: &[(F, S)] = &[
    (F::Monster, S::Strength),
    (F::Jungle, S::Health),
    (F::Durability, S::Health),
];

const TANK: &[(F, S)] = &[
    (F::Jungle, S::Health),
    (F::Monster, S::Strength),
    (F::Durability, S::Health),
];

const CASTER: &[(F, S)] = &[
    (F::Durability, S::Health),
    (F::Monster, S::Focus),
];

/// Opening emblems (one passive each), then Bruiser for good: 5 shards of
/// the chosen stat plus one of each other is the best stats per gold, and
/// stats stack across copies.
pub fn build(kind: C) -> Vec<(F, S)> {
    let (opening, main) = match kind {
        C::Ryth | C::Ren | C::HeartOfRuin => (TANK, S::Strength),
        C::Marcella | C::Cassi | C::Stellar | C::Prism => (CASTER, S::Focus),
        _ => (FIGHTER, S::Strength),
    };
    let mut plan = opening.to_vec();
    for i in 0..30 {
        plan.push((F::Bruiser, if i % 4 == 3 { S::Health } else { main }));
    }
    plan
}

/// Spend gold on the build; returns true if anything was bought.
pub fn shop(me: &Champion, kind: C) -> Result<bool> {
    let mut bought = false;
    let counts = me.item_count()?;
    let mut gold = me.gold_count()?;
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
