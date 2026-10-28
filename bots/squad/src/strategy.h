#pragma once
// Strategy engine: sector farming, captures, tribute runs, ability use, item
// builds and light combat micro. Behaviour is tuned by StratConfig (config.h).
#include <cambc.h>
#include <algorithm>
#include <array>
#include <cfloat>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <iostream>
#include <optional>
#include <span>
#include <unordered_map>
#include <utility>
#include <variant>
#include <vector>

#include "config.h"

namespace strat {

using cambc::bitboard;
using cambc::team;
using cambc::vec2;

inline int dist(vec2 a, vec2 b) { return static_cast<int>(a.chebyshev_distance(b)); }

inline const std::array<vec2, 8>& dirs() {
    static const std::array<vec2, 8> d{ vec2::north, vec2::north_east, vec2::east, vec2::south_east,
                                        vec2::south, vec2::south_west, vec2::west, vec2::north_west };
    return d;
}

inline bitboard tiles_around(vec2 position, float radius) {
    bitboard tiles;
    tiles.clear();
    tiles.draw_chebyshev(position, radius);
    return tiles;
}

// ----------------------------- draft memory plan -----------------------------
// Layout: ['S'][ver=1][n_slots][n_groups_lo][n_groups_hi] then one byte per
// camp group (engine order) holding the owning slot index (255 = unassigned).
struct Plan {
    std::vector<std::uint8_t> group_slot;  // slot index per group (255 = none)
    int slots = 0;
    bool ok = false;
};

inline Plan read_plan() {
    Plan p;
    const auto* bytes = cambc::draft_memory.data();
    const std::size_t n = cambc::draft_memory.size();
    if (n < 5 || bytes[0] != std::byte{ 'S' } || bytes[1] != std::byte{ 1 }) return p;
    p.slots = static_cast<int>(bytes[2]);
    const std::size_t groups = static_cast<std::size_t>(bytes[3]) |
                               (static_cast<std::size_t>(bytes[4]) << 8);
    if (n < 5 + groups) return p;
    p.group_slot.assign(reinterpret_cast<const std::uint8_t*>(bytes + 5),
                        reinterpret_cast<const std::uint8_t*>(bytes + 5) + groups);
    p.ok = true;
    return p;
}

// ------------------------------ group tracking ------------------------------
enum class Observed : std::uint8_t { alive, reward, respawning, gone };

struct GroupMem {
    Observed state = Observed::alive;
    int respawn_at = -1;   // round the group is expected back
    bool seen = false;
};

// Snapshotted visible camp; all live queries resolved once per turn.
struct CampSnap {
    CampSnap(cambc::camp c) : ref(std::move(c)) {}
    cambc::camp ref;
    cambc::camp_type kind = cambc::camp_type::wolf;
    vec2 pos{ 0, 0 };
    vec2 spawn{ 0, 0 };
    float hp = 0, str = 0;
    int range = 0;
    bool asleep = false;
    std::size_t group = SIZE_MAX;
};

// Snapshotted visible enemy champion.
struct EnemySnap {
    EnemySnap(cambc::champion c) : ref(std::move(c)) {}
    cambc::champion ref;
    cambc::champion_type type = cambc::champion_type::ryth;
    vec2 pos{ 0, 0 };
    float hp = 0, maxhp = 1, str = 0;
    int range = 1;
    unsigned gems = 0;
};

// Snapshotted visible ally (excluding self for heal targeting).
struct AllySnap {
    AllySnap(cambc::champion c) : ref(std::move(c)) {}
    cambc::champion ref;
    vec2 pos{ 0, 0 };
    float hp = 0, maxhp = 1;
};

// Team channel over the engine's 8-byte shared memory — the only way to pass
// on what one champion sees. Stamps are round & 255 and ages are modular.
//   [0] squad 0 target group + 1 (0 = none)   [1] squad 0 stamp
//   [2] squad 1 target group + 1              [3] squad 1 stamp
//   [4] beacon x   [5] beacon y   [6] beacon stamp
//   [7] beacon enemy count (low 7 bits, 0 = none) | 0x80 spotter under fire
struct TeamComms {
    std::array<std::uint8_t, 8> b{};
    bool ok = false;

    static std::uint8_t now() { return static_cast<std::uint8_t>(cambc::round_number() & 0xFF); }
    static int age(std::uint8_t stamp) { return (static_cast<int>(now()) - stamp) & 0xFF; }

    void load() {
        ok = cambc::shared_memory.size() >= b.size();
        if (!ok) return;
        try {
            std::array<std::byte, 8> raw{};
            cambc::shared_memory.read(0, std::span<std::byte>(raw));
            for (std::size_t i = 0; i < b.size(); ++i) b[i] = std::to_integer<std::uint8_t>(raw[i]);
        } catch (...) { ok = false; }
    }

    void put(std::size_t off, std::initializer_list<std::uint8_t> vals) {
        if (!ok || off + vals.size() > b.size()) return;
        std::array<std::byte, 8> raw{};
        std::size_t n = 0;
        for (auto v : vals) { b[off + n] = v; raw[n++] = std::byte{ v }; }
        try { cambc::shared_memory.write(off, std::span<const std::byte>(raw.data(), n)); } catch (...) {}
    }

    // A squad leader's announced target; stale after max_age silent rounds
    // (dead, recalling, tributing) so the follower falls back to solo play.
    int squad_target(int s, int max_age) const {
        if (!ok || s < 0 || s > 1 || !b[2 * s] || age(b[2 * s + 1]) > max_age) return -1;
        return b[2 * s] - 1;
    }
    void set_squad_target(int s, int g) {   // g < 0 clears
        if (s < 0 || s > 1) return;
        put(2 * s, { static_cast<std::uint8_t>(g < 0 || g >= 255 ? 0 : g + 1), now() });
    }

    bool beacon(int max_age, vec2& p, int& count, bool& fire) const {
        if (!ok || (b[7] & 0x7F) == 0 || age(b[6]) > max_age) return false;
        p = { b[4], b[5] };
        count = b[7] & 0x7F;
        fire = (b[7] & 0x80) != 0;
        return true;
    }
    int beacon_age() const { return age(b[6]); }
    void set_beacon(vec2 p, int count, bool fire) {
        put(4, { static_cast<std::uint8_t>(p.x), static_cast<std::uint8_t>(p.y), now(),
                 static_cast<std::uint8_t>(std::clamp(count, 1, 127) | (fire ? 0x80 : 0)) });
    }
};

// Defined below; used by World::refresh.
inline bitboard blocked_tiles(const bitboard& terrain);
inline bitboard path_blockers(const bitboard& blocked);
inline bitboard static_blockers();

struct World {
    // Static map data, built once.
    std::vector<cambc::map::camp_group> groups;
    std::vector<vec2> centers;
    std::vector<bitboard> spawn_tiles;
    std::vector<std::uint8_t> my_groups;   // 1 = assigned to me
    int my_index = 0;
    int n_allies = 1;
    // Squads (CFG.rally): a tank leader paired with a damage follower. unit
    // indexes the farming unit (squad or solo champ) for sector assignment.
    enum class Role : std::uint8_t { solo, leader, follower };
    Role role = Role::solo;
    int squad = -1;                        // 0/1 for squad members
    int unit = 0, n_units = 1;
    vec2 home{ 0, 0 };                     // allied spawn centroid
    bitboard terrain;                      // walls|holes|altars|enemy spawn — never changes
    bitboard home_reach;                   // tiles reachable from home on foot (static)
    std::vector<float> group_hp;           // total member health per group (static)
    std::vector<float> group_str;          // total member strength per group (static)
    std::vector<int>   group_home_d;       // chebyshev home -> nearest spawn tile (static)
    std::vector<int16_t> tile_group;       // w*h flat map: tile -> group index, -1 none (static)
    std::vector<int> group_gems;           // static reward values
    std::vector<int> group_gold;
    std::vector<int> group_range;          // longest member attack range (static)
    TeamComms comms;                       // shared-memory channel, reloaded each turn

    // Walkable-component graph: holes/walls split the map into regions that
    // only dashes or teleport crystals can cross. comp_hop[a][b] holds the
    // launch tiles in a and landing tiles in b for a TP jump; next_hop is the
    // first-hop routing table over the jump graph (multi-island paths).
    std::vector<int16_t> tile_comp;        // w*h flat map: tile -> component, -1 unwalkable
    std::vector<bitboard> comp_tiles;
    std::vector<int> group_comp;           // group -> component index
    struct Hop { bitboard launch; bitboard land; };
    std::vector<std::unordered_map<int, Hop>> comp_hop;
    std::vector<std::vector<int>> next_hop;
    std::vector<char> comp_altar;          // component has a usable altar
    int home_comp = -1;
    int cur_comp = 0;                      // this champ's component this turn
    bool has_tp = false;                   // carrying an unused teleport crystal
    Plan plan;

    // Per-turn dynamic data.
    std::vector<GroupMem> gmem;            // indexed by group index
    bitboard visible;
    std::vector<CampSnap> camps;
    std::vector<EnemySnap> enemies;
    std::vector<AllySnap> allies_seen;
    bitboard enemy_locks;
    bitboard ally_locks;
    bitboard blocked;              // walk-blocked tiles this turn
    bitboard danger;               // attack ranges of awake camps + visible enemies

    World() { init(); }

    void init() {
        groups = cambc::map::camp_groups();
        centers.reserve(groups.size());
        spawn_tiles.reserve(groups.size());
        for (auto& g : groups) {
            auto tiles = g.spawn_tiles();
            auto pos = tiles.positions();
            vec2 c{ 0, 0 };
            for (auto p : pos) c = c + p;
            c = { c.x / std::max<int>(1, pos.size()), c.y / std::max<int>(1, pos.size()) };
            centers.push_back(c);
            spawn_tiles.push_back(tiles);
        }
        // Flat tile->group lookup: O(1) membership instead of bitboard scans.
        tile_group.assign(cambc::map::width() * cambc::map::height(), -1);
        for (std::size_t i = 0; i < groups.size(); ++i)
            for (auto t : spawn_tiles[i].positions())
                if (cambc::map::is_in_bounds(t))
                    tile_group[t.y * cambc::map::width() + t.x] = static_cast<int16_t>(i);
        gmem.assign(groups.size(), GroupMem{});
        plan = read_plan();
        // My slot index: rank of my handle among allied handles.
        auto allies = cambc::champions(team::ally);
        std::vector<std::uint32_t> handles;
        for (auto& c : allies)
            handles.push_back(static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(c)));
        std::sort(handles.begin(), handles.end());
        const auto mine = static_cast<std::uint32_t>(
            static_cast<cambc::handle_champion_t>(cambc::self()));
        for (std::size_t i = 0; i < handles.size(); ++i)
            if (handles[i] == mine) my_index = static_cast<int>(i);
        n_allies = std::max<int>(1, handles.size());
        if (CFG.rally) assign_squads(handles, mine);

