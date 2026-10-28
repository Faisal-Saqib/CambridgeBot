// Dump the engine's item table (stats, passive, cost) and resign.
use cambc::{ItemType, ChampionDraft};

fn main() -> cambc::Result<()> {
    loop {
        if cambc::is_draft() {
            let chosen = cambc::draft::current_draft(Some(cambc::Team::Ally).unwrap())?;
            for &p in ChampionDraft::ALL {
                if !chosen.contains(&p) { cambc::draft::pick(p).ok(); break; }
            }
        } else {
            for &it in ItemType::ALL {
                if let Ok(info) = it.info() {
                    println!("ITEM {:?} cost={} combine={} result={:?} hp={} str={} foc={} passive={:?} mag={} buy={}",
                        it, info.cost, info.combine_count, info.result, info.health_points, info.strength_points,
                        info.focus_points, info.passive, info.passive_magnitude, info.purchasable);
                }
            }
            cambc::resign().ok();
        }
        cambc::end_turn();
    }
}
