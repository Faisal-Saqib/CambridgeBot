// Draft phase: pick by priority order and write a per-champion camp-group
// sector assignment into draft memory for the bots to read later.
#include <cambc.h>
#include "draft.h"
#include "config.h"
#include "strategy.h"
#include <algorithm>
#include <numeric>
#include <vector>

using cambc::vec2;

namespace {

// Greedy sector assignment: walk camp groups by descending value and give each
// to the draft slot minimising (slot load * w1 + distance from slot centroid).
std::vector<std::uint8_t> assign_sectors(const std::vector<cambc::map::camp_group>& groups,
                                         std::size_t slots, vec2 home) {
    const std::size_t n = groups.size();
    std::vector<vec2> centers(n);
    std::vector<double> values(n);
    for (std::size_t i = 0; i < n; ++i) {
        auto pos = groups[i].spawn_tiles().positions();
        vec2 c{ 0, 0 };
        for (auto p : pos) c = c + p;
        centers[i] = { c.x / std::max<int>(1, pos.size()), c.y / std::max<int>(1, pos.size()) };
        values[i] = groups[i].gem_value() * 10.0 + groups[i].gold_value() * 0.4 + 1.0;
    }

    std::vector<std::size_t> order(n);
    std::iota(order.begin(), order.end(), 0);
    std::sort(order.begin(), order.end(), [&](auto a, auto b) { return values[a] > values[b]; });

    std::vector<std::uint8_t> assign(n, 255);
    std::vector<double> load(slots, 0.0);
    std::vector<vec2> centroid(slots, home);
    std::vector<std::size_t> counts(slots, 0);

    for (auto i : order) {
        std::size_t best = 0;
        double best_cost = 1e18;
        for (std::size_t s = 0; s < slots; ++s) {
            const double d = strat::dist(centers[i], centroid[s]);
            const double cost = load[s] * 3.0 + d;
            if (cost < best_cost) { best_cost = cost; best = s; }
        }
        assign[i] = static_cast<std::uint8_t>(best);
        load[best] += values[i];
        auto& c = centroid[best];
        const double w = 1.0 / (counts[best] + 1);
        c = { static_cast<std::int32_t>(c.x * (1 - w) + centers[i].x * w),
              static_cast<std::int32_t>(c.y * (1 - w) + centers[i].y * w) };
        ++counts[best];
    }
    return assign;
}

void write_plan() {
    const auto groups = cambc::map::camp_groups();
    const std::size_t slots = std::max<std::size_t>(1, cambc::draft::team_size());

    // Sector seed: centroid of our spawn region.
    auto spawn = cambc::map::spawn_region(cambc::team::ally).positions();
    vec2 home{ 0, 0 };
    for (auto p : spawn) home = home + p;
    if (!spawn.empty()) home = { home.x / (int)spawn.size(), home.y / (int)spawn.size() };

    const auto assign = assign_sectors(groups, slots, home);

    std::vector<std::byte> bytes;
    bytes.reserve(5 + groups.size());
    bytes.push_back(std::byte{ 'S' });
    bytes.push_back(std::byte{ 1 });
    bytes.push_back(static_cast<std::byte>(slots));
    bytes.push_back(static_cast<std::byte>(groups.size() & 0xFF));
    bytes.push_back(static_cast<std::byte>((groups.size() >> 8) & 0xFF));
    for (auto s : assign) bytes.push_back(static_cast<std::byte>(s));
    cambc::draft_memory = bytes;
}

} // namespace

void play_draft() {
    static bool planned = false;
    if (!planned) {
        planned = true;
        try { write_plan(); } catch (...) {}
    }

    const auto chosen = cambc::draft::current_draft(cambc::team::ally);
    auto unpicked = [&](cambc::champion_draft p) {
        return std::find(chosen.begin(), chosen.end(), p) == chosen.end();
    };
    for (auto pick : CFG.draft_order)
        if (unpicked(pick)) { cambc::draft::pick(pick); return; }
    // Fallback: any released champion we have not picked.
    for (int i = 0; i < 12; ++i)
        if (unpicked(static_cast<cambc::champion_draft>(i))) {
            cambc::draft::pick(static_cast<cambc::champion_draft>(i));
            return;
        }
}
