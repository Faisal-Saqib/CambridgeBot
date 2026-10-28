# Online testing and iteration

User requirement: finish and analyze **at least five online matches on one fixed bot version before each strategy tweak**. Queued matches and local simulations do not count. Completed games with bot faults remain in the report with their actual win/loss outcome and fault diagnostics; do not silently discard them. Five is the minimum observation batch, not proof of improvement.

## Repeatable cycle

1. Run `cambc --version`, `cambc submissions list` and `cambc match-groups quota --json`. Save the live submission ID/version, quota and timestamp. Stop if the CLI is blocked or a build is still queued.
2. Current user policy (supersedes the earlier +/-200 rating-band step, which remains historical): every NEW unranked challenge must be against a team that is CURRENTLY ranked 1-20, rechecked immediately before each request. Use more than one top-20 team over successive batches. Official quota is 50 outgoing five-map match groups per hour, one group per slot. If the CLI cannot show current ranks, record the missing field before spending quota.
3. Keep a frozen source copy and source/build hashes for each tested candidate. Record group IDs, match IDs, map, side, outcome, opponent and submission attribution. Verify the candidate is live before creating a group. Do not attribute a game by its roster or by the time it was queued; label the version unverified if the platform supplies no conclusive attribution.
4. Complete at least one five-match online group, inspect every result and preserve summaries/replays. Compare score, collection, submissions, carried-gem loss by killer type, deaths, gold, purchases, wards, fuel exhaustion and bot faults. Check event timelines for the proposed mechanism; a score alone is insufficient.
5. Choose one cohesive change supported by that batch. Keep unrelated draft, items, grouping and banking changes separate. Record the hypothesis, intended effect and possible regressions before editing.
6. Build and run focused local regressions on both sides where relevant. Use a broader panel only for a remaining generalization risk or a release gate. A local result above 52% is not automatic approval; maps and related opponents are correlated.
7. Submit only after local verification. Confirm ready/live status, then complete and analyze at least five online matches on the candidate before the next strategy tweak. Compare against the baseline with map, side, opponent and version differences made explicit. Retain, revise or roll back based on both mechanisms and results.
8. Update `CHANGELOG.md`, the candidate's document under `strategies/`, `FULL_STRATEGY.md` and this batch record before starting another iteration. Keep factual results separate from hypotheses and planned behavior.

## Batch record

For every batch record:

- Candidate label; source snapshot and hashes; platform submission ID/version and attribution evidence.
- Own and opponent ratings when selected; quota before/after; group and match IDs.
- Per-match map, side, outcome, score and diagnostics, including failed matches.
- Aggregate metrics with definitions, source paths and coverage/missing-data notes.
- Mechanism supported by events, remaining uncertainties, and the one next change.
- Local verification, online follow-up, decision and known weaknesses.

## Current checkpoint (2026-10-28, top-20 policy)

- CLI works. Historical online batches (rating band +/-200): v20 4/10, v21 2/10, v22 5/10, v23 3/10. v22 (submission ff1fc23c-7e9d-42b4-9744-b63a36108c6a) is now the preserved rollback baseline. Live v24 (guarded support, submission 758c6fd5-4884-4477-91ed-78f2b61f2e59; Live:24 Selected:24, Mode: PINNED VERSION, confirmed after activating 24) runs from bots/apex.
- Latest explicit user policy: every NEW unranked challenge must be against a CURRENT rank 1-20 team, rechecked before each request. The official quota is 50 outgoing five-map groups per hour, one group per slot. The earlier peer campaign was collected and then closed to dispatch: 195/350 old results saved, 35/70 maps complete, and 31 unsubmitted groups will not be sent to those old peers. It remains historical.
- Top-team study: 18 observations from 15 distinct ranked games, top three selected across six maps. See [TOP_TEAM_FINDINGS.md](TOP_TEAM_FINDINGS.md) and [TOP_TEAM_OBSERVATIONS.md](TOP_TEAM_OBSERVATIONS.md).
- Fresh top-20 v22 baseline: 25 completed games on The Line, Anvil, Stampede, Starfish and Expanse against Intercontinental Fish (rank 1), print dont int (4), hello (8), NEETCoders (12) and HBH (16), with all ranks rechecked at create. Result 1/25; the only win was Expanse against print dont int. Our totals: 4044 submitted, 5179 collected, 555 deaths, 16 kills, 55789 gold, 986 carried gems lost (all PvP), 227 tributes, 150 fuel-exhaustion events, 0 faults. Opponents: 25687 submitted, 38 deaths, 550 kills, 235860 gold. Sources: matches/top20-cohesion-20261028/baseline/analysis.json and [top20-cohesion-baseline.md](top20-cohesion-baseline.md).
- bots/cohesion (rigid whole-team formation) is REJECTED, local and unsubmitted; see [strategies/cohesion-local.md](strategies/cohesion-local.md). A smaller local candidate, bots/guarded, is described in [strategies/guarded-local.md](strategies/guarded-local.md). bots/guarded is now live as v24.
- Per-match submission IDs are not exposed online. Attribution uses saved live/selected/source-hash guards and saved-opponent source-group requests. Keep the minimum of five completed online games per fixed version before the next gameplay iteration. Other evidence: [cycle record](online-cycle-20261027.md).
- Raw r4 broad local gate counts (cohesion rejected): cohesion vs apex22 5/140 and vs titan 14/140 over all published local maps and both sides (matches/panel-cohesion-20261028-154431).
- v24 guarded support is live at the user's explicit request for immediate publication before their Devin weekly quota runs out. Experimental release: local 50/140 against apex22, three WASI protocol tests passed, zero faults across the full 140-game gate; no online candidate results yet. v22 is the preserved rollback baseline. Next gameplay tweak must follow at least five completed v24 online matches, all new opponents currently top20.