        {
            const auto spawn = cambc::map::spawn_region(team::ally).positions();
            vec2 h{ 0, 0 };
            for (auto p : spawn) h = h + p;
            if (!spawn.empty()) home = { h.x / static_cast<int>(spawn.size()),
                                        h.y / static_cast<int>(spawn.size()) };
        }

        // Static terrain + one BFS from home: everything a walk can ever
        // reach. Per-turn reach checks become bitboard membership tests.
        terrain = static_blockers();
        {
            cambc::distance_field f;
            bitboard roots;
            roots.clear();
            roots.set(home);
            f.compute(terrain, roots, home_reach);  // visited = reachable set
        }
        group_hp.assign(groups.size(), 0.f);
        group_str.assign(groups.size(), 0.f);
        group_home_d.assign(groups.size(), 0);
        group_range.assign(groups.size(), 0);
        for (std::size_t i = 0; i < groups.size(); ++i) {
            for (auto& member : groups[i].camps()) {
                const auto bs = member.base_stats();
                group_hp[i] += bs.base_health;
                if (bs.base_strength > 0 && bs.base_attack_range > 0) {
                    group_str[i] += bs.base_strength;
                    group_range[i] = std::max(group_range[i],
                                              static_cast<int>(bs.base_attack_range));
                }
            }
            int hd = INT32_MAX;
            for (auto t : spawn_tiles[i].positions())
                hd = std::min(hd, dist(home, t));
            group_home_d[i] = hd;
        }
        group_gems.resize(groups.size());
        group_gold.resize(groups.size());
        for (std::size_t i = 0; i < groups.size(); ++i) {
            group_gems[i] = groups[i].gem_value();
            group_gold[i] = groups[i].gold_value();
        }

        // Farm in pairs: consecutive allies share a sector so hard groups get
        // focus fire (a solo champ just dies to the big guards repeatedly).
        // With squads, each farming unit (squad or solo champ) owns a sector.
        const int n_pairs = CFG.rally ? n_units : std::max(1, (n_allies + 1) / 2);
        const int my_pair = CFG.rally ? unit : std::min(my_index / 2, n_pairs - 1);
        my_groups.assign(groups.size(), 0);
        for (std::size_t i = 0; i < groups.size(); ++i) {
            int slot = -1;
            if (plan.ok && i < plan.group_slot.size() && plan.group_slot[i] != 255)
                slot = plan.group_slot[i];
            else
                slot = static_cast<int>(i) % n_allies;  // deterministic fallback spread
            my_groups[i] = (slot % n_pairs == my_pair) ? 1 : 0;
        }

        // Connected components of walkable terrain (8-dir flood fill) and the
        // TP-jump edges between them (landing must be an open tile within 3).
        {
            const int MW = cambc::map::width(), MH = cambc::map::height();
            tile_comp.assign(MW * MH, -1);
            std::vector<vec2> stack;
            for (int y = 0; y < MH; ++y) for (int x = 0; x < MW; ++x) {
                const vec2 t{ x, y };
                if (terrain.is_set(t) || tile_comp[y * MW + x] >= 0) continue;
                const int c = static_cast<int>(comp_tiles.size());
                comp_tiles.emplace_back();
                comp_tiles.back().clear();
                tile_comp[y * MW + x] = static_cast<int16_t>(c);
                stack.push_back(t);
                while (!stack.empty()) {
                    const vec2 p = stack.back(); stack.pop_back();
                    comp_tiles[c].set(p);
                    for (int dy = -1; dy <= 1; ++dy)
                        for (int dx = -1; dx <= 1; ++dx) {
                            if (!dx && !dy) continue;
                            const vec2 q{ p.x + dx, p.y + dy };
                            if (!cambc::map::is_in_bounds(q) || terrain.is_set(q)) continue;
                            const int qi = q.y * MW + q.x;
                            if (tile_comp[qi] >= 0) continue;
                            tile_comp[qi] = static_cast<int16_t>(c);
                            stack.push_back(q);
                        }
                }
            }
            home_comp = comp_at(home);
            group_comp.assign(groups.size(), -1);
            for (std::size_t i = 0; i < groups.size(); ++i)
                for (auto t : spawn_tiles[i].positions())
                    if (comp_at(t) >= 0) { group_comp[i] = comp_at(t); break; }
        }
        // Jump edges: for each comp, tiles within 3 of a foreign walkable tile
        // are launchpads. Dilate the foreign set 3x then intersect our tiles.
        {
            const int nc = static_cast<int>(comp_tiles.size());
            bitboard walk; walk.clear();
            for (auto& c : comp_tiles) walk |= c;
            auto dil1 = [](const bitboard& b) {
                auto r = b | b.shift_right(1) | b.shift_right(-1);
                return r | r.shift_up(1) | r.shift_up(-1);
            };
            comp_hop.resize(nc);
            for (int a = 0; a < nc; ++a) {
                bitboard foreign = walk & ~comp_tiles[a];
                if (foreign.is_empty()) continue;
                bitboard zone = foreign;
                for (int k = 0; k < 3; ++k) zone |= dil1(zone);
                zone &= comp_tiles[a];
                for (auto t : zone.positions())
                    for (int dy = -3; dy <= 3; ++dy)
                        for (int dx = -3; dx <= 3; ++dx) {
                            if (!dx && !dy) continue;
                            const vec2 u{ t.x + dx, t.y + dy };
                            if (!cambc::map::is_in_bounds(u)) continue;
                            const int b = comp_at(u);
                            if (b < 0 || b == a) continue;
                            auto& h = comp_hop[a][b];
                            h.launch.set(t); h.land.set(u);
                        }
            }
            // First-hop routing table via BFS over the jump graph.
            next_hop.assign(nc, std::vector<int>(nc, -1));
            for (int s = 0; s < nc; ++s) {
                std::vector<int> order{ s };
                std::vector<char> vis(nc, 0); vis[s] = 1; next_hop[s][s] = s;
                for (std::size_t qi = 0; qi < order.size(); ++qi) {
                    const int c = order[qi];
                    for (auto& kv : comp_hop[c]) {
                        const int b = kv.first;
                        if (vis[b]) continue;
                        vis[b] = 1;
                        next_hop[s][b] = (c == s) ? b : next_hop[s][c];
                        order.push_back(b);
                    }
                }
            }
            // Which components have a usable altar (altar tiles are terrain —
            // usable when a walkable neighbour sits in this component).
            comp_altar.assign(nc, 0);
            for (auto a : cambc::map::altars().positions())
                for (int dy = -1; dy <= 1; ++dy)
                    for (int dx = -1; dx <= 1; ++dx) {
                        const int c = comp_at({ a.x + dx, a.y + dy });
                        if (c >= 0) comp_altar[c] = 1;
                    }
        }

        // one-time map dump
        if (my_index == 0) {
            std::cout << "MAP " << cambc::map::width() << "x" << cambc::map::height() << std::endl;
            std::cout << "spawn:";
            for (auto t : cambc::map::spawn_region(team::ally).positions())
                std::cout << " " << cambc::to_string(t);
            std::cout << std::endl;
            std::cout << "altars:";
            for (auto t : cambc::map::altars().positions())
                std::cout << " " << cambc::to_string(t);
            std::cout << std::endl;
            for (std::size_t i = 0; i < groups.size(); ++i) {
                std::cout << "grp" << i << " c=" << cambc::to_string(centers[i])
                          << " gems=" << groups[i].gem_value() << " gold=" << groups[i].gold_value()
                          << " spawns:";
                for (auto t : spawn_tiles[i].positions()) std::cout << " " << cambc::to_string(t);
                std::cout << " camps:";
                for (auto& m : groups[i].camps()) {
                    auto bs = m.base_stats();
                    std::cout << " [" << (int)m.kind() << "@" << cambc::to_string(m.spawn_position())
                              << " hp" << bs.base_health << " s" << bs.base_strength
                              << " r" << bs.base_attack_range << "]";
                }
                std::cout << std::endl;
            }
            // ASCII map: # wall, ~ hole, A altar, S spawn, e enemy spawn, . open
            {
                const auto walls = cambc::map::walls();
                const auto holes = cambc::map::holes();
                const auto altars = cambc::map::altars();
                const auto sA = cambc::map::spawn_region(team::ally);
                const auto sE = cambc::map::spawn_region(team::enemy);
                bitboard gsp; gsp.clear();
                for (auto& s : spawn_tiles) gsp |= s;
                for (int y = 0; y < cambc::map::height(); y += 2) {
                    std::string row;
                    for (int x = 0; x < cambc::map::width(); ++x) {
                        vec2 t{ x, y };
                        row += walls.is_set(t) ? '#' : holes.is_set(t) ? '~'
                             : altars.is_set(t) ? 'A' : sA.is_set(t) ? 'S'
                             : sE.is_set(t) ? 'e' : gsp.is_set(t) ? 'g' : '.';
                    }
                    std::cout << row << std::endl;
                }
            }
        }
    }

