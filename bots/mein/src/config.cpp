#include "config.h"

// Balanced flagship: spread sector farming, full ability use, contesting,
// jungle-family items for cheap camp sustain.
const StratConfig CFG = [] {
    StratConfig c;
    c.name = "main";
    c.heal_shadow = true;   // opponent comps sustain through hunts via Willow
    c.buy_tp = true;
    // DPS-first draft: basic-attack strength wins farm races, and Vendetta's
    // kill-reset passive is the best camp clearer in the roster. Vesper's
    // +33% gold and Tavi's shop-anywhere come next; Willow keeps farmers
    // alive; pure casters last. (Marcella/Heart of Ruin looked strong in
    // opponent lineups but our engine can't exploit their synergy — they
    // farmed ~300 gems worse than the DPS comp.)
    // Willow sits third: small-draft maps (3 picks) still get a healer, and
    // full drafts keep the same five.
    // Cassi & Issac sits third: one pick buys two bodies (extra capture
    // speed, farm parallelism, and a stun), and peer teams beat us with the
    // 4v3/6v5 body advantage on every map size.
    c.draft_order = {
        cambc::champion_draft::vendetta,
        cambc::champion_draft::vesper_vale,
        cambc::champion_draft::cassi_and_issac,
        cambc::champion_draft::varg,
        cambc::champion_draft::ryth,
        cambc::champion_draft::tavi,
        cambc::champion_draft::willow,
        cambc::champion_draft::marcella,
        cambc::champion_draft::heart_of_ruin,
        cambc::champion_draft::ren,
        cambc::champion_draft::prism,
        cambc::champion_draft::stellar,
    };
    c.item_family = cambc::item_family::jungle;
    c.tribute_min = 5;
    c.recall_frac = 0.30f;
    c.buy_locks = true;
    c.buy_tp = true;
    c.spread = true;
    c.contest = true;
    c.wards = true;
    c.use_abilities = true;
    c.chase_enemies = false;
    c.group_farm = false;
    c.engage_safety = 0.8f;
    c.flee_frac = 0.35f;
    return c;
}();
