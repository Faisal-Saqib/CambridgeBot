#include "config.h"

// Warband: two-tier farming. Cheap groups are farmed solo and spread out;
// groups a lone champion can't clear without dying are farmed by a squad that
// gathers outside aggro (shared-memory rally), lets the tank take the hits and
// focus-fires. Sightings are broadcast so carriers dodge hunters nobody else
// can see and nearby free champions answer distress calls.
const StratConfig CFG = [] {
    StratConfig c;
    c.name = "squad";
    // Tank + healer core: camps hit the nearest champion, so a 1200hp Ryth in
    // front with Willow behind makes elk/golem groups safe for the squad.
    c.draft_order = {
        cambc::champion_draft::vendetta,
        cambc::champion_draft::vesper_vale,
        cambc::champion_draft::ryth,
        cambc::champion_draft::willow,
        cambc::champion_draft::marcella,
        cambc::champion_draft::cassi_and_issac,
        cambc::champion_draft::varg,
        cambc::champion_draft::tavi,
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
    c.engage_safety = 0.8f;
    c.flee_frac = 0.35f;
    c.heal_shadow = true;
    c.rally = true;
    c.beacon = true;
    c.ranged_standoff = true;
    return c;
}();
