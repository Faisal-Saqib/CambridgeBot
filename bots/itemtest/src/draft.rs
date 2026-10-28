use cambc::{ChampionDraft as D, Result, Team};

/// Pick order by team size. Cassi & Issac is one pick but two bodies.
fn preferences(team_size: usize) -> &'static [D] {
    match team_size {
        // (Tested over all 70 maps against titan: Vendetta for small maps
        // 4-12 on 3/4-pick maps, Cassi & Issac everywhere 52-88. Kept.)
        0..=3 => &[D::VesperVale, D::Marcella, D::Ryth, D::Tavi, D::Willow],
        4 => &[D::VesperVale, D::Marcella, D::Ryth, D::Tavi, D::Willow],
        _ => &[D::Willow, D::VesperVale, D::Ryth, D::Tavi, D::Marcella],
    }
}

pub fn play() -> Result<()> {
    let chosen = cambc::draft::current_draft(Team::Ally)?;
    let size = cambc::draft::team_size()?;
    for &pick in preferences(size) {
        if !chosen.contains(&pick) {
            return cambc::draft::pick(pick);
        }
    }
    for &pick in D::ALL {
        if !chosen.contains(&pick) {
            return cambc::draft::pick(pick);
        }
    }
    Ok(())
}
