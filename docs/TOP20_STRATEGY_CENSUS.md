# Top-20 strategy census

Strategies measured from downloaded ranked summaries of the current top-20 ladder teams (matches/top20-scout, `scripts/top20_scout.py` + `scripts/strategy_census.py`). Ordered by how many of the 20 teams exhibit each pattern in the sampled games.

Sample: 1040 matches analyzed, 1869 top-20 team-games (0 incomplete skipped). A team counts as **ever using** a strategy if at least one sampled game meets the threshold; **habitual** means the threshold is met in at least half of that team's sampled games. Win rate is across the feature's games.

Caveat: historical bot versions are unknowable; ranks are capture-time. Prevalence is not proof of causality — it shows what the best teams do, not necessarily why they win.

| Rank | Strategy point | Habitual | Ever used | Games | Win rate |
| --- | --- | --- | --- | --- | --- |
| 1 | Regular ward placement | 20/20 | 20/20 | 1807 | 51% |
| 2 | Low carried-gem losses (protected carriers / early banking) | 20/20 | 20/20 | 1287 | 67% |
| 3 | One champion captures; allies zone or farm | 19/20 | 20/20 | 1706 | 52% |
| 4 | Bruiser-family stat builds | 18/20 | 20/20 | 1315 | 58% |
| 5 | Altar locks | 12/20 | 14/20 | 1144 | 49% |
| 6 | Teleport crystals | 9/20 | 17/20 | 781 | 48% |
| 7 | Group kills with 3+ credited attackers | 7/20 | 20/20 | 840 | 45% |
| 8 | Strength-majority item builds | 4/20 | 18/20 | 453 | 49% |
| 9 | Concentrated gold on one carry (>=50% team share) | 3/20 | 20/20 | 659 | 54% |
| 10 | Health-majority item builds | 3/20 | 17/20 | 419 | 51% |
| 11 | Small frequent tributes (<25 gems mean) | 2/20 | 20/20 | 409 | 35% |
| 12 | Linked-pair drafts (Cassi & Issac, 5 bodies) | 1/20 | 7/20 | 149 | 60% |
| 13 | Concentrated champion damage (>=60% on one champ) | 0/20 | 20/20 | 333 | 53% |
| 14 | Early aggression (3+ kills before round 200) | 0/20 | 20/20 | 224 | 80% |
| 15 | Tight clustered farming (<=8-tile spread) | 0/20 | 20/20 | 181 | 59% |
| 16 | Focus-majority item builds | 0/20 | 15/20 | 119 | 46% |
| 17 | Jungle-family builds | 0/20 | 14/20 | 107 | 27% |
| 18 | Treasure-family builds | 0/20 | 12/20 | 128 | 27% |
| 19 | Prospector-family builds | 0/20 | 10/20 | 129 | 34% |
| 20 | Other/unclassified item families | 0/20 | 10/20 | 67 | 58% |
| 21 | Durability-family builds | 0/20 | 4/20 | 8 | 12% |
| 22 | Capture-family builds | 0/20 | 3/20 | 9 | 44% |
| 23 | Monster-family builds | 0/20 | 3/20 | 5 | 20% |

## Thresholds used
- `carry_gold_share >= 0.50; carry_damage_share >= 0.60`
- `single_recipient share of capture events >= 0.80`
- `attackers per kill >= 3.0; tribute mean < 25 gems`
- `early kills: kills before round 200 >= 3`
- `farm spread <= 8 tiles (mean pairwise distance of simultaneous clears)`
- `low gem loss: lost carried gems <= 15% of submitted`
- `item family share >= 30% of buys; stat majority >= 50%`
- `wards >= 5/game; linked pair: more bodies than draft picks`

## Per-team per-map detail
Aggregated per map in [TOP20_MAP_TARGETS.md](TOP20_MAP_TARGETS.md).