    // Pair each tank (leader) with a damage dealer (follower) by champion type,
    // at most two squads; everyone else farms solo. Every ally stands on the
    // spawn at init, so all bots see the same roster and agree on the pairing.
    void assign_squads(const std::vector<std::uint32_t>& handles, std::uint32_t mine) {
        using ct = cambc::champion_type;
        static constexpr std::array<ct, 5> tanks{ ct::ryth, ct::marcella, ct::heart_of_ruin, ct::varg, ct::ren };
        static constexpr std::array<ct, 7> dps{ ct::vendetta, ct::vesper_vale, ct::tavi, ct::issac,
                                                ct::cassi, ct::stellar, ct::prism };
        std::vector<std::pair<std::uint32_t, ct>> roster;
        try { roster.emplace_back(mine, cambc::self().champion_name()); } catch (...) { return; }
        for (auto& c : cambc::vision::champions(team::ally)) {
            const auto h = static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(c));
            if (h == mine) continue;
            try { roster.emplace_back(h, c.champion_name()); } catch (...) {}
        }
        if (roster.size() != handles.size()) return;   // someone unseen: stay solo
        auto pick = [&](auto& order, std::vector<std::uint32_t>& out) {
            for (auto t : order)
                for (auto& [h, ty] : roster)
                    if (ty == t) out.push_back(h);
        };
        std::vector<std::uint32_t> lead, follow;
        pick(tanks, lead);
        pick(dps, follow);
        const int pairs = std::min<int>({ 2, static_cast<int>(lead.size()), static_cast<int>(follow.size()) });
        std::vector<std::uint32_t> solos;
        for (auto h : handles) {
            const bool paired =
                std::find(lead.begin(), lead.begin() + pairs, h) != lead.begin() + pairs
                || std::find(follow.begin(), follow.begin() + pairs, h) != follow.begin() + pairs;
            if (!paired) solos.push_back(h);
        }
        n_units = pairs + static_cast<int>(solos.size());
        for (int p = 0; p < pairs; ++p) {
            if (lead[p] == mine) { role = Role::leader; squad = p; unit = p; }
            if (follow[p] == mine) { role = Role::follower; squad = p; unit = p; }
        }
        for (std::size_t k = 0; k < solos.size(); ++k)
            if (solos[k] == mine) unit = pairs + static_cast<int>(k);
        n_units = std::max(1, n_units);
    }

    // O(1) group membership via the static tile map.
    int group_at(vec2 t) const {
        if (!cambc::map::is_in_bounds(t)) return -1;
        return tile_group[t.y * cambc::map::width() + t.x];
    }

    // O(1) component membership via the static tile map.
    int comp_at(vec2 t) const {
        if (!cambc::map::is_in_bounds(t)) return -1;
        return tile_comp[t.y * cambc::map::width() + t.x];
    }

    void refresh() {
        if (CFG.rally || CFG.beacon) comms.load();
        visible = cambc::vision::visible_tiles();
        enemy_locks = cambc::vision::altar_lock_tiles(team::enemy);
        ally_locks = cambc::vision::altar_lock_tiles(team::ally);

        // Snapshot visible camps; live queries are guarded because dead or
        // freshly hidden camps throw engine errors.
        camps.clear();
        for (auto& c : cambc::vision::camps()) {
            CampSnap s{ c };
            s.kind = c.kind();
            s.spawn = c.spawn_position();
            try {
                s.pos = c.position();
                s.hp = c.health();
                s.str = c.strength();
                s.range = c.attack_range();
                s.asleep = c.is_asleep();
                if (!c.is_alive()) continue;
            } catch (...) { continue; }
            camps.push_back(s);
        }
        // Map member camps to their group index for focus targeting.
        for (auto& s : camps) s.group = group_at(s.spawn);

        enemies.clear();
        for (auto& c : cambc::vision::champions(team::enemy)) {
            EnemySnap s{ c };
            try {
                if (!c.is_alive() || !c.is_visible()) continue;
                s.pos = c.position();
                s.hp = c.health();
                s.maxhp = std::max(1.f, c.max_health());
                s.str = c.strength();
                s.range = c.attack_range();
                s.type = c.champion_name();
                try { s.gems = c.gem_count(); } catch (...) {}
            } catch (...) { continue; }
            enemies.push_back(s);
        }

        const auto self_handle = static_cast<cambc::handle_champion_t>(cambc::self());
        allies_seen.clear();
        for (auto& c : cambc::vision::champions(team::ally)) {
            if (static_cast<cambc::handle_champion_t>(c) == self_handle) continue;
            AllySnap s{ c };
            try {
                if (!c.is_alive() || !c.is_visible()) continue;
                s.pos = c.position();
                s.hp = c.health();
                s.maxhp = std::max(1.f, c.max_health());
            } catch (...) { continue; }
            allies_seen.push_back(s);
        }

        const int round = static_cast<int>(cambc::round_number());
        // Stagger group polls: an engine state() call per visible group per
        // turn burns a third of the fuel budget on big maps. Each group is
        // re-observed every 4 rounds; capture progress is queried live anyway.
        for (std::size_t i = 0; i < groups.size(); ++i) {
            auto& m = gmem[i];
            // Reawaken groups whose respawn timer has expired.
            if (m.state == Observed::respawning && m.respawn_at >= 0 && round >= m.respawn_at)
                m.state = Observed::alive;
            if (((round + static_cast<int>(i)) & 3) != 0) continue;  // staggered polls
            const bool seen = !(spawn_tiles[i] & visible).is_empty();
            if (seen) {
                try {
                    auto s = groups[i].state();
                    if (std::holds_alternative<cambc::map::camp_group_alive>(s)) {
                        m.state = Observed::alive;
                    } else if (std::holds_alternative<cambc::map::camp_group_reward_available>(s)) {
                        m.state = Observed::reward;
                    } else {
                        auto& r = std::get<cambc::map::camp_group_respawning>(s);
                        m.state = Observed::respawning;
                        m.respawn_at = round + r.timer;
                    }
                    m.seen = true;
                } catch (...) {
                }
            }
            // A group we saw cleared that now shows live camps again.
            if (m.state != Observed::alive && seen)
                for (auto& s : camps)
                    if (s.group == i) { m.state = Observed::alive; break; }
        }

        // Walk-blocked tiles this turn (static terrain + visible units).
        blocked = blocked_tiles(terrain);
        const auto self_pos = cambc::self().position();
        cur_comp = comp_at(self_pos);
        try {
            has_tp = cambc::self().consumables()
                [cambc::consumable_type::tp_crystal].count() > 0;
        } catch (...) { has_tp = false; }

        // Danger zone: attack ranges of things that can actually reach this
        // champ soon — nearby awake camps and nearby visible enemies. Carriers
        // and fleeing champs route around them (a death dumps the haul).
        // Sleeping camps are excluded: they only fight back once struck.
        danger.clear();
        for (auto& s : camps)
            if (!s.asleep && s.str > 0 && dist(s.pos, self_pos) <= 12)
                danger |= tiles_around(s.pos, s.range);
        for (auto& s : enemies)
            if (s.str > 0 && dist(s.pos, self_pos) <= 8)
                danger |= tiles_around(s.pos, s.range);
        // A hunter a teammate spotted moments ago still threatens carriers
        // walking past it, even though we can't see it ourselves.
        if (CFG.beacon && enemies.empty()) {
            vec2 bp; int bc = 0; bool bf = false;
            if (comms.beacon(4, bp, bc, bf) && dist(bp, self_pos) <= 14)
                danger |= tiles_around(bp, 4);
        }
    }

    bool group_farmable(std::size_t i) const {
        return gmem[i].state == Observed::alive;
    }

    bool group_reachable(std::size_t i) const {
        const int gc = group_comp[i];
        if (gc < 0 || cur_comp < 0) return false;
        if (gc == cur_comp) return true;              // same component: walkable
        return next_hop[cur_comp][gc] >= 0;           // reachable via TP jumps
    }

    // Terrain reachability only: units move, so a camp plugging a corridor
    // must not flip the answer turn to turn.
    bool goals_reachable(const bitboard& goals) const {
        const auto pos = cambc::self().position();
        for (auto t : goals.positions())
            if (t == pos || comp_at(t) == cur_comp) return true;
        return false;
    }

    bool group_has_member_camp(std::size_t i) const {
        for (auto& s : camps)
            if (s.group == i) return true;
        return false;
    }

    bool group_has_reward(std::size_t i) const {
        return gmem[i].state == Observed::reward;
    }
};

// ------------------------------ small helpers -------------------------------

// Stat each champion wants from shards. Basic attacks fire every round and
// scale with strength, so almost every farmer wants strength; only the pure
// nuke casters (low strength growth, high focus scaling) prefer focus.
inline cambc::item_stat stat_for(cambc::champion_type t) {
    switch (t) {
    case cambc::champion_type::stellar:
    case cambc::champion_type::prism:
    case cambc::champion_type::cassi:       return cambc::item_stat::focus;
    default:                               return cambc::item_stat::strength;
    }
}

// Tiles blocked for walking, from what we can currently see. Terrain masks are
// supplied by the caller (they never change) so we only pay for the dynamic
// vision unions.
inline bitboard blocked_tiles(const bitboard& terrain) {
    auto blocked = terrain | cambc::vision::champion_tiles()
        | cambc::vision::camp_tiles() | cambc::vision::teleport_tiles();
    blocked.set(cambc::self().position(), false);
    return blocked;
}

// Pathfinding walls: like blocked_tiles but allied champions are passable —
// they move away on their own turns, so routing through them is fine and
// avoids permanent gridlock in spawn clusters.
inline bitboard path_blockers(const bitboard& blocked) {
    auto w = blocked;
    w &= ~cambc::vision::champion_tiles(team::ally);
    return w;
}

// Terrain-only walls for reachability queries: camps and champions MOVE, so a
// camp plugging a 1-tile chamber door must not make its group "unreachable" —
// we can walk to the door and fight it.
inline bitboard static_blockers() {
    return cambc::map::walls() | cambc::map::holes() | cambc::map::altars()
        | cambc::map::spawn_region(team::enemy);
}

// Step toward the closest tile in `goals`; returns true if we moved or are
// already standing on a goal tile. Tries a cheap greedy step first and only
// pays for a BFS field when greedy can't improve. `use_field` latches true
// once the field has been needed: greedy and BFS disagree in walled pockets
// (greedy walks in, BFS walks out) and ping-pong forever without the latch.
inline bool move_toward_goals(const bitboard& blocked, bitboard goals, bool& use_field) {
    auto& me = cambc::self();
    if (!me.can_move()) return false;
    if (goals.is_set(me.position())) return true;

    goals &= ~blocked | cambc::vision::camp_tiles();
    if (goals.is_empty()) return false;

    const auto path_walls = path_blockers(blocked);
    const auto allies = cambc::vision::champion_tiles(team::ally);
    const auto speed = static_cast<std::uint16_t>(
        std::max(1, me.base_stats().base_move_speed));
    const auto reach_tiles = path_walls.reachable_tiles(me.position(), speed).positions();

    if (!use_field) {
        // Greedy pass: chebyshev distance to the goal set — zero BFS cost and
        // right on open maps, which is most of the walking we do.
        const auto goal_tiles = goals.positions();
        const auto cheb = [&](vec2 t) {
            int d = INT32_MAX;
            for (auto g : goal_tiles) d = std::min(d, dist(t, g));
            return d;
        };
        const int d_here = cheb(me.position());
        std::vector<std::pair<int, vec2>> steps;
        for (auto tile : reach_tiles) {
            const int d = cheb(tile);
            if (d >= d_here) continue;
            steps.emplace_back(d * 4 + (allies.is_set(tile) ? 3 : 0), tile);
        }
        std::sort(steps.begin(), steps.end());
        for (auto& [d, tile] : steps) {
            try {
                if (me.move_absolute(tile)) return true;
            } catch (...) {}
        }
        use_field = true;  // greedy exhausted — take field steps until objective changes
    }

    cambc::distance_field field;
    cambc::bitboard visited;
    field.compute_to(path_walls & ~goals, goals, tiles_around(me.position(), 0), visited);
    if (field.get(me.position()) == cambc::distance_field::unreachable) return false;

    std::vector<std::pair<int, vec2>> steps;
    const int f_here = field.get(me.position());
    for (auto tile : reach_tiles) {
        const int d = field.get(tile);
        if (d >= f_here) continue;
        steps.emplace_back(d * 4 + (allies.is_set(tile) ? 3 : 0), tile);
    }
    std::sort(steps.begin(), steps.end());
    for (auto& [d, tile] : steps) {
        try {
            if (me.move_absolute(tile)) return true;
        } catch (...) {
            // Stale snapshot: an ally moved onto this tile after our vision
            // query. Engine throws for known-occupied tiles; try the next.
        }
    }
    return false;
}

