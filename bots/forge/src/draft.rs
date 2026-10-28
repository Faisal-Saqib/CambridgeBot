use cambc::{ChampionDraft as D, Result, Team};

/// Pick order by team size. Cassi & Issac is one pick but two bodies.
///
/// forge: copied from what top-20 teams draft (matches/top-team-study-20261028
/// and the 25-game v22 top-20 baseline). On 3-pick Anvil every opponent that
/// beat us had two of Marcella / Vesper / Heart of Ruin. On Expanse their
/// Vendetta and Varg dealt 35-50k camp damage while our Willow and Tavi dealt
/// 10-25k, so the support picks are replaced by farmers that also fight.
fn preferences(team_size: usize) -> &'static [D] {
    match team_size {
        0..=3 => &[D::Marcella, D::VesperVale, D::HeartOfRuin, D::Vendetta, D::Ryth],
        4 => &[D::VesperVale, D::Vendetta, D::HeartOfRuin, D::Marcella, D::Varg],
        _ => &[D::VesperVale, D::Vendetta, D::HeartOfRuin, D::Varg, D::Marcella, D::Ryth],
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
