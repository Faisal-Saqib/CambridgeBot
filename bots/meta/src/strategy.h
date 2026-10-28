#pragma once
// Strategy engine: sector farming, captures, tribute runs, ability use, item
// builds and light combat micro. Behaviour is tuned by StratConfig (config.h).
#include <cambc.h>
#include <algorithm>
#include <array>
#include <cfloat>
#include <cmath>
#include <cstdint>
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
    vec2 home{ 0, 0 };                     // allied spawn centroid
    bitboard terrain;                      // walls|holes|altars|enemy spawn — never changes
    bitboard home_reach;                   // tiles reachable from home on foot (static)
    std::vector<float> group_hp;           // total member health per group (static)
    std::vector<float> group_str;          // total member strength per group (static)
    std::vector<int>   group_home_d;       // chebyshev home -> nearest spawn tile (static)
    Plan plan;

    // Per-turn dynamic data.
    std::unordered_map<std::uint32_t, GroupMem> mem;
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
        for (std::size_t i = 0; i < groups.size(); ++i) {
            for (auto& member : groups[i].camps()) {
                const auto bs = member.base_stats();
                group_hp[i] += bs.base_health;
                if (bs.base_strength > 0 && bs.base_attack_range > 0)
                    group_str[i] += bs.base_strength;
            }
            int hd = INT32_MAX;
            for (auto t : spawn_tiles[i].positions())
                hd = std::min(hd, dist(home, t));
            group_home_d[i] = hd;
        }

        // Farm in pairs: consecutive allies share a sector so hard groups get
        // focus fire (a solo champ just dies to the big guards repeatedly).
        const int n_pairs = std::max(1, (n_allies + 1) / 2);
        const int my_pair = std::min(my_index / 2, n_pairs - 1);
        my_groups.assign(groups.size(), 0);
        for (std::size_t i = 0; i < groups.size(); ++i) {
            int slot = -1;
            if (plan.ok && i < plan.group_slot.size() && plan.group_slot[i] != 255)
                slot = plan.group_slot[i];
            else
                slot = static_cast<int>(i) % n_allies;  // deterministic fallback spread
            my_groups[i] = (slot % n_pairs == my_pair) ? 1 : 0;
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

    std::uint32_t group_id(std::size_t i) const {
        return static_cast<std::uint32_t>(
            static_cast<cambc::handle_camp_group_t>(groups[i]));
    }

    void refresh() {
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
        for (auto& s : camps)
            for (std::size_t i = 0; i < groups.size(); ++i)
                if (spawn_tiles[i].is_set(s.spawn)) { s.group = i; break; }

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
        for (std::size_t i = 0; i < groups.size(); ++i) {
            auto& m = mem[group_id(i)];
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
            // Reawaken groups whose respawn timer has expired.
            if (m.state == Observed::respawning && m.respawn_at >= 0 && round >= m.respawn_at)
                m.state = Observed::alive;
            // A group we saw cleared that now shows live camps again.
            if (m.state != Observed::alive && seen)
                for (auto& s : camps)
                    if (s.group == i) { m.state = Observed::alive; break; }
        }

        // Walk-blocked tiles this turn (static terrain + visible units).
        blocked = blocked_tiles(terrain);

        // Danger zone: attack ranges of things that can actually reach this
        // champ soon — nearby awake camps and nearby visible enemies. Carriers
        // and fleeing champs route around them (a death dumps the haul).
        // Sleeping camps are excluded: they only fight back once struck.
        danger.clear();
        const auto self_pos = cambc::self().position();
        for (auto& s : camps)
            if (!s.asleep && s.str > 0 && dist(s.pos, self_pos) <= 10)
                danger |= tiles_around(s.pos, s.range);
        for (auto& s : enemies)
            if (s.str > 0 && dist(s.pos, self_pos) <= 8)
                danger |= tiles_around(s.pos, s.range);
    }

    bool group_farmable(std::size_t i) const {
        const auto it = mem.find(group_id(i));
        if (it == mem.end()) return true;  // never seen: assume alive
        return it->second.state == Observed::alive;
    }

    bool group_reachable(std::size_t i) const {
        return !(spawn_tiles[i] & home_reach).is_empty();
    }

    // Terrain reachability only: units move, so a camp plugging a corridor
    // must not flip the answer turn to turn.
    bool goals_reachable(const bitboard& goals) const {
        const auto pos = cambc::self().position();
        for (auto t : goals.positions())
            if (t == pos || home_reach.is_set(t)) return true;
        return false;
    }

    bool group_has_member_camp(std::size_t i) const {
        for (auto& s : camps)
            if (s.group == i) return true;
        return false;
    }

    bool group_has_reward(std::size_t i) const {
        const auto it = mem.find(group_id(i));
        return it != mem.end() && it->second.state == Observed::reward;
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
        }

        // Dead champions still get shop turns.
        if (!me.is_alive()) {
            phase_ = "dead";
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

        try {
            phase_ = "refresh";   world_->refresh();
        if (cambc::round_number() < 15 || cambc::round_number() % 100 == 0) {
            std::cout << "i" << world_->my_index << " r" << cambc::round_number()
                      << " camps=" << world_->camps.size() << " enemies=" << world_->enemies.size()
                      << " groups=" << world_->groups.size() << " states:";
            for (std::size_t gi = 0; gi < world_->groups.size(); ++gi) {
                auto it = world_->mem.find(world_->group_id(gi));
                std::cout << (it == world_->mem.end() ? '?' : (it->second.state == strat::Observed::alive ? 'a' : it->second.state == strat::Observed::reward ? 'R' : it->second.state == strat::Observed::respawning ? 's' : 'g'));
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
    std::unordered_map<std::uint32_t, int> blocked_until_;

    // Movement routing mode (see move_toward_goals): once the BFS field has
    // been needed for the current objective, keep using it — greedy and field
    // steps disagree in walled pockets and oscillate without the latch.
    bool route_field_ = false;
    std::size_t route_group_ = SIZE_MAX;

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
        dbg_kind_ = static_cast<int>(obj.kind);
        dbg_group_ = obj.group;
        dbg_stay_ = obj.stay;
        dbg_goals_ = obj.goals.positions().size();
        dbg_cm_ = me.can_move(); dbg_ca_ = me.can_attack();

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
    enum class ObjKind { Farm, Capture, Tribute, Flee, Fight, Wander };

    struct Objective {
        ObjKind kind = ObjKind::Wander;
        bitboard goals;          // tiles we want to stand on / path to
        vec2 altar{ -1, -1 };
        std::size_t group = SIZE_MAX;
        bool stay = false;       // hold position (capturing)
        bool flee = false;
        bool protect = false;    // path around awake camps / enemy ranges
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
        if (CFG.buy_tp && me.can_buy(cambc::consumable_type::tp_crystal)
            && me.gold_count() >= cambc::consumable_type::tp_crystal.cost() + 40) {
            try { me.buy(cambc::consumable_type::tp_crystal); } catch (...) {}
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

    Objective choose_objective() {
        auto& me = cambc::self();
        Objective obj;
        obj.goals.clear();
        const vec2 pos = me.position();

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
            const bool hurt = me.health() < me.max_health() * 0.65f;
            // Flee when a threat is imminent and we have something to lose.
            // A healthy empty-handed champ keeps farming — a passing enemy is
            // not worth abandoning a camp over.
            const bool imminent = nearest_e <= 4 && (outnumbered || hurt);
            const bool carrier_at_risk = carrying && (hurt || outnumbered) && nearest_e <= 6;
            if (imminent || carrier_at_risk) {
                obj.kind = ObjKind::Flee;
                obj.flee = true;
                obj.protect = true;
                return obj;
            }

            // Fight back: an enemy whose attack range already covers us is
            // hitting us for free while we farm. If the fight is even (not
            // outnumbered, not hurt) close on the nearest such hunter instead
            // of donating HP. Carriers skip this — tribute ignores damage.
            if (!carrying && !outnumbered && !hurt) {
                const EnemySnap* hunter = nullptr;
                int hunter_d = INT32_MAX;
                for (auto& e : world_->enemies) {
                    const int d = dist(pos, e.pos);
                    if (d <= e.range && d <= 6 && d < hunter_d) { hunter = &e; hunter_d = d; }
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
        }

        // 1) Tribute when carrying enough gems.
        if (me.gem_count() >= CFG.tribute_min) {
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
                o.kind = ObjKind::Farm;
                // Path to live member camps; fall back to the spawn region
                // when none are visible yet.
                o.goals.clear();
                for (auto& s : world_->camps)
                    if (s.group == target) o.goals |= tiles_around(s.pos, 1);
                if (o.goals.is_empty()) o.goals = world_->spawn_tiles[target];
            }
            if (!world_->goals_reachable(o.goals)) continue;
            o.stay = o.goals.is_set(pos) && world_->group_has_member_camp(target);

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
                blocked_until_[world_->group_id(o.group)] =
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
        if (!found) sticky_group_ = SIZE_MAX;

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
        obj.protect = CFG.protect_carriers && me.health() < me.max_health() * 0.6f;
        obj.goals.clear();
        const vec2 pos = me.position();

        // Prefer the nearest unlocked altar; enemy-locked ones are a fallback
        // (submit_gems converts into attacks on the lock anyway).
        vec2 best{ -1, -1 };
        int best_d = INT32_MAX;
        vec2 best_locked{ -1, -1 };
        int best_locked_d = INT32_MAX;
        for (auto altar : cambc::map::altars().positions()) {
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
        const vec2 pos = me.position();
        for (std::size_t i = 0; i < world_->groups.size(); ++i) {
            if (!world_->spawn_tiles[i].is_set(pos)) continue;
            if (!world_->group_has_reward(i)) continue;
            try {
                const auto cap = world_->groups[i].capture_state();
                using ct = cambc::map::camp_group_capture_type;
                if (cap.state == ct::ally_capturing || cap.state == ct::capture_available
                    || cap.state == ct::contested)
                    return i;
            } catch (...) {}
        }
        return SIZE_MAX;
    }

    // Estimated health cost of clearing a group using cached group totals.
    float fight_cost(std::size_t i) {
        auto& me = cambc::self();
        const float dps = std::max(1.f, me.strength()) + me.focus() * 0.4f;
        const float rounds = std::max(1.f, world_->group_hp[i]) / dps;
        return world_->group_str[i] * rounds;
    }

    // Farmable/reward groups ranked best-first as (score, index) pairs.
    // Unreachable groups are excluded; groups we are standing in but cannot
    // see camps for are deprioritised (already searched — move on).
    std::vector<std::pair<double, std::size_t>> ranked_groups() {
        auto& me = cambc::self();
        const vec2 pos = me.position();
        const float hp = me.health();
        std::vector<std::pair<double, std::size_t>> scored;

        for (std::size_t i = 0; i < world_->groups.size(); ++i) {
            if (!world_->group_farmable(i) && !world_->group_has_reward(i)) continue;
            if (!world_->group_reachable(i)) continue;
            // Temporarily blacklisted: chasing a fleeing camp that never
            // gets closer wastes the whole match.
            {
                auto it = blocked_until_.find(world_->group_id(i));
                if (it != blocked_until_.end()
                    && static_cast<int>(cambc::round_number()) < it->second
                    && !world_->group_has_reward(i)) continue;
            }
            const auto& g = world_->groups[i];
            double value = g.gem_value() * 10.0 + g.gold_value() * 0.4;
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
            const float cost = fight_cost(i);
            const float lives = cost / std::max(1.f, hp);
            double score = value / (1.0 + walk) / (1.0 + lives * 1.0);
            if (world_->group_has_reward(i)) score *= 6.0;      // free reward: grab it
            if (CFG.spread && world_->my_groups[i]) score *= 1.3;  // prefer my sector
            // Already inside this group's region with no member camps in view:
            // camps roamed off — deprioritise so we keep sweeping the map.
            if (world_->spawn_tiles[i].is_set(pos) && !world_->group_has_reward(i)
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
        if (!protect_gems) {
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
        const auto spots = me.ward_placement_tiles();
        vec2 target{ -1, -1 };
        if (!obj.goals.is_empty()) {
            int best_d = INT32_MAX;
            for (auto t : spots.positions()) {
                if (!cambc::map::is_in_bounds(t) || cambc::map::walls().is_set(t)) continue;
                for (auto g : obj.goals.positions()) {
                    const int d = dist(t, g);
                    if (d < best_d) { best_d = d; target = t; }
                }
            }
        }
        if (target.x < 0) {
            for (auto t : spots.positions())
                if (t != me.position() && cambc::map::is_in_bounds(t) && !cambc::map::walls().is_set(t)) { target = t; break; }
        }
        if (target.x >= 0) { try { me.place_ward(target); } catch (...) {} }
    }
};

} // namespace strat