// Step directly away from a threat tile (used for kiting / fleeing).
inline bool step_away_from(const bitboard& blocked, vec2 threat) {
    auto& me = cambc::self();
    if (!me.can_move()) return false;
    const int here = dist(me.position(), threat);
    const auto speed = static_cast<std::uint16_t>(
        std::max(1, me.base_stats().base_move_speed));
    std::vector<std::pair<int, vec2>> steps;
    for (auto tile : blocked.reachable_tiles(me.position(), speed).positions())
        if (dist(tile, threat) > here) steps.emplace_back(dist(tile, threat), tile);
    std::sort(steps.begin(), steps.end(), [](auto& a, auto& b) { return a.first > b.first; });
    for (auto& [d, tile] : steps) {
        try {
            if (me.move_absolute(tile)) return true;
        } catch (...) {}
    }
    return false;
}

inline float group_total_strength(const cambc::map::camp_group& g) {
    float total = 0;
    for (auto& member : g.camps()) {
        float str = member.base_stats().base_strength;
        float range = static_cast<float>(member.base_stats().base_attack_range);
        // Only count members that could hit us while we attack them.
        if (str > 0 && range > 0) total += str;
    }
    return total;
}

inline float group_total_health(const cambc::map::camp_group& g) {
    float total = 0;
    for (auto& member : g.camps()) total += member.base_stats().base_health;
    return total;
}

// True when the champion carries a heal ability (Willow-style support).
inline bool has_heal(cambc::champion& me) {
    for (auto& ab : me.abilities())
        if (auto info = ab.info())
            if (std::holds_alternative<cambc::ability_heal>(*info)) return true;
    return false;
}

// ------------------------------- the bot ------------------------------------
class Engine {
public:
    void play() {
        auto& me = cambc::self();

        if (!world_) {
            try { world_.emplace(); }
            catch (const std::exception& e) {
                std::cout << "world init failed: " << e.what() << std::endl;
                throw;
            }
            blocked_until_.assign(world_->groups.size(), -1);
        }

        // Dead champions still get shop turns.
        if (!me.is_alive()) {
            phase_ = "dead";
            // Died attacking a group with no enemy in sight: blacklist it —
            // camps stay lethal (lost_world's monolith camped its approaches
            // and killed us in a loop). Skip when enemies were visible: a
            // hunter killing us near a group shouldn't surrender it to them.
            if (!was_dead_ && dbg_group_ != SIZE_MAX
                && dbg_group_ < blocked_until_.size()
                && world_->enemies.empty())
                blocked_until_[dbg_group_] = cambc::round_number() + 80;
            if (!was_dead_ && dbg_last_gems_ > 0)
                std::cout << "  i" << (world_ ? world_->my_index : -1)
                          << " DIED carrying " << dbg_last_gems_ << " gems" << std::endl;
            was_dead_ = true;
            buy_all();
            return;
        }
        was_dead_ = false;
        dbg_last_gems_ = me.gem_count();
        // Let channels run: recall, tribute and teleport resolve on their own.
        if (me.is_recalling() || me.is_submitting_gems() || me.is_teleporting()) { phase_ = "channel"; return; }

        const auto fuel0 = cambc::fuel_remaining();
        try {
            phase_ = "refresh";   world_->refresh();
        if (cambc::round_number() % 50 == 0)
            std::cout << "i" << world_->my_index << " r" << cambc::round_number()
                      << " fuelStart=" << fuel0 << " afterRefresh=" << cambc::fuel_remaining() << std::endl;
        if (cambc::round_number() < 15 || cambc::round_number() % 100 == 0) {
            std::cout << "i" << world_->my_index << " r" << cambc::round_number()
                      << " camps=" << world_->camps.size() << " enemies=" << world_->enemies.size()
                      << " groups=" << world_->groups.size() << " states:";
            for (std::size_t gi = 0; gi < world_->groups.size(); ++gi) {
                auto st = world_->gmem[gi].state;
                std::cout << (st == strat::Observed::alive ? 'a' : st == strat::Observed::reward ? 'R' : st == strat::Observed::respawning ? 's' : 'g');
            }
            std::cout << std::endl;
        }
            phase_ = "turn";      play_turn_impl(me);
        } catch (const std::exception& e) {
            std::cout << "phase " << phase_ << " failed: " << e.what() << std::endl;
            throw;
        }
        if ((world_->my_index == 0 && cambc::round_number() < 250)
            || cambc::round_number() < 15 || cambc::round_number() % 100 == 0)
            std::cout << "i" << world_->my_index << " r" << cambc::round_number()
                      << " pos=" << cambc::to_string(me.position())
                      << " hp=" << me.health() << " gems=" << me.gem_count()
                      << " kind=" << dbg_kind_ << " grp=" << (dbg_group_ == SIZE_MAX ? -1 : (int)dbg_group_)
                      << " stay=" << dbg_stay_ << " ng=" << dbg_goals_
                      << " cm=" << dbg_cm_ << " ca=" << dbg_ca_
                      << " stg=" << dbg_stage_turns_ << "/" << dbg_rally_calls_
                      << "/" << dbg_rally_quits_
                      << " fuelEnd=" << cambc::fuel_remaining()
                      << " exit=" << phase_ << std::endl;
    }

private:
    const char* phase_ = "init";
    int dbg_kind_ = -1;
    std::size_t dbg_group_ = SIZE_MAX;
    bool dbg_stay_ = false;
    std::size_t dbg_goals_ = 0;
    bool dbg_cm_ = false, dbg_ca_ = false;
    int dbg_last_gems_ = 0;
    bool was_dead_ = false;

    // Objective hysteresis (see choose_objective).
    std::size_t sticky_group_ = SIZE_MAX;

    // Fleeing-camp stall detection (see choose_objective).
    std::size_t chase_group_ = SIZE_MAX;
    int chase_stall_ = 0;
    int chase_best_ = INT32_MAX;
    std::vector<int> blocked_until_;       // group index -> round unblocked

    // Movement routing mode (see move_toward_goals): once the BFS field has
    // been needed for the current objective, keep using it — greedy and field
    // steps disagree in walled pockets and oscillate without the latch.
    bool route_field_ = false;
    std::size_t route_group_ = SIZE_MAX;
    float last_hp_ = -1.f;

    // Squad bookkeeping (see squad_gate / the leader announcement).
    std::size_t stage_group_ = SIZE_MAX;
    int stage_since_ = 0;
    int last_stage_round_ = -10;
    std::size_t announced_ = SIZE_MAX;     // leader: group announced to the follower
    std::size_t engage_group_ = SIZE_MAX;  // squad fight we committed to (no re-staging)
    int dbg_stage_turns_ = 0, dbg_rally_calls_ = 0, dbg_rally_quits_ = 0;

    void play_turn_impl(cambc::champion& me) {
        phase_ = "state";

        const auto st = me.state();
        if (!st.contains(cambc::champion_state::can_move)
            && !st.contains(cambc::champion_state::can_attack)
            && !st.contains(cambc::champion_state::can_cast)) { phase_ = "noactions"; return; }

        const vec2 pos = me.position();
        const bool on_spawn = cambc::map::spawn_region(team::ally).is_set(pos);

        if (on_spawn) {
            phase_ = "spawn";
            buy_all();
            // Resting one turn-end on spawn heals to full; stay if damaged.
            if (me.health() < me.max_health() * 0.97f) { phase_ = "rest"; return; }
        }

        // Tavi's passive lets her shop anywhere — idle gold compounds nowhere,
        // so buy shards in the field the moment one is affordable.
        if (me.champion_name() == cambc::champion_type::tavi) buy_all();

        // Emergency recall when badly hurt away from base — only while
        // carrying gems. A dying farmer just keeps chipping; camps stay
        // damaged and a fresh body walks back faster than a recall heals.
        // The more gems we carry the earlier we bail: a death dumps them all.
        // Recall is cancelled by ANY damage — never channel it while an
        // enemy or awake camp is in range; keep walking instead.
        const float carry_frac = me.gem_count() >= 10 ? 0.5f : CFG.recall_frac;
        if (!on_spawn && me.gem_count() > 0 && me.health() < me.max_health() * carry_frac
            && incoming_threat() <= 0.f) {
            phase_ = "recall";
            try { me.recall(); } catch (...) {}
            go_home();
            return;
        }

        // Shopping trip: idle gold does nothing — strong opponents convert
        // nearly all of it into shards. When holding real money with empty
        // hands and nothing in range to threaten the channel, recall home,
        // heal, buy, and walk back out.
        if (!on_spawn && me.gem_count() == 0 && me.gold_count() >= CFG.shop_gold
            && incoming_threat() <= 0.f && world_->enemies.empty()) {
            phase_ = "shop_recall";
            try { me.recall(); } catch (...) {}
            go_home();
            return;
        }

        // Start a tribute immediately when carrying enough gems at an altar.
        phase_ = "submit_now";
        if (me.gem_count() >= CFG.tribute_min && try_submit_now()) return;

        // Objective selection.
        phase_ = "objective";
        Objective obj = choose_objective();
        // Leader moved on (tribute, flee, capture, cheap group): withdraw the
        // announcement so the follower goes back to solo farming.
        if (announced_ != SIZE_MAX && !(obj.kind == ObjKind::Farm && obj.group == announced_)) {
            world_->comms.set_squad_target(world_->squad, -1);
            announced_ = SIZE_MAX;
        }
        if (obj.group != engage_group_) engage_group_ = SIZE_MAX;
        dbg_kind_ = static_cast<int>(obj.kind);
        dbg_group_ = obj.group;
        dbg_stay_ = obj.stay;
        dbg_goals_ = obj.goals.positions().size();
        dbg_cm_ = me.can_move(); dbg_ca_ = me.can_attack();
        if (obj.staging) ++dbg_stage_turns_;

        // Each phase runs under its own guard: a stale handle or an invalid
        // target must not eat the rest of the turn.
        auto guard = [&](const char* name, auto fn) {
            phase_ = name;
            try { fn(); }
            catch (const std::exception& e) {
                if (cambc::round_number() % 100 == 0)
                    std::cout << "  i" << world_->my_index << " " << name
                              << " err: " << e.what() << std::endl;
            }
        };

        // Abilities (at most one cast): pick the best non-reset spell.
        if (CFG.use_abilities) guard("cast", [&] { cast_best(obj); });

        // Fight: hit the best target in range, then spend attack resets.
        bool attacked = false;
        guard("attack", [&] {
            attacked = attack_best(obj);
            if (attacked) spend_resets(obj);
        });

        // Move toward the objective if we still can.
        guard("move", [&] {
            if (!me.can_move()) return;
            if (obj.stay) {
                // Holding a capture tile: nothing to do.
            } else if (obj.flee) {
                // Teleport crystal beats recall under fire: damage does not
                // cancel the channel and the blink ignores walls, so a hunter
                // cannot body-block the escape. Blink toward home and away
                // from the nearest enemy, then keep walking.
                auto& tps = me.consumables()[cambc::consumable_type::tp_crystal];
                if (tps.count() > 0 && !world_->enemies.empty()) {
                    const auto spawn = cambc::map::spawn_region(team::ally);
                    vec2 home = spawn.positions().front();
                    int hd = INT32_MAX;
                    for (auto t : spawn.positions())
                        if (dist(t, pos) < hd) { hd = dist(t, pos); home = t; }
                    vec2 best_tile = pos; float best_key = -FLT_MAX;
                    for (int dy = -3; dy <= 3; ++dy)
                        for (int dx = -3; dx <= 3; ++dx) {
                            if (!dx && !dy) continue;
                            const vec2 t{ pos.x + dx, pos.y + dy };
                            if (!cambc::map::is_in_bounds(t) || world_->blocked.is_set(t)) continue;
                            int nearest = INT32_MAX;
                            for (auto& e : world_->enemies)
                                nearest = std::min(nearest, dist(t, e.pos));
                            if (nearest == INT32_MAX) continue;
                            const float key = nearest * 2.f - dist(t, home);
                            if (key > best_key) { best_key = key; best_tile = t; }
                        }
                    if (best_tile != pos)
                        try { if (tps.use(best_tile)) return; } catch (...) {}
                }
                bitboard goals = cambc::map::spawn_region(team::ally);
                // Safety in numbers: also accept tiles next to visible allies.
                for (auto& a : world_->allies_seen)
                    goals |= tiles_around(a.pos, 2);
                goals.set(me.position(), false);
                bitboard walls = world_->blocked;
                if (obj.protect) walls |= world_->danger;
                bool fld = false;
                if (!move_toward_goals(walls, goals, fld))
                    go_home();
            } else if (obj.kind == ObjKind::Jump) {
                // On a launchpad: channel the crystal to the landing tile
                // nearest our final target. Otherwise keep walking to one.
                if (obj.goals.is_set(pos)) {
                    auto& tps = me.consumables()[cambc::consumable_type::tp_crystal];
                    if (tps.count() > 0) {
                        std::vector<vec2> cands;
                        for (auto t : obj.land.positions())
                            if (dist(t, pos) <= 3 && !world_->blocked.is_set(t))
                                cands.push_back(t);
                        std::sort(cands.begin(), cands.end(), [&](vec2 a, vec2 b) {
                            return dist(a, obj.jump_dest) < dist(b, obj.jump_dest); });
                        for (auto t : cands) {
                            try { if (tps.use(t)) break; } catch (...) {}
                            if (me.is_teleporting()) break;
                        }
                    }
                }
                if (!me.is_teleporting())
                    move_toward_goals(world_->blocked, obj.goals, route_field_);
            } else if (!obj.goals.is_empty()) {
                if (obj.group != route_group_) { route_group_ = obj.group; route_field_ = false; }
                bitboard walls = world_->blocked;
                if (obj.protect) walls |= world_->danger;
                if (!move_toward_goals(walls, obj.goals, route_field_) && obj.protect)
                    move_toward_goals(world_->blocked, obj.goals, route_field_);
                // Ranged champions may still have an attack through a reset.
                spend_resets(obj);
                if (me.can_attack()) attack_best(obj);
            }
        });

        // Place a ward toward our objective once recharged.
        if (CFG.wards) guard("ward", [&] { place_ward(obj); });

        // Altar lock on our tribute altar when enemies are close.
        if (CFG.buy_locks && obj.kind == ObjKind::Tribute && obj.altar.x >= 0) {
            auto& locks = me.consumables()[cambc::consumable_type::altar_lock];
            if (locks.count() > 0 && dist(pos, obj.altar) <= 2 && !world_->enemies.empty())
                try { locks.use(obj.altar); } catch (...) {}
        }

        me.set_priority(10 + static_cast<int>(me.gem_count()));
    }

private:
    enum class ObjKind { Farm, Capture, Tribute, Flee, Fight, Jump, Wander };

