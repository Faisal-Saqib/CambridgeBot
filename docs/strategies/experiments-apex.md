# apex experiments (not submitted)

All measured against titan or apex over all 70 maps, both sides, unless noted. Results are historical deterministic comparisons. Small differences and related opponents do not establish statistical significance; debug logging can alter execution under fuel limits.

| Variant (bot dir) | Change | Result | Verdict |
| --- | --- | --- | --- |
| hunter / apex HUNT | Aggressive everywhere: take even fights, join from further away, chase hurt enemies | 61–79 vs titan (3-pick 12–12, 4-pick 13–19, 5-pick 36–48) | Off; kept only for brawl maps (v20) |
| apex C&I draft | Cassi & Issac in every draft (extra body) | 52–88 vs titan | Rejected |
| apex Vendetta draft | Vendetta in the 3/4-pick drafts | 4–12 on 16 small-map games | Rejected |
| apex ball | 3-pick team moves as one group | 8–8 on 16 small-map games | Neutral; off |
| apex standoff | Leave a ranged standoff after 8 turns without hits | 65–75 vs titan | Off |
| apexb1 | Capture emblem first, then titan's build | 60–80 vs apex v20 | Rejected (delays combat items) |
| apexb2 | Capture first + Prospector + Power stacking (Ascendance-style) | 60–80 vs apex v20 | Rejected in this form |
| apexb3 | titan opening, then Capture + Prospector, then Bruiser | 75-65 vs apex v20; later 224-196 vs titan/titanj1/titanj2 (420 games) | Candidate only; not promoted |

## Tools made along the way
- `titanj1..3`: titan with small deterministic perturbations to job scores. These are related sparring variants, not independent random trials. The earlier fuel-only perturbation did not change the tested outcomes.
- `titandbg`, `apexdbg`: debug-logging builds (`DEBUG = true`).
- `reachscan` (C++): prints, for every map, gems reachable only by teleport crystal plus map shape, then resigns. Only 01islands (372/608) and 02the-pond (70/148) have many gems cut off.
- `itemscan` (Rust): dumps the engine's item table (stats, passive, magnitude, cost).
- `scripts/panel.py`: one bot against a panel of opponents, many maps, both sides, in one parallel batch.
- `scripts/online_report.py`, `scripts/opponent_report.py`: download and summarise online matches; deep-dive one opponent.

## Recovered follow-up (2026-10-27)

The previously started panel completed: apexb3 won 80/140 vs titan, 75/140 vs titanj1 and 69/140 vs titanj2 (224/420 total); neither side recorded a bot fault. The separate historical apex follow-up won 67/140 vs titanj2. [Frozen evidence](../local-panel-followup-2026-10-27.json) records source manifests, coverage and limitations. These were existing local results, not fresh online matches, and no additional gameplay change was made.
