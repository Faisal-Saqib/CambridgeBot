# Bot strategies and versions

- [FULL_STRATEGY.md](FULL_STRATEGY.md): compact explanation of implemented and planned behavior.
- [PLAN.md](PLAN.md): priorities, hypotheses and risks.
- [CHANGELOG.md](CHANGELOG.md): changes, evidence, verification and release status.
- [ONLINE_TESTING.md](ONLINE_TESTING.md): at least five completed online matches before each strategy tweak, rating selection and version tracking.
- [MAP_CAMPAIGN.md](MAP_CAMPAIGN.md): protocol for the per-map, five-team baseline campaign.
- [MAP_MATRIX.md](MAP_MATRIX.md): generated live coverage and results matrix.
- [MAP_FINDINGS.md](MAP_FINDINGS.md): reviewed findings from completed five-opponent map blocks (currently the first five maps).
- [TOP_TEAM_FINDINGS.md](TOP_TEAM_FINDINGS.md) and [TOP_TEAM_OBSERVATIONS.md](TOP_TEAM_OBSERVATIONS.md): study of top-ranked teams' games.
- [TOP20_STRATEGY_CENSUS.md](TOP20_STRATEGY_CENSUS.md): strategy patterns across all top-20 teams, ordered by prevalence (1,040 downloaded ranked matches).
- [TOP20_MAP_TARGETS.md](TOP20_MAP_TARGETS.md): per-map top-20 behaviour and 10 target points per map.`n- [TOP20_DEEP_ANALYSIS.md](TOP20_DEEP_ANALYSIS.md): deep per-team breakdown — drafts, item builds, wards, traversal, reward distribution (1,124 matches).
- [HANDOFF_PROMPT.md](HANDOFF_PROMPT.md): self-contained brief for the next implementation cycle.
- [top20-cohesion-baseline.md](top20-cohesion-baseline.md): generated match table for the fresh top-20 v22 baseline.
- [strategies/cohesion-local.md](strategies/cohesion-local.md): rejected local whole-team formation experiment (unsubmitted).
- [strategies/guarded-local.md](strategies/guarded-local.md): v24 guarded support (live, experimental).
- [strategies/prism-carry-plan.md](strategies/prism-carry-plan.md): proposed Prism carry experiment (not implemented).
- [TACTICAL_CANDIDATES.md](TACTICAL_CANDIDATES.md): user-proposed tactics and source findings; not yet validated or enabled.

| Strategy | Source | Status |
| --- | --- | --- |
| [C++ main v1-v18](strategies/main-cpp-v1-v18.md) | bots/main | Historical |
| [C++ squad](strategies/squad-cpp.md) | bots/squad | Shelved experiment |
| [titan v19](strategies/titan-v19.md) | bots/titan | Reference opponent |
| [apex v20](strategies/apex-v20.md) | bots/apex20 | Historical baseline |
| [apex v21](strategies/apex-v21.md) | bots/apex21 | Archived/rejected (2/10 online) |
| [apex v22](strategies/apex-v22.md) | bots/apex22 | Rollback baseline (inactive, preserved) |
| [apex v23](strategies/apex-v23.md) | bots/apex23 | Archived grouping trial; 3/10 online |
| [cohesion (local)](strategies/cohesion-local.md) | bots/cohesion | Rejected local experiment (19/280); unsubmitted |
| [apex v24 guarded support](strategies/guarded-local.md) | bots/apex / bots/guarded | Live 24 (experimental, released at user request) |
| [Experiments](strategies/experiments-apex.md) | bots/apexb*, bots/hunter, others | Historical local variants |

## Current checkpoint (2026-10-28)

The CLI works. Forty online games completed: v20 4/10, v21 2/10, v22 5/10, v23 3/10. Those results are v22's historical record; **v24 guarded support is now live** (Live:24 Selected:24, Mode: PINNED VERSION, submission `758c6fd5-4884-4477-91ed-78f2b61f2e59`), released at the user's explicit request with no online v24 results yet. v22 is the preserved rollback baseline; working bots/apex is the v24 source. Each version had ten completed online games before the next tweak.

See [the cycle record](online-cycle-20261027.md) for results, attribution and limitations. the_line remains unresolved. The v23 grouping implementation is preserved under bots/apex23 rather than enabled in the live bot.

[Historical item-panel follow-up](local-panel-followup-2026-10-27.json): 224/420 wins for apexb3; no item change was promoted in this cycle.

## Commands

- Live state: `cambc submissions list`
- Quota: `cambc match-groups quota --json`
- Queue five unranked games after rating/version checks: `cambc match-groups create <TEAM_ID>`
- Recent results: `python scripts\online_report.py --limit 30`
- Opponent report: `python scripts\opponent_report.py Ascendance`
- Local comparison: `python scripts\panel.py apex --opps apex20 --maps 00the-line 00anvil 00expanse 02crossing --quiet`

The current online report scripts require a working CLI. Preserve match IDs and submission attribution separately; roster alone does not establish a version.

## Per-map baseline (old peer campaign closed)

The old peer campaign is closed with 195/350 results saved and 35/70 maps completed against all five peers. Further coverage will use current top-20 teams; only 25 top-20 baseline games have run so far. The runner supports the 70-map campaign and respects 50 outgoing five-map groups per hour. [MAP_MATRIX.md](MAP_MATRIX.md) retains the historical peer results; v24 is the live strategy (experimental); 70-map coverage is deferred under the user's urgent-release direction.

## Top-20 checkpoint (2026-10-28)

New unranked challenges must target a CURRENT rank 1-20 team (official quota: 50 outgoing five-map groups per hour). The old peer campaign was closed to dispatch with 195/350 results saved. Fresh top-20 baseline of v22 (25 games complete): 1/25 wins over 25 games against five top-20 teams; see [top20-cohesion-baseline.md](top20-cohesion-baseline.md) and [TOP_TEAM_FINDINGS.md](TOP_TEAM_FINDINGS.md). The rigid cohesion candidate was rejected (19/280 broad local gate) and remains local and unsubmitted; the smaller guarded candidate is now live as v24 (experimental). v24 guarded support is live at the user's explicit request for immediate publication before their Devin weekly quota runs out. Experimental release: local 50/140 against apex22, three WASI protocol tests passed, zero faults across the full 140-game gate; no online candidate results yet. v22 is the preserved rollback baseline. Next gameplay tweak must follow at least five completed v24 online matches, all new opponents currently top20.