    struct Objective {
        ObjKind kind = ObjKind::Wander;
        bitboard goals;          // tiles we want to stand on / path to
        bitboard land;           // Jump: candidate landing tiles in next comp
        vec2 jump_dest{ -1, -1 };// Jump: final target (picks the landing)
        vec2 altar{ -1, -1 };
        std::size_t group = SIZE_MAX;
        bool stay = false;       // hold position (capturing)
        bool flee = false;
        bool protect = false;    // path around awake camps / enemy ranges
        bool staging = false;    // waiting outside aggro for the squad: wake nothing
    };

    std::optional<World> world_;

    // ------------------------------ economy ---------------------------------
    void buy_all() {
        auto& me = cambc::self();
        const auto stat = stat_for(me.champion_name());
        const auto shard = cambc::get_item_enum(CFG.item_family, stat, true);
        const unsigned gold = me.gold_count();

        // Consumables first (cheap), then shards. The crystal is the escape
        // tool; the lock stalls enemy tribute on our altar.
        if (CFG.buy_locks && me.can_buy(cambc::consumable_type::altar_lock)
            && gold >= cambc::consumable_type::altar_lock.cost() + 30) {
            try { me.buy(cambc::consumable_type::altar_lock); } catch (...) {}
        }
        // Two crystals minimum: one to hop out, one to get back for tribute.
        if (CFG.buy_tp) {
            for (int i = 0; i < 2; ++i) {
                if (me.consumables()[cambc::consumable_type::tp_crystal].count() >= 2) break;
                if (!me.can_buy(cambc::consumable_type::tp_crystal)
                    || me.gold_count() < cambc::consumable_type::tp_crystal.cost() + 40) break;
                try { me.buy(cambc::consumable_type::tp_crystal); } catch (...) {}
            }
        }
        const unsigned count = me.gold_count() / shard.cost();
        if (count && me.can_buy(shard, count)) {
            try { me.buy(shard, count); } catch (...) {}
        }
    }

    void go_home() {
        auto& me = cambc::self();
        bitboard goals = cambc::map::spawn_region(team::ally);
        goals.set(me.position(), false);
        bool fld = false;
        move_toward_goals(world_->blocked, goals, fld);
    }

    // ---------------------------- objectives --------------------------------
    // Begin the tribute channel if we stand next to a usable altar.
    bool try_submit_now() {
        auto& me = cambc::self();
        const vec2 pos = me.position();
        int best_d = INT32_MAX;
        vec2 best{ -1, -1 };
        for (auto altar : cambc::map::altars().positions()) {
            const int d = dist(pos, altar);
            if (d <= cambc::constants::submit_gems_range && d < best_d) {
                best_d = d;
                best = altar;
            }
        }
        if (best.x < 0) return false;
        try { me.submit_gems(best); return true; } catch (...) { return false; }
    }

    // Walk to a launchpad and channel a TP crystal toward `target_comp`.
    // jump_dest picks which landing tile to take (nearest to the final goal).
    std::optional<Objective> jump_objective(int target_comp, vec2 jump_dest) {
        const int cur = world_->cur_comp;
        if (cur < 0 || target_comp < 0 || target_comp == cur) return std::nullopt;
        const int hop = world_->next_hop[cur][target_comp];
        if (hop < 0) return std::nullopt;
        auto it = world_->comp_hop[cur].find(hop);
        if (it == world_->comp_hop[cur].end() || it->second.launch.is_empty())
            return std::nullopt;
        Objective o;
        o.kind = ObjKind::Jump;
        o.goals = it->second.launch;
        o.land = it->second.land;
        o.jump_dest = jump_dest;
        return o;
    }

