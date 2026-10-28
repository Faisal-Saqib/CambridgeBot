#include "config.h"

// Balanced flagship: spread sector farming, full ability use, contesting,
// jungle-family items for cheap camp sustain.
const StratConfig CFG = [] {
    StratConfig c;
    c.name = "monster";
    // DPS-first draft: basic-attack strength wins farm races, and Vendetta's
    // kill-reset passive is the best camp clearer in the roster. Vesper's
    // +33% gold and Tavi's shop-anywhere come next; pure casters last.
    c.draft_order = {
        cambc::champion_draft::vendetta,
        cambc::champion_draft::vesper_vale,
        cambc::champion_draft::varg,
        cambc::champion_draft::tavi,
        cambc::champion_draft::willow,
        cambc::champion_draft::ryth,
        cambc::champion_draft::marcella,
        cambc::champion_draft::heart_of_ruin,
        cambc::champion_draft::ren,
        cambc::champion_draft::cassi_and_issac,
        cambc::champion_draft::prism,
        cambc::champion_draft::stellar,
    };
    c.item_family = cambc::item_family::monster;
    c.tribute_min = 8;
    c.recall_frac = 0.30f;
    c.buy_locks = true;
    c.buy_tp = false;
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
