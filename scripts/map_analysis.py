#!/usr/bin/env python3
"""Aggregate downloaded top-20 summaries per map and draft per-map target points.

Offline analysis over census.json (produced by scripts/strategy_census.py).
Emits docs/TOP20_MAP_TARGETS.md. Target points mix measured evidence with
clearly-labelled hypotheses; nothing here is validated gameplay.
"""
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CENSUS = ROOT / "matches" / "top20-scout" / "census.json"
OUT = ROOT / "docs" / "TOP20_MAP_TARGETS.md"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def fmt(v, digits=1):
    return f"{v:.{digits}f}" if v is not None else "n/a"


def main():
    census = load(CENSUS)
    games = census["games_detail"]
    by_map = defaultdict(list)
    for g in games:
        if g["map"]:
            by_map[g["map"]].append(g)

    def stat(gs, key):
        return mean([g[key] for g in gs])

    global_stats = {k: stat(games, k) for k in
                    ("kills", "deaths", "tribute_mean", "top_gold_share",
                     "farm_spread", "gem_loss")}

    lines = ["# Top-20 per-map target analysis", "",
             "Aggregated from downloaded ranked summaries of the current top-20 teams "
             "(matches/top20-scout). Each map lists measured top-20 behaviour plus ten "
             "target points. Points marked [measured] come from the downloaded games; "
             "[hypothesis] marks proposals derived from those measurements and map "
             "knowledge — none are validated gameplay yet.", ""]
    lines.append(f"Sample: {len(games)} team-games across {len(by_map)} maps. "
                 f"Global averages: kills {fmt(global_stats['kills'])}, "
                 f"tribute mean {fmt(global_stats['tribute_mean'])}, "
                 f"carry share {fmt(global_stats['top_gold_share'], 2)}, "
                 f"farm spread {fmt(global_stats['farm_spread'])} tiles.")
    lines.append("")

    for name in sorted(by_map):
        gs = by_map[name]
        wins = [g for g in gs if g["won"]]
        kills = stat(gs, "kills")
        deaths = stat(gs, "deaths")
        camp_deaths = sum(g["deaths_to_camps"] for g in gs)
        tribute = stat(gs, "tribute_mean")
        carry = stat(gs, "top_gold_share")
        spread = stat(gs, "farm_spread")
        group = mean([g["attackers_per_kill"] for g in gs if g["attackers_per_kill"]])
        single_cap = mean([g["single_captures"] / g["captures"] for g in gs if g["captures"]])
        wards = stat(gs, "wards")
        locks = sum(sum(v for k, v in g["consumables"].items() if k.lower() == "altar lock") for g in gs)
        crystals = sum(sum(v for k, v in g["consumables"].items() if k.lower() == "teleport crystal") for g in gs)
        linked = sum(1 for g in gs if g["bodies"] > g["draft_size"])
        early = stat(gs, "early_kills")
        drafts = Counter(c for g in gs if g["won"] for c in g["draft"])
        top_drafts = ", ".join(f"{c}({n})" for c, n in drafts.most_common(4))
        win_carry = stat(wins, "top_gold_share")
        win_spread = stat(wins, "farm_spread")

        lines.append(f"## {name} — {len(gs)} team-games, {len(wins)} wins")
        lines.append("")
        lines.append(
            f"kills {fmt(kills)} vs avg {fmt(global_stats['kills'])} | "
            f"tribute {fmt(tribute)} | carry {fmt(carry, 2)} | "
            f"group-kill {fmt(group)} | spread {fmt(spread)} | "
            f"wards {fmt(wards)} | locks {locks} crystals {crystals} | "
            f"linked {linked}/{len(gs)} | camp deaths {camp_deaths} | "
            f"winner draft picks: {top_drafts or 'n/a'}")
        lines.append("")
        pts = []
        if kills is not None and global_stats["kills"] and kills > global_stats["kills"] * 1.4:
            pts.append(f"[measured] Heavy fighting map ({fmt(kills)} kills/game vs "
                       f"{fmt(global_stats['kills'])} avg) — travel grouped and don't "
                       "farm alone in the open.")
        if group and group >= 3:
            pts.append(f"[measured] Winners fight with ~{fmt(group)} attackers/kill — "
                       "commit multiple champs or disengage; solo fights lose.")
        if spread is not None and global_stats["farm_spread"]:
            if spread <= global_stats["farm_spread"] * 0.7:
                pts.append(f"[measured] Tight clustered farming ({fmt(spread)}-tile "
                           "spread) — top teams clear adjacent camps, not split map-wide.")
            elif spread >= global_stats["farm_spread"] * 1.3:
                pts.append(f"[measured] Wide split farming ({fmt(spread)}-tile spread) — "
                           "top teams spread champs across distant camps here.")
        if carry is not None and carry >= 0.5:
            pts.append(f"[measured] Carry concentration ({fmt(carry, 2)} top gold "
                       "share) — funnel rewards to one champion and protect it.")
        if tribute is not None and tribute < 20:
            pts.append(f"[measured] Small frequent tributes (mean {fmt(tribute)}) — "
                       "top teams bank early rather than hoard here.")
        elif tribute is not None and tribute > 40:
            pts.append(f"[measured] Large hauls banked (mean {fmt(tribute)}) — "
                       "long trips worth it; carrier escort matters.")
        if locks:
            pts.append(f"[measured] Altar locks used ({locks} in sample) — "
                       "expect locked altars; carry removal pressure or lock first.")
        if crystals:
            pts.append(f"[measured] Teleport crystals bought ({crystals} in sample) — "
                       "terrain crossing/blink escapes matter on this map.")
        if wards is not None and wards >= 6:
            pts.append(f"[measured] Heavy warding ({fmt(wards)}/game) — vision "
                       "control of approaches is standard here.")
        if early and early >= 2:
            pts.append(f"[measured] Early aggression ({fmt(early)} kills before "
                       "round 200) — don't greed-farm the opening.")
        if camp_deaths >= 3:
            pts.append(f"[measured] Camps kill champions ({camp_deaths} camp deaths "
                       "in sample) — only fight camps you can finish, dodge respawn traps.")
        if linked:
            pts.append(f"[measured] Linked-pair drafts used ({linked} games) — "
                       "5-body drafts appear here; focus the pair for a double kill.")
        if single_cap and single_cap >= 0.8:
            pts.append(f"[measured] Single-recipient captures "
                       f"({fmt(single_cap * 100, 0)}%) — one champ captures while "
                       "allies zone or keep farming.")
        pts.append("[hypothesis] Route gems along the shortest safe path to the "
                   "nearest altar; reroute around visible enemy positions.")
        pts.append("[hypothesis] Keep banking trips paired when an enemy is seen "
                   "within ~14 tiles; solo carriers are the main gem-loss channel.")
        pts.append("[hypothesis] Contest the highest-value camp group before it "
                   "falls below the scarcity threshold; deny the enemy's jackpot.")
        pts.append("[hypothesis] Draft from the winners' observed picks "
                   f"({top_drafts or 'n/a'}) unless our counter-pool differs.")
        pts.append("[hypothesis] Pre-position one defender near our richest "
                   "unbanked camps when the enemy deathball is visible.")
        pts.append("[hypothesis] Rotate injured frontliners out before they die; "
                   "a second escort covers while the injured one recalls and returns.")
        pts.append("[hypothesis] If the enemy deathball holds the center, prefer "
                   "edge camps until it disperses; retake center with numbers, not solo.")
        pts.append("[hypothesis] Stagger tribute completions so the team does not "
                   "converge on the same altar at the same time.")
        pts.append("[hypothesis] Watch enemy carrier routes to the altar; a "
                   "successful kill hands us their whole bag.")
        pts = pts[:10]
        for i, p in enumerate(pts, 1):
            lines.append(f"{i}. {p}")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} covering {len(by_map)} maps", flush=True)


if __name__ == "__main__":
    main()