    Objective choose_objective() {
        auto& me = cambc::self();
        Objective obj;
        obj.goals.clear();
        const vec2 pos = me.position();
        // Took damage since our last turn? Camps land hits between turns too,
        // but with an enemy visible a falling bar usually means their poke.
        const bool took_dmg = last_hp_ > 0.f && me.health() < last_hp_ - 1.f;
        last_hp_ = me.health();

        // 0) Enemy pressure: real players hunt isolated farmers. When visible
        // enemies outnumber nearby allies, head home — a death gives the
        // killer our carried gems plus 60 rounds of downtime. Skipped when a
        // tribute is one altar away: damage does not cancel tributes.
        if (!world_->enemies.empty()) {
            int close_enemies = 0, close_allies = 0, nearest_e = INT32_MAX;
            vec2 nearest_pos{ 0, 0 };
            for (auto& e : world_->enemies) {
                const int d = dist(pos, e.pos);
                if (d < nearest_e) { nearest_e = d; nearest_pos = e.pos; }
                if (d <= 7) ++close_enemies;
            }
            for (auto& a : world_->allies_seen)
                if (dist(pos, a.pos) <= 7) ++close_allies;
            const bool outnumbered = close_enemies > close_allies;
            const bool carrying = me.gem_count() > 0;
            // The twins share a fate — either dying kills both. Bail earlier
            // so a single bad fight costs one body of tempo, not two.
            const bool twin = me.champion_name() == cambc::champion_type::cassi
                || me.champion_name() == cambc::champion_type::issac;
            const bool hurt = me.health()
                < me.max_health() * (twin ? 0.70f : 0.65f);
            // Under fire = some enemy's attack range already covers us —
            // they're landing free hits while we walk. Ability poke lands
            // from beyond attack range (Stellar hits at 5-6): falling health
            // no awake camp explains counts as enemy fire too.
            bool poked = false;
            if (took_dmg) {
                poked = true;
                for (auto& s : world_->camps)
                    if (!s.asleep && dist(pos, s.pos) <= s.range) { poked = false; break; }
            }
            bool under_fire = poked;
            for (auto& e : world_->enemies)
                if (dist(pos, e.pos) <= e.range) { under_fire = true; break; }
            // Broadcast the sighting. A teammate's fresh distress call is not
            // overwritten by a calm sighting — it is what pulls help in.
            vec2 dbp{ -99, -99 };
            int dbc = 0;
            bool dbf = false;
            const bool distress = CFG.beacon && world_->comms.beacon(2, dbp, dbc, dbf) && dbf;
            if (CFG.beacon && !(distress && !under_fire && world_->comms.beacon_age() <= 1))
                world_->comms.set_beacon(nearest_pos, close_enemies, under_fire);
            // Flee when a threat is imminent and we have something to lose.
            // A healthy empty-handed champ keeps farming — a passing enemy is
            // not worth abandoning a camp over.
            const bool imminent = nearest_e <= 4 && (outnumbered || hurt);
            const bool carrier_at_risk = carrying && nearest_e <= 7
                && (hurt || outnumbered || under_fire);
            if (imminent || carrier_at_risk) {
                // Fleeing across a gap: jump back toward home with a crystal.
                if (world_->cur_comp != world_->home_comp && world_->has_tp)
                    if (auto j = jump_objective(world_->home_comp, world_->home))
                        return *j;
                obj.kind = ObjKind::Flee;
                obj.flee = true;
                obj.protect = true;
                return obj;
            }

            // Fight back: an enemy whose attack range already covers us is
            // hitting us for free while we farm. If the fight is even (not
            // outnumbered, not hurt) close on the nearest such hunter instead
            // of donating HP. Heavy carriers skip this — losing 3 gems to a
            // scuffle is cheap, losing a 20-gem haul is not.
            if (me.gem_count() <= 3 && !outnumbered && !hurt) {
                const EnemySnap* hunter = nullptr;
                int hunter_d = INT32_MAX;
                for (auto& e : world_->enemies) {
                    const int d = dist(pos, e.pos);
                    // Answering a distress call: the hunter on our teammate
                    // is fair game even though it isn't hitting us.
                    const bool helping = distress && dist(e.pos, dbp) <= 3;
                    const bool in_range = d <= e.range || ((poked || helping) && d <= 6);
                    if (in_range && d <= 6 && d < hunter_d) { hunter = &e; hunter_d = d; }
                }
                if (hunter) {
                    obj.kind = ObjKind::Fight;
                    obj.goals = tiles_around(hunter->pos,
                        static_cast<int>(me.attack_range()));
                    obj.goals &= ~world_->blocked;
                    if (!obj.goals.is_empty()
                        && world_->goals_reachable(obj.goals)) return obj;
                }
            }
        } else if (CFG.beacon && me.gem_count() <= 3
                   && me.health() >= me.max_health() * 0.7f) {
            // A teammate nearby is under fire from one or two hunters we can't
            // see: converge, so the hunter meets two or three of us instead of
            // one. A kill also pays 100 gold plus whatever the hunter carries.
            vec2 bp; int bc = 0; bool bf = false;
            if (world_->comms.beacon(2, bp, bc, bf) && bf && bc <= 2
                && dist(pos, bp) <= 8 && dist(pos, bp) >= 2
                && current_capture() == SIZE_MAX) {
                obj.kind = ObjKind::Fight;
                obj.goals = tiles_around(bp, 2) & ~world_->blocked;
                obj.goals.set(pos, false);
                if (!obj.goals.is_empty() && world_->goals_reachable(obj.goals)) return obj;
                obj.goals.clear();
            }
        }

        // 1) Tribute when carrying enough gems.
        if (me.gem_count() >= CFG.tribute_min) {
            // Stranded on a foreign component with no altar: hop back toward
            // home with a crystal, or recall (the only terrain-proof escape).
            const int cur = world_->cur_comp;
            if (cur >= 0 && cur != world_->home_comp && !world_->comp_altar[cur]) {
                if (world_->has_tp)
                    if (auto j = jump_objective(world_->home_comp, world_->home))
                        return *j;
                if (incoming_threat() <= 0.f) {
                    try { me.recall(); } catch (...) {}
                    obj.kind = ObjKind::Wander;
                    return obj;
                }
            }
            obj = tribute_objective();
            if (obj.kind == ObjKind::Tribute) return obj;
        }

        // 1b) Healers shadow a hurt ally: camping next to the carry keeps them
        // farming instead of walking home or dying. Opponent Willow comps
        // sustain their farmers through whole clears this way.
        if (CFG.heal_shadow && has_heal(me)) {
            const AllySnap* ward = nullptr;
            float ward_key = FLT_MAX;
            for (auto& a : world_->allies_seen) {
                if (a.hp >= a.maxhp * 0.82f) continue;
                // Only divert for an ally already close — hiking across the
                // map to heal costs more than their downtime.
                if (dist(pos, a.pos) > 8) continue;
                const float key = dist(pos, a.pos) + a.hp * 0.02f;
                if (key < ward_key) { ward_key = key; ward = &a; }
            }
            if (ward) {
                obj.kind = ObjKind::Farm;
                obj.goals = tiles_around(ward->pos, 2) & ~world_->terrain;
                obj.goals.set(pos, false);
                if (!obj.goals.is_empty() && world_->goals_reachable(obj.goals))
                    return obj;
                obj.goals.clear();
            }
        }

        // 2) Stay on a capture that is counting down.
        if (std::size_t g = current_capture(); g != SIZE_MAX) {
            obj.kind = ObjKind::Capture;
            obj.group = g;
            obj.goals = world_->spawn_tiles[g];
            obj.stay = world_->spawn_tiles[g].is_set(pos);
            return obj;
        }

        // 3) Squad follower: the leader announced a dangerous group — drop the
        // solo farm and go help (stage beside it until the leader is there).
        if (squad_role(World::Role::follower)) {
            const int g = world_->comms.squad_target(world_->squad, kSquadAge);
            const int round = static_cast<int>(cambc::round_number());
            if (g >= 0 && static_cast<std::size_t>(g) < world_->groups.size()
                && world_->group_farmable(g) && world_->group_comp[g] == world_->cur_comp
                && round >= blocked_until_[g]) {
                Objective o = farm_objective(static_cast<std::size_t>(g));
                if (world_->goals_reachable(o.goals)) {
                    o.stay = o.goals.is_set(pos) && world_->group_has_member_camp(g);
                    if (squad_gate(o)) {
                        sticky_group_ = o.group;
                        chase_group_ = SIZE_MAX;
                        chase_stall_ = 0;
                        return o;
                    }
                }
            }
        }

        // 4) Farm: best group whose goal tiles are actually walkable now.
        // Hysteresis: keep the current target while it scores within 55% of
        // the leader — oscillating between two near-equal groups makes the
        // champion walk back and forth forever.
        const auto ranked = ranked_groups();
        // Prefer the sticky target if it still scores within 55% of the
        // leader — prevents objective flip-flopping.
        std::size_t start_at = 0;
        if (sticky_group_ != SIZE_MAX && !ranked.empty()) {
            const double best = ranked.front().first;
            for (std::size_t k = 0; k < ranked.size(); ++k)
                if (ranked[k].second == sticky_group_ && ranked[k].first > best * 0.55)
                    { start_at = k; break; }
        }
        bool found = false;
        for (std::size_t k = start_at; k < ranked.size(); ++k) {
            const std::size_t target = ranked[k].second;
            Objective o;
            o.group = target;
            if (world_->group_has_reward(target)) {
                o.kind = ObjKind::Capture;
                o.goals = world_->spawn_tiles[target];
            } else {
                // Path to live member camps; fall back to the spawn region
                // when none are visible yet.
                o = farm_objective(target);
            }
            // Foreign component: only reachable via a TP jump.
            const int gc = world_->group_comp[target];
            if (gc >= 0 && gc != world_->cur_comp) {
                if (!world_->has_tp) continue;
                if (auto j = jump_objective(gc, world_->centers[target])) {
                    sticky_group_ = target;
                    chase_stall_ = 0;
                    return *j;
                }
                continue;
            }
            if (!world_->goals_reachable(o.goals)) continue;
            o.stay = o.goals.is_set(pos) && world_->group_has_member_camp(target);

            // Squad leader on a dangerous group: announce it to the follower
            // and wait at a staging tile until they stand together (no stall
            // timer — standing still is the point there).
            if (squad_role(World::Role::leader) && o.kind == ObjKind::Farm
                && solo_lives(target, my_dps(), me.max_health()) >= 1.f) {
                world_->comms.set_squad_target(world_->squad, static_cast<int>(target));
                if (announced_ != target) ++dbg_rally_calls_;
                announced_ = target;
                if (!squad_gate(o)) continue;
                if (o.staging) {
                    sticky_group_ = o.group;
                    chase_group_ = SIZE_MAX;
                    chase_stall_ = 0;
                    return o;
                }
            }

            // Stall detection: if our distance to this group's centre has not
            // improved in 12 rounds (a corridor blocked by a camp we cannot
            // reach), give up on it for a while. Distances <= 2 mean we're in
            // contact — keep fighting, big camps take that long to kill.
            const int best_goal_d = dist(cambc::self().position(), world_->centers[o.group]);
            bool engaged = false;
            for (auto& c : world_->camps)
                if (c.group == o.group && dist(c.pos, cambc::self().position()) <= 4) {
                    engaged = true;
                    break;
                }
            if (o.group != chase_group_ || best_goal_d < chase_best_ || engaged) {
                chase_group_ = o.group;
                chase_best_ = best_goal_d;
                chase_stall_ = 0;
            } else if (++chase_stall_ > 12) {
                blocked_until_[o.group] =
                    static_cast<int>(cambc::round_number()) + 80;
                chase_group_ = SIZE_MAX;
                chase_stall_ = 0;
                sticky_group_ = SIZE_MAX;
                continue;  // skip it this turn too
            }
            sticky_group_ = o.group;
            found = true;
            return o;
        }
        if (!found) {
            sticky_group_ = SIZE_MAX;
            const int cur = world_->cur_comp;
            if (cur >= 0 && cur != world_->home_comp) {
                // Stranded on a foreign island with nothing left locally: hop
                // home to re-stock, or recall when out of crystals.
                if (world_->has_tp) {
                    if (auto j = jump_objective(world_->home_comp, world_->home))
                        return *j;
                } else if (incoming_threat() <= 0.f) {
                    try { me.recall(); } catch (...) {}
                    obj.kind = ObjKind::Wander;
                    return obj;
                }
            } else if (!world_->has_tp && cur >= 0) {
                // Everything left sits across a gap and we hold no crystal:
                // walk home so the spawn shop restocks us.
                bool foreign_left = false;
                for (std::size_t i = 0; i < world_->groups.size(); ++i)
                    if ((world_->group_farmable(i) || world_->group_has_reward(i))
                        && world_->group_comp[i] >= 0 && world_->group_comp[i] != cur
                        && world_->next_hop[cur][world_->group_comp[i]] >= 0) {
                        foreign_left = true;
                        break;
                    }
                if (foreign_left) {
                    obj.kind = ObjKind::Farm;
                    obj.goals = cambc::map::spawn_region(team::ally);
                    return obj;
                }
            }
        }

        // 4) Contest an enemy capture in view.
        if (CFG.contest) {
            for (std::size_t i = 0; i < world_->groups.size(); ++i) {
                if ((world_->spawn_tiles[i] & world_->visible).is_empty()) continue;
                try {
                    const auto cap = world_->groups[i].capture_state();
                    if (cap.state == cambc::map::camp_group_capture_type::enemy_capturing
                        && world_->goals_reachable(world_->spawn_tiles[i])) {
                        obj.kind = ObjKind::Capture;
                        obj.group = i;
                        obj.goals = world_->spawn_tiles[i];
                        return obj;
                    }
                } catch (...) {}
            }
        }

        // 5) Wander toward the map centre / unexplored side.
        bitboard g;
        g.clear();
        g.set({ cambc::map::width() / 2, cambc::map::height() / 2 });
        obj.goals = g;
        return obj;
    }

