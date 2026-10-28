#!/usr/bin/env python3
"""Render the top-20 strategy census as docs/TOP20_STRATEGY_CENSUS.md."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CENSUS = ROOT / "matches" / "top20-scout" / "census.json"
OUT = ROOT / "docs" / "TOP20_STRATEGY_CENSUS.md"

TITLES = {
    "single_recipient_captures": "One champion captures; allies zone or farm",
    "warding": "Regular ward placement",
    "item_family:bruiser": "Bruiser-family stat builds",
    "protected_carriers_low_loss": "Low carried-gem losses (protected carriers / early banking)",
    "group_kills_3plus": "Group kills with 3+ credited attackers",
    "carry_gold_concentration": "Concentrated gold on one carry (>=50% team share)",
    "consumable:altar_lock": "Altar locks",
    "consumable:teleport_crystal": "Teleport crystals",
    "small_tributes": "Small frequent tributes (<25 gems mean)",
    "stat_majority:health": "Health-majority item builds",
    "stat_majority:strength": "Strength-majority item builds",
    "early_aggression": "Early aggression (3+ kills before round 200)",
    "carry_damage_concentration": "Concentrated champion damage (>=60% on one champ)",
    "item_family:prospector": "Prospector-family builds",
    "item_family:treasure": "Treasure-family builds",
    "tight_farm_grouping": "Tight clustered farming (<=8-tile spread)",
    "linked_pair_draft": "Linked-pair drafts (Cassi & Issac, 5 bodies)",
    "item_family:jungle": "Jungle-family builds",
    "stat_majority:focus": "Focus-majority item builds",
    "item_family:durability": "Durability-family builds",
    "item_family:capture": "Capture-family builds",
    "item_family:collector": "Collector-family builds",
    "item_family:monster": "Monster-family builds",
    "item_family:home": "Home-family builds",
    "item_family:other": "Other/unclassified item families",
}


def main():
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    features = [f for f in census["features"] if f["feature"] != "any_game"]
    lines = [
        "# Top-20 strategy census",
        "",
        "Strategies measured from downloaded ranked summaries of the current "
        "top-20 ladder teams (matches/top20-scout, `scripts/top20_scout.py` + "
        "`scripts/strategy_census.py`). Ordered by how many of the 20 teams "
        "exhibit each pattern in the sampled games.",
        "",
        f"Sample: {census['matches_analyzed']} matches analyzed, "
        f"{census['team_games']} top-20 team-games "
        f"({census['skipped_incomplete']} incomplete skipped). "
        "A team counts as **ever using** a strategy if at least one sampled game "
        "meets the threshold; **habitual** means the threshold is met in at least "
        "half of that team's sampled games. Win rate is across the feature's games.",
        "",
        "Caveat: historical bot versions are unknowable; ranks are capture-time. "
        "Prevalence is not proof of causality — it shows what the best teams do, "
        "not necessarily why they win.",
        "",
        "| Rank | Strategy point | Habitual | Ever used | Games | Win rate |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for i, f in enumerate(features, 1):
        title = TITLES.get(f["feature"], f["feature"])
        wr = f"{f['win_rate'] * 100:.0f}%" if f["win_rate"] is not None else "n/a"
        lines.append(f"| {i} | {title} | {f['habitual_count']}/20 | "
                     f"{f['team_count']}/20 | {f['games']} | {wr} |")
    lines.append("")
    lines.append("## Thresholds used")
    lines.extend(f"- `{k}`" for k in [
        "carry_gold_share >= 0.50; carry_damage_share >= 0.60",
        "single_recipient share of capture events >= 0.80",
        "attackers per kill >= 3.0; tribute mean < 25 gems",
        "early kills: kills before round 200 >= 3",
        "farm spread <= 8 tiles (mean pairwise distance of simultaneous clears)",
        "low gem loss: lost carried gems <= 15% of submitted",
        "item family share >= 30% of buys; stat majority >= 50%",
        "wards >= 5/game; linked pair: more bodies than draft picks",
    ])
    lines.append("")
    lines.append("## Per-team per-map detail")
    lines.append("Aggregated per map in [TOP20_MAP_TARGETS.md](TOP20_MAP_TARGETS.md).")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}", flush=True)


if __name__ == "__main__":
    main()
