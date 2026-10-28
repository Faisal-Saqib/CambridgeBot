#pragma once
// Strategy configuration. Each bot variant defines its own CFG.
#include <cambc.h>
#include <vector>

struct StratConfig {
    const char* name = "main";

    // Draft: pick the first champion in this list our team has not chosen yet.
    std::vector<cambc::champion_draft> draft_order;

    // Item builds: which emblem family shard to keep buying.
    cambc::item_family item_family = cambc::item_family::jungle;

    // Economy
    std::uint32_t tribute_min = 1;   // gems carried before heading to an altar
    float recall_frac = 0.30f;       // recall when health drops below this fraction
    bool buy_locks = true;           // buy altar locks at spawn
    bool buy_tp = false;             // buy teleport crystals at spawn

    // Map control
    bool spread = true;              // each champion farms its draft-assigned sector
    bool contest = true;             // step onto groups the enemy is capturing
    bool wards = true;               // place free wards toward objectives

    // Combat
    bool use_abilities = true;
    bool chase_enemies = false;      // leave farming to chase enemy champions
    bool group_farm = false;         // ignore sectors: team piles onto one group
    bool kite = false;               // hit-and-run high strength camps
    float engage_safety = 0.8f;      // skip fights estimated to cost more than this fraction of hp
    float flee_frac = 0.35f;         // retreat from enemy champions below this health fraction
    bool heal_shadow = true;         // healers walk to nearby hurt allies
    bool protect_carriers = true;    // carriers detour around nearby threat ranges
    unsigned shop_gold = 320;        // recall-home shopping trip threshold
};

// The concrete config lives in config.cpp so it can differ per bot.
extern const StratConfig CFG;