    Objective tribute_objective() {
        auto& me = cambc::self();
        Objective obj;
        obj.kind = ObjKind::Tribute;
        // Only a hurt carrier detours around threat ranges — tribute ignores
        // damage anyway, so a healthy carrier tanks the odd hit rather than
        // walking the long way.
        // Route around live danger when the haul is precious or we're already
        // chipped: crossing an awake camp's range costs ~2*range*str damage,
        // which stacks on top of farm damage and kills carriers mid-route.
        obj.protect = CFG.protect_carriers
            && (me.health() < me.max_health() * 0.75f || me.gem_count() >= 12);
        obj.goals.clear();
        const vec2 pos = me.position();

        // Prefer the nearest unlocked altar; enemy-locked ones are a fallback
        // (submit_gems converts into attacks on the lock anyway).
        vec2 best{ -1, -1 };
        int best_d = INT32_MAX;
        vec2 best_locked{ -1, -1 };
        int best_locked_d = INT32_MAX;
        for (auto altar : cambc::map::altars().positions()) {
            // An altar is usable only when one of its neighbours is walkable
            // in our current component — a gap-locked altar is unreachable.
            bool usable = false;
            for (int dy = -1; dy <= 1 && !usable; ++dy)
                for (int dx = -1; dx <= 1 && !usable; ++dx)
                    if (world_->comp_at({ altar.x + dx, altar.y + dy }) == world_->cur_comp)
                        usable = true;
            if (!usable) continue;
            const int d = dist(pos, altar);
            const bool enemy_lock = world_->enemy_locks.is_set(altar);
            if (!enemy_lock && d < best_d) { best_d = d; best = altar; }
            if (enemy_lock && d < best_locked_d) { best_locked_d = d; best_locked = altar; }
        }
        const vec2 altar = best.x >= 0 ? best : best_locked;
        if (altar.x < 0) { obj.kind = ObjKind::Wander; return obj; }
        obj.altar = altar;
        obj.goals = tiles_around(altar, cambc::constants::submit_gems_range);
        return obj;
    }

    // Group whose region we currently occupy and which we are capturing.
    std::size_t current_capture() {
        auto& me = cambc::self();
        const int gi = world_->group_at(me.position());
        if (gi < 0 || !world_->group_has_reward(gi)) return SIZE_MAX;
        try {
            const auto cap = world_->groups[gi].capture_state();
            using ct = cambc::map::camp_group_capture_type;
            if (cap.state == ct::ally_capturing || cap.state == ct::capture_available
                || cap.state == ct::contested)
                return static_cast<std::size_t>(gi);
        } catch (...) {}
        return SIZE_MAX;
    }

    // Estimated health cost of clearing a group using cached group totals.
    float fight_cost(std::size_t i) { return fight_cost(i, my_dps()); }
    float fight_cost(std::size_t i, float dps) const {
        const float rounds = std::max(1.f, world_->group_hp[i]) / dps;
        return world_->group_str[i] * rounds;
    }
    static float my_dps() {
        auto& me = cambc::self();
        return std::max(1.f, me.strength()) + me.focus() * 0.4f;
    }

    // --------------------------------- squads ---------------------------------
    // Camps hit the nearest champion and a group deals str x rounds-alive in
    // total, so two champions focusing one group take about half the damage a
    // solo farmer would — and the tank in front takes most of it. Groups a
    // lone champion can't clear without dying are farmed by a pair instead:
    // the tank leader announces the target in shared memory, its damage
    // follower walks over, and both wait just outside aggro until they stand
    // together, then engage. Cheap groups are still farmed solo and spread.
    static constexpr int kSquadAge = 2;   // rounds an announcement survives silence
    float solo_lives(std::size_t g, float dps, float maxhp) const {
        return fight_cost(g, dps) / std::max(1.f, maxhp);
    }
    bool squad_role(World::Role r) const { return CFG.rally && world_->role == r; }

    // Farm objective for a group: stand next to its live camps (ranged
    // champions at max range), or walk to its spawn tiles if none are seen.
    Objective farm_objective(std::size_t target) {
        Objective o;
        o.group = target;
        o.kind = ObjKind::Farm;
        o.goals.clear();
        // Ranged champions hold at max range so the melee in front stay
        // nearest — camps always hit the nearest champion.
        const int reach = CFG.ranged_standoff
            ? std::max(1, static_cast<int>(cambc::self().attack_range())) : 1;
        for (auto& s : world_->camps)
            if (s.group == target) o.goals |= tiles_around(s.pos, reach);
        if (o.goals.is_empty()) o.goals = world_->spawn_tiles[target];
        return o;
    }

    // Hold a staging tile outside the group's aggro until a teammate stands
    // with us, or the fight is already on. Returns false to skip the group.
    bool squad_gate(Objective& o) {
        auto& me = cambc::self();
        const std::size_t g = o.group;
        const vec2 pos = me.position();
        const int round = static_cast<int>(cambc::round_number());
        // Committed: once we've decided to go in, don't second-guess it on
        // the approach (that flip-flop kept whole squads pacing in place).
        if (engage_group_ == g) return true;
        if (stage_group_ != g || round - last_stage_round_ > 20) {
            stage_group_ = g;
            stage_since_ = round;
        }

        // Fight already on (the tank or a teammate woke the group): join in.
        for (auto& s : world_->camps)
            if (s.group == g && !s.asleep) { engage_group_ = g; return true; }

        // Staging ring: open tiles just outside every member's attack range.
        bitboard aggro, outer;
        aggro.clear();
        outer.clear();
        const int r = world_->group_range[g] + 1;
        for (auto t : world_->spawn_tiles[g].positions()) {
            aggro |= tiles_around(t, r);
            outer |= tiles_around(t, r + 2);
        }
        for (auto& s : world_->camps)
            if (s.group == g) aggro |= tiles_around(s.pos, s.range + 1);
        const bitboard ring = outer & ~aggro & ~world_->blocked;

        // Together: any teammate beside us or anywhere around the group (the
        // ring test must use `outer` — occupied tiles are cut from `ring`).
        for (auto& a : world_->allies_seen)
            if (dist(a.pos, pos) <= 4 || outer.is_set(a.pos)) { engage_group_ = g; return true; }
        if (round - stage_since_ > 12) {
            // Partner isn't coming (dead, hauling gems home): take the fight
            // alone only if it is merely uncomfortable, else skip the group.
            if (solo_lives(g, my_dps(), me.max_health()) < 1.6f) { engage_group_ = g; return true; }
            blocked_until_[g] = round + 40;
            stage_group_ = SIZE_MAX;
            ++dbg_rally_quits_;
            return false;
        }
        if (ring.is_empty() || !world_->goals_reachable(ring)) return true;
        o.goals = ring;
        o.stay = ring.is_set(pos);
        o.staging = true;
        last_stage_round_ = round;
        return true;
    }

    // Farmable/reward groups ranked best-first as (score, index) pairs.
    // Unreachable groups are excluded; groups we are standing in but cannot
    // see camps for are deprioritised (already searched — move on).
    std::vector<std::pair<double, std::size_t>> ranked_groups() {
        auto& me = cambc::self();
        const vec2 pos = me.position();
        const float hp = me.health();
        const int pos_group = world_->group_at(pos);
        std::vector<std::pair<double, std::size_t>> scored;

        // Gem scarcity: on maps like stampede a single raid-boss group holds
        // nearly all the gems. When one group dominates the remaining supply,
        // every champion scores it identically high — the deterministic
        // ranking makes the whole team converge into a spontaneous raid,
        // which is also the only way to crack 4x2400hp guards without
        // bleeding a dozen solo deaths.
        float total_gems = 0.f;
        for (std::size_t i = 0; i < world_->groups.size(); ++i)
            if (world_->group_farmable(i) && world_->group_reachable(i))
                total_gems += world_->group_gems[i];

        const float dps = my_dps();
        const float maxhp = me.max_health();
        const bool lead = squad_role(World::Role::leader);

        for (std::size_t i = 0; i < world_->groups.size(); ++i) {
            if (!world_->group_farmable(i) && !world_->group_has_reward(i)) continue;
            if (!world_->group_reachable(i)) continue;
            // Temporarily blacklisted: chasing a fleeing camp that never
            // gets closer wastes the whole match.
            {
                if (static_cast<int>(cambc::round_number()) < blocked_until_[i]
                    && !world_->group_has_reward(i)) continue;
            }
            double value = world_->group_gems[i] * 10.0 + world_->group_gold[i] * 0.4;
            if (value <= 0) value = 1;
            const int d = dist(pos, world_->centers[i]);
            // Every farm loop ends with a death or a recall — both resume at
            // the spawn, so the effective travel distance is champ→group plus
            // spawn→group. Far groups lose a lot of uptime to walking.
            const int d_home = world_->group_home_d[i];
            const double walk = 0.15 * d + 0.10 * d_home;
            // Score = value per expected life lost, discounted by distance.
            // fight_cost is the total damage taken to clear the group;
            // cost/hp is roughly the number of deaths it will cost. A monolith
            // (~20000hp, 200dmg/round) costs dozens of lives for its 256 gems,
            // while wolf groups cost ~1 life — cheap groups first wins.
            const float cost = fight_cost(i, dps);
            float lives = cost / std::max(1.f, hp);
            // A squad leader prices dangerous groups as a pair fight: the group
            // dies twice as fast and the hits are shared, so ~1/4 the lives.
            if (lead && !world_->group_has_reward(i) && solo_lives(i, dps, maxhp) >= 1.f)
                lives /= 4.f;
            double score = value / (1.0 + walk) / (1.0 + lives * 1.0);
            if (total_gems > 0 && world_->group_gems[i] > total_gems * 0.6f)
                score *= 3.0;                                 // raid call: all converge
            if (world_->group_has_reward(i)) score *= 6.0;      // free reward: grab it
            if (CFG.spread && world_->my_groups[i]) score *= 1.3;  // prefer my sector
            // Already inside this group's region with no member camps in view:
            // camps roamed off — deprioritise so we keep sweeping the map.
            if (pos_group == static_cast<int>(i) && !world_->group_has_reward(i)
                && !world_->group_has_member_camp(i)) score *= 0.02;
            scored.emplace_back(score, i);
        }
        // Last resort: if everything was filtered as unsafe, accept the
        // cheapest reachable fight — dying at a camp beats scoring nothing.
        if (scored.empty()) {
            float best_cost = FLT_MAX;
            std::size_t best = SIZE_MAX;
            for (std::size_t i = 0; i < world_->groups.size(); ++i) {
                if (!world_->group_farmable(i) && !world_->group_has_reward(i)) continue;
                if (!world_->group_reachable(i)) continue;
                const float c = fight_cost(i);
                if (c < best_cost) { best_cost = c; best = i; }
            }
            if (best != SIZE_MAX) scored.emplace_back(0.01, best);
        }
        std::sort(scored.begin(), scored.end(),
                  [](auto& a, auto& b) { return a.first > b.first; });
        return scored;
    }

