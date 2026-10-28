# Online strategy cycle - 2026-10-27 to 2026-10-28

Final decision: retain **v22**, confirmed live and selected in pinned mode as `ff1fc23c-7e9d-42b4-9744-b63a36108c6a`. Working `bots/apex` matches frozen `bots/apex22` and builds. v21 and v23 remain archived experiments.

## Comparison design

Forty completed online games: ten per version, five against Ascendance and five against QS2. Every batch was analyzed before the next strategy tweak, exceeding the user's five-match minimum.

The five maps were the_line, treasure_box, crossing, expanse and starfish. Our sides against Ascendance were a,b,a,b,a; against QS2 b,a,b,a,b. Follow-ups requested the original opponent submissions with `--source-group`. All matched map hashes, sides, seeds and engine builds were checked. Opponents were within +/-200 actual rating points when each group was created; exact ratings are in the saved group records.

These are limited deterministic comparisons against two related sets of opponents, not a statistical estimate of the whole ladder. Per-match submission IDs are not exposed by the CLI. Own versions are supported by the saved live-state checks before/after completed batches and no intervening submission; roster is not used as version evidence.

## Online results

| Version | Change | Ascendance | QS2 | Overall | Decision |
| --- | --- | --- | --- | --- | --- |
| v20 | Baseline | 1-4 | 3-2 | 4-6 | Reference |
| v21 | Smaller tribute limits + wards | 0-5 | 2-3 | 2-8 | Reject combined implementation |
| v22 | Smaller tribute limits only | 3-2 | 2-3 | 5-5 | Retain |
| v23 | v22 + melee/ranged cohesion | 0-5 | 3-2 | 3-7 | Reject this grouping implementation |

| Our metrics, ten games each | v20 | v21 | v22 | v23 |
| --- | --- | --- | --- | --- |
| Submitted gems | 6419 | 6037 | 7242 | 5633 |
| Collected gems metric | 8799 | 7968 | 9365 | 7141 |
| Gems lost on death | 1927 | 1743 | 1918 | 1352 |
| Deaths | 134 | 174 | 125 | 163 |
| Champion kills | 42 | 52 | 69 | 33 |
| Gold earned | 40403 | 35930 | 42299 | 29524 |
| Completed tributes | 203 | 269 | 338 | 287 |
| Mean gems per tribute | 31.62 | 22.44 | 21.43 | 19.63 |
| Ward placements | 0 | 2337 | 0 | 0 |
| Fuel exhaustion events | 284 | 890 | 263 | 284 |
| Bot faults | 0 | 0 | 0 | 0 |

Metrics are totals, not duration-adjusted rates. Fuel counts include initialization and per-champion suspensions; they are not crashes. Completed tribute totals were checked against team and champion score totals; death and kill totals against events.

## Interpretation

- v22 banks smaller hauls and had the strongest online outcome in this panel, including 3/5 against Ascendance versus baseline 1/5. Its total gem loss was almost unchanged, so carrier safety is not solved.
- The v21 combined change produced smaller tributes but more deaths and fuel suspensions. The ablation favored v22; the data does not prove that ward placement alone caused every regression or that wards are inherently bad.
- v23 reduced raw gem losses while also collecting and submitting fewer gems. Its grouping implementation did not justify replacing v22. The code remains available in `bots/apex23` for further work.
- Every online the_line test was lost. v22 still banked zero there against both opponents. Local success on that map must not be reported as an online fix.

## Local verification

v21 won 8/10 against v20; v22 won 4/10 against v20. v23 won 7/12 against v22 on six maps, including three-, four- and five-pick drafts. A full v23 comparison then covered all 70 maps on both sides: 72 wins, 68 losses, zero bot faults on either side. This modest local result did not outweigh the online regression. The initial full-map attempt failed before producing games; its successful retry is the only completed full gate.

The restored working v22 source matches its frozen snapshot and compiled successfully. No redundant match suite was rerun after restoration.

## Evidence and versions

All raw data and immutable analyses are under `matches/online-cycle-20261027/`: `baseline-analysis.json`, `v21-analysis.json`, `v22-analysis.json`, `v23-analysis.json`, the comparison JSONs, local-analysis JSONs, source hashes, CLI captures and group records. Summaries are cached by full match ID under `matches/online/`. `scripts/analyze_online_batch.py` analyzes explicit saved groups with identity/coverage/metric checks; it never selects a recent-match sample implicitly.

| Platform version | Submission ID | Frozen source |
| --- | --- | --- |
| v20 | 38ea3cf0-e36d-4020-ab46-4ff925ca0758 | bots/apex20 |
| v21 | 09e1c9c5-23a3-43a4-92c0-d48859558a9e | bots/apex21 |
| v22 | ff1fc23c-7e9d-42b4-9744-b63a36108c6a | bots/apex22 |
| v23 | 08ae3185-ed3d-447e-b1ac-7d3c62db691a | bots/apex23 |

Final live-state evidence: `platform-final-state.json` and `final-live-status.txt`. Selecting an inactive version queued a platform rebuild; restoration was only declared complete once the CLI reported Live22/Selected22.

## Remaining work

Investigate delivery and combat priority on the_line, actual carrier routes and altar-lock interactions. Revisit grouping only with evidence about separation and farming cost; permanent regrouping is not automatically beneficial. Personal wards, items, escape tools and new formations remain separate experiments, each requiring a completed online batch before another tweak.

A separate ccprobe produced no diagnostic output, so the Ryth ability-targeting hypothesis remains unresolved. No production ability change was made on that evidence.