    // ------------------------------- combat ----------------------------------
    // Best basic-attack target currently in range.
    bool attack_best(const Objective& obj) {
        auto& me = cambc::self();
        if (!me.can_attack()) return false;
        const auto reach = me.attack_tiles();

        CampSnap* best_camp = nullptr;
        float best_camp_key = FLT_MAX;
        // Hauling gems to an altar: do not wake fresh camps — a sleeping camp
        // only fights back once struck, and dying dumps everything we carry.
        const bool protect_gems = obj.kind == ObjKind::Tribute;
        if (!protect_gems && !obj.staging) {
            for (auto& s : world_->camps) {
                if (!reach.is_set(s.pos)) continue;
                // Prefer members of our target group; inside a group kill the
                // damage dealers first (they hurt most per round alive).
                float key = s.hp * 0.01f - s.str * 10.f;
                if (s.group != obj.group) key += 10000.f;
                if (key < best_camp_key) { best_camp_key = key; best_camp = &s; }
            }
        }

        EnemySnap* best_enemy = nullptr;
        float best_enemy_score = -1;
        for (auto& s : world_->enemies) {
            if (!reach.is_set(s.pos)) continue;
            const float score = 1000.f - s.hp + s.gems * 200.f;
            if (score > best_enemy_score) { best_enemy_score = score; best_enemy = &s; }
        }

        // Enemy altar locks in range when we want to tribute there.
        for (auto tile : world_->enemy_locks.positions()) {
            if (!reach.is_set(tile)) continue;
            if (obj.kind == ObjKind::Tribute && dist(tile, obj.altar) == 0) {
                try {
                    auto lock = cambc::vision::altar_lock_at(tile);
                    me.attack(lock);
                    return true;
                } catch (...) {}
            }
        }

        // Champion kills steal gems — prioritise targets we can hurt most.
        if (best_enemy && (CFG.chase_enemies || best_enemy_score > 800.f || !best_camp)) {
            try { me.attack(best_enemy->ref); return true; } catch (...) {}
        }
        if (best_camp) {
            try { me.attack(best_camp->ref); return true; } catch (...) {}
        }
        if (best_enemy) {
            try { me.attack(best_enemy->ref); return true; } catch (...) {}
        }
        return false;
    }

    // Cast attack-reset abilities to squeeze out extra attacks.
    void spend_resets(const Objective& obj) {
        auto& me = cambc::self();
        if (me.can_attack()) { attack_best(obj); return; }
        if (!CFG.use_abilities || !me.can_cast()) return;
        for (auto& ab : me.abilities()) {
            if (!ab.is_attack_reset()) continue;
            try {
                if (ab.is_ready() && ab.use()) {
                    attack_best(obj);
                    return;
                }
            } catch (...) {}
        }
    }

    // Cast the best available non-reset ability.
    void cast_best(const Objective& obj) {
        auto& me = cambc::self();
        if (!me.can_cast()) return;
        // Staging for a squad fight: a stray spell would wake the group early.
        if (obj.staging && world_->enemies.empty()) return;

        struct Cand { float score; int slot; cambc::camp* camp; cambc::champion* champ; vec2 tile; int kind;
            std::vector<vec2> tiles; };  // dash landing candidates, best-first
        std::optional<Cand> best;
        auto consider = [&](Cand c) {
            if (!best || c.score > best->score) best = c;
        };

        const vec2 pos = me.position();
        const bool threat = incoming_threat() > 0;

        for (auto& ab : me.abilities()) {
            if (ab.is_attack_reset() || !ab.info()) continue;
            bool ready = false;
            try { ready = ab.is_ready(); } catch (...) {}
            if (!ready) continue;
            const auto& info = *ab.info();
            const int slot = static_cast<int>(ab.slot());

            if (auto* dmg = std::get_if<cambc::ability_damage>(&info)) {
                const float d = ab.damage_amount();
                for (auto& s : world_->enemies) {
                    if (dist(pos, s.pos) > dmg->range) continue;
                    float kill = d >= s.hp ? 500.f : 0.f;
                    consider({ d * 3.f + kill + s.gems * 300.f, slot, nullptr, &s.ref, {}, 0 });
                }
                if (ab.can_target_camps())
                    for (auto& s : world_->camps) {
                        if (dist(pos, s.pos) > dmg->range) continue;
                        float kill = d >= s.hp ? 200.f : 0.f;
                        consider({ d + kill, slot, &s.ref, nullptr, {}, 0 });
                    }
            } else if (auto* cc = std::get_if<cambc::ability_cc>(&info)) {
                const float d = ab.damage_amount();
                for (auto& s : world_->enemies) {
                    if (dist(pos, s.pos) > cc->range) continue;
                    consider({ 150.f + d * 2.f + s.gems * 300.f, slot, nullptr, &s.ref, {}, 1 });
                }
                if (ab.can_target_camps())
                    for (auto& s : world_->camps) {
                        if (dist(pos, s.pos) > cc->range || s.str <= 0) continue;
                        consider({ 60.f + d + s.str * 2.f, slot, &s.ref, nullptr, {}, 1 });
                    }
                // Ground-targeted stuns (Ryth's area stun): pick the tile
                // stunning the most enemies and dangerous camps at once.
                if (ab.can_target_ground()) {
                    for (auto t : tiles_around(pos, cc->range).positions()) {
                        int hits = 0;
                        for (auto& s : world_->enemies)
                            if (dist(t, s.pos) <= 1) ++hits;
                        for (auto& s : world_->camps)
                            if (s.str > 0 && dist(t, s.pos) <= 1) ++hits;
                        if (hits >= 2)
                            consider({ 120.f + hits * 80.f + d, slot, nullptr, nullptr, t, 2 });
                    }
                }
            } else if (auto* aoe = std::get_if<cambc::ability_aoe_damage>(&info)) {
                const float d = ab.damage_amount();
                // Try ground tiles in range; count hits in the effect radius.
                for (auto t : tiles_around(pos, aoe->range).positions()) {
                    if (!cambc::map::is_in_bounds(t)) continue;
                    int hits = 0;
                    for (auto& s : world_->camps) if (dist(t, s.pos) <= aoe->radius) ++hits;
                    for (auto& s : world_->enemies)
                        if (dist(t, s.pos) <= aoe->radius) ++hits;
                    if (hits >= 2)
                        consider({ d * hits * 1.4f, slot, nullptr, nullptr, t, 2 });
                }
            } else if (auto* heal = std::get_if<cambc::ability_heal>(&info)) {
                const float h = ab.heal_amount();
                // Self-heal: keeps a solo farmer alive through camp damage.
                {
                    const float missing = me.max_health() - me.health();
                    if (missing > h * 0.5f && threat)
                        consider({ missing * 0.9f + 50.f, slot, nullptr, &me, {}, 3 });
                }
                for (auto& s : world_->allies_seen) {
                    if (dist(pos, s.pos) > heal->range) continue;
                    const float missing = s.maxhp - s.hp;
                    if (missing > h * 0.4f)
                        consider({ missing * 0.8f, slot, nullptr, &s.ref, {}, 3 });
                }
            } else if (auto* sh = std::get_if<cambc::ability_shield>(&info)) {
                if (threat && !me.buffs().has_shield()) {
                    const float s = ab.shield_amount();
                    consider({ s * 0.6f, slot, nullptr, nullptr, {}, 4 });
                }
            } else if (auto* dash = std::get_if<cambc::ability_dash>(&info)) {
                // Combat dash when it lands damage on 2+ targets.
                if (dash->modifier > 0) {
                    for (auto t : tiles_around(pos, dash->range).positions()) {
                        int hits = 0;
                        for (auto& s : world_->camps) if (dist(t, s.pos) <= dash->radius) ++hits;
                        for (auto& s : world_->enemies)
                            if (dist(t, s.pos) <= dash->radius) ++hits;
                        if (hits >= 2)
                            consider({ ab.damage_amount() * hits + 100.f, slot, nullptr, nullptr, t, 5 });
                    }
                }
                // Mobility dash toward a distant objective. The engine
                // validates dash paths/landings strictly, so offer several
                // candidates — we try them in order at cast time.
                if (!obj.goals.is_empty() && !obj.goals.is_set(pos) && !threat) {
                    std::vector<std::pair<int, vec2>> cand;
                    int here = INT32_MAX;
                    for (auto g : obj.goals.positions()) here = std::min(here, dist(pos, g));
                    for (auto t : tiles_around(pos, dash->range).positions()) {
                        if (dist(pos, t) < 2) continue;
                        if (!cambc::map::is_in_bounds(t) || world_->blocked.is_set(t)) continue;
                        int ft = INT32_MAX;
                        for (auto g : obj.goals.positions()) ft = std::min(ft, dist(t, g));
                        if (ft >= here) continue;
                        cand.emplace_back(ft, t);
                    }
                    std::sort(cand.begin(), cand.end());
                    if (!cand.empty()) {
                        Cand c{ 40.f, slot, nullptr, nullptr, cand.front().second, 5, {} };
                        for (auto& [d, t] : cand) c.tiles.push_back(t);
                        consider(std::move(c));
                    }
                }
            }
        }

        if (!best) return;
        const bool dbg = cambc::round_number() < 15 || cambc::round_number() % 100 == 0;
        auto abilities = me.abilities();
        auto& ab = abilities[best->slot];
        try {
            bool ok = false;
            switch (best->kind) {
            case 0: case 1:
                if (best->champ) { ab.use(*best->champ); ok = true; }
                else if (best->camp) { ab.use(*best->camp); ok = true; }
                break;
            case 2:
                ab.use(best->tile); ok = true; break;
            case 3:
                if (best->champ) { ab.use(*best->champ); ok = true; }
                break;
            case 4:
                ab.use(); ok = true; break;
            case 5:
                // Dash: engine rejects illegal landings — walk the candidate
                // list until one works.
                for (auto t : best->tiles) {
                    try { ab.use(t); ok = true; break; }
                    catch (...) {}
                }
                break;
            }
            if (dbg && ok)
                std::cout << "  i" << world_->my_index << " cast kind=" << best->kind
                          << " slot=" << best->slot << " ok" << std::endl;
        } catch (const std::exception& e) {
            if (dbg)
                std::cout << "  i" << world_->my_index << " cast kind=" << best->kind
                          << " slot=" << best->slot << " fail " << e.what() << std::endl;
        }
    }

    // Incoming damage we should expect this round.
    float incoming_threat() {
        auto& me = cambc::self();
        float total = 0;
        for (auto& s : world_->camps) {
            if (s.asleep || s.str <= 0) continue;
            if (dist(me.position(), s.pos) <= s.range) total += s.str;
        }
        for (auto& s : world_->enemies)
            if (dist(me.position(), s.pos) <= s.range) total += s.str;
        return total;
    }

    void place_ward(const Objective& obj) {
        auto& me = cambc::self();
        if (me.ward_cooldown() != 0) return;
        // Ward toward our objective: pick the placement tile closest to goals.
        const auto spots = me.ward_placement_tiles().positions();
        const auto walls = cambc::map::walls();
        const auto goal_tiles = obj.goals.positions();
        vec2 target{ -1, -1 };
        if (!goal_tiles.empty()) {
            int best_d = INT32_MAX;
            for (auto t : spots) {
                if (!cambc::map::is_in_bounds(t) || walls.is_set(t)) continue;
                for (auto g : goal_tiles) {
                    const int d = dist(t, g);
                    if (d < best_d) { best_d = d; target = t; }
                }
            }
        }
        if (target.x < 0) {
            for (auto t : spots)
                if (t != me.position() && cambc::map::is_in_bounds(t) && !walls.is_set(t)) { target = t; break; }
        }
        if (target.x >= 0) { try { me.place_ward(target); } catch (...) {} }
    }
};

} // namespace strat
