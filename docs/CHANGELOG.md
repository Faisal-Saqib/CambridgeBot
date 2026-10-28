# Strategy changelog

Platform versions are confirmed only by CLI/platform evidence. Candidate labels describe local source changes. Each strategy entry includes its behavior, rationale, risks, verification and release status; see [ONLINE_TESTING.md](ONLINE_TESTING.md) for the five-match iteration rule.

## 2026-10-28 - v24 guarded support released (live, experimental)

- Platform v24, submission `758c6fd5-4884-4477-91ed-78f2b61f2e59` (note 'Guarded support: threat regrouping and carrier escorts'): Live:24 Selected:24, Mode: PINNED VERSION, confirmed after activating 24. Source: bots/apex (byte-identical to bots/guarded, archive matches/top20-cohesion-20261028/guarded-r1-source). v22 (`ff1fc23c-7e9d-42b4-9744-b63a36108c6a`) stays inactive and available as the rollback baseline.
- v24 guarded support is live at the user's explicit request for immediate publication before their Devin weekly quota runs out. Experimental release: local 50/140 against apex22, three WASI protocol tests passed, zero faults across the full 140-game gate; no online candidate results yet. v22 is the preserved rollback baseline. Next gameplay tweak must follow at least five completed v24 online matches, all new opponents currently top20.
- Deferred under the urgent-release direction: 70-map coverage. The old 350-peer campaign is closed, and the top-20 baseline of v22 is complete at 25 games.
- Proposed (not implemented): [Prism carry plan](strategies/prism-carry-plan.md).

## 2026-10-28 - Guarded local experiment (threat-activated support)

- Rejected rigid whole-team cohesion r4 (19/280 broad gate) and started a smaller local candidate, bots/guarded, on apex22: threat-activated support and carrier escort with individual farm claims preserved, no hard movement tether and no shared recall. See [guarded-local.md](strategies/guarded-local.md).
- Focused local panel vs apex22 on six maps, both sides: 2/12 (avg gems 509 - 875), folder matches/panel-guarded-20261028-160047.
- Broad local gate (all 70 maps, both sides, apex22 only): raw count 50/140 (avg gems 663 - 826), folder matches/panel-guarded-20261028-160447. Source frozen in matches/top20-cohesion-20261028/guarded-r1-source. Three WASI protocol tests passed. The candidate is unsubmitted and not live; live v22 is unchanged.
- The old peer campaign is CLOSED to dispatch. The top-20 runner now supports a 70-map campaign, but only the 25 top-20 baseline games have run so far.

## 2026-10-28 - Top-20 policy, fresh baseline and local cohesion candidate

- Policy: every NEW unranked challenge must target a CURRENT rank 1-20 team, rechecked before each request; official quota is 50 outgoing five-map groups per hour. The peer campaign was collected and closed to dispatch (195/350 results saved, 35/70 maps complete, 31 unsubmitted groups will not be sent to those peers); it remains historical.
- Top-team study: 18 observations from 15 distinct ranked games, top three selected across six maps ([findings](TOP_TEAM_FINDINGS.md), [observations](TOP_TEAM_OBSERVATIONS.md)).
- Fresh top-20 baseline of live v22: 1/25 wins on The Line, Anvil, Stampede, Starfish and Expanse against ranks 1, 4, 8, 12 and 16. Ours: 4044 submitted, 555 deaths, 16 kills, 986 carried gems lost, 150 fuel-exhaustion events, 0 faults; opponents: 25687 submitted, 550 kills. Table: [top20-cohesion-baseline.md](top20-cohesion-baseline.md).
- Local cohesion candidate (bots/cohesion, REJECTED, unsubmitted, not live): focused local results against apex22 were r1 0/12, r2 3/12, r3 3/12, r4 0/12 with fixes described in [cohesion-local.md](strategies/cohesion-local.md). Seven WASI protocol tests passed. The r4 broad local gate (all maps, both sides) produced raw counts of 5/140 against apex22 and 14/140 against titan (19/280 total; folder matches/panel-cohesion-20261028-154431); 0 engine-reported faults in all 280 games. Rigid whole-team cohesion r4 is rejected; its source and archives are preserved. No promotion claim; live v22 unchanged.

## 2026-10-28 - Queue baseline requests before collecting results

- Added `--queue-first` scheduling at the user's request. Eligible groups are submitted before summary downloads; collection proceeds after dispatch or while further requests are blocked.
- Preserved the fixed v22 source, five opponents, maps, sides, saved opponent submissions, official group quota and durable intent journal. No gameplay change or new bot submission was made.
- Reconciliation now runs before the dispatch/collection decision. Progress refreshes after each collected group, and read retries print their delays.
- Offline self-tests passed quota boundaries, accepted-group deduplication, version guards, ambiguous-create guards, queue-first ordering, and collection when quota or an initial source snapshot prevents dispatch.
- Began a separate study of top teams' available games and the user's concentrated-upgrade/Focus ideas. These are research candidates, not promoted improvements.

## 2026-10-28 - Correct match-group quota accounting

- The user clarified that one five-map group uses one quota slot. The official counter confirmed 10 used and 40 available.
- The previous individual-game counting caused a premature pause. The scheduler now uses the fresh official group counter plus a local accepted-group ledger.
- All results were preserved and the existing queue resumed without duplicate groups. 69 new group requests cover 345 new games.
- This supersedes the earlier 50-individual-match checkpoint below, which is kept as history.

## 2026-10-28 - Map-specific baseline campaign initialized

- Set up a per-map baseline: fixed pinned v22 on all 70 maps against five real teams (70 x 5 = 350 cells). Five compatible historical v22/Ascendance results are reused; 345 new matches are planned.
- The scheduler caps individual unranked matches at 50 per rolling hour, counting queued matches and reservations, and checks version, quota and ratings before each group. Results are frozen once analyzed, and state is durable so a restart does not requeue completed groups.
- Generated coverage matrix and per-map worksheets are in docs/MAP_MATRIX.md and docs/maps/. No new matches are claimed finished here, the campaign is not complete, and no gameplay change was made. Protocol: [MAP_CAMPAIGN.md](MAP_CAMPAIGN.md).

## 2026-10-28 - retain v22 after 40 online games

- Completed ten online games per version before the next tweak: v20 4/10, v21 2/10, v22 5/10, v23 3/10. Each comparison reused maps, sides, seeds, engine build and requested saved opponent submissions; ratings were checked within +/-200 points.
- Retained v22: normal tribute limits 30/15/5 and threatened/Marcella limits 15/8/5, without wards or the new cohesion mode. Mean tribute 21.43 versus baseline 31.62; total gem loss 1918 versus 1927, so carrier losses remain a weakness.
- Grouping v23 scored 0/5 against Ascendance and 3/5 against QS2. Its full local gate scored 72/140 with no faults, but online results did not support promotion. Archived source and explanation in bots/apex23 and strategies/apex-v23.md.
- Restored working bots/apex to byte-identical apex22, rebuilt, and confirmed pinned Live22/Selected22 (`ff1fc23c-7e9d-42b4-9744-b63a36108c6a`). Zero bot faults across the 40 online games.
- Added explicit saved-batch analysis in scripts/analyze_online_batch.py and preserved results/provenance. Full record: [online cycle](online-cycle-20261027.md). the_line remains unresolved.

## 2026-10-27 - online testing resumed; v21 rejected, v22 trial queued

- `cambc 4.0.0` runs again. Confirmed v20 live, then completed ten baseline online games before any new strategy tweak: 4 wins, 6 losses.
- Submitted the existing smaller-tribute + ward candidate as v21 (`09e1c9c5-23a3-43a4-92c0-d48859558a9e`) after a fault-free 8/10 local panel. Its matched ten-game online result was 2 wins, 8 losses.
- Our mean tribute fell 31.62 to 22.44 gems; deaths rose 134 to 174 and fuel-exhaustion events 284 to 890. No bot faults. These observations do not isolate which part of the combined change caused the regression.
- Selected v20 for rollback; the platform queued a rebuild, so rollback was not immediately effective.
- Removed ward placement only for v22, retaining the smaller banking limits and all other strategy code. Local validation 4/10 with no faults. Submitted as `ff1fc23c-7e9d-42b4-9744-b63a36108c6a`; queued, not yet verified live at this checkpoint.
- Preserved source snapshots and matched-batch evidence. Full record: [online cycle](online-cycle-20261027.md). No unrelated drafting, item, formation or ability change was included.

## 2026-10-27 - resume checkpoint (no gameplay change)

- Added the requirement for at least five completed online matches on a fixed version before each strategy tweak, followed by at least five candidate matches before the next tweak.
- Rechecked the CLI: Windows Application Control still blocks `cambc --version`. No new matches, builds or submissions ran. Current live status is unverified; v20 was the last confirmed live version.
- Preserved the unbuilt v21 candidate and the v20 source baseline. Grouping, consumables and further item changes remain planned.
- Recorded the completed historical item follow-up: apexb3 (opening items, then Capture/Prospector, then Bruiser) won 224/420 local games: 80/140 vs titan, 75/140 vs titanj1, 69/140 vs titanj2. No bot faults were recorded for either side. The separate historical apex follow-up was 67/140 vs titanj2.
- Evidence: [frozen local results](local-panel-followup-2026-10-27.json). These results do not count toward the online minimum, do not prove a gain against Ascendance and lack archived source hashes for exact version attribution. No item change was promoted.
- Corrected the pairing plan: camps choose the nearest champion; enemy bots choose their own targets. A melee partner cannot force opponents to attack it.

## v21 candidate - smaller hauls and wards (not submitted or verified)

- Normal banking: 30 gems anywhere, 15 within 15 tiles of an altar, 5 within 4 tiles.
- Threatened champions and Marcella: 15 anywhere, 8 within 15 tiles, 5 within 4 tiles. Threat means recent nearby enemy sightings, a recent teammate death or health below 60%.
- Place personal wards near altars or toward the enemy side when the previous ward is far away.
- Intended benefit: reduce carried gems lost and improve local information. Risks: extra travel, extra computation and altered combat decisions. Smaller thresholds do not override the existing heal/fight priority or gate/capture exclusions.
- Status: source written earlier in `bots/apex`; no successful build, local test or online test of this candidate yet. Details: [apex-v21](strategies/apex-v21.md).

## v20 - last verified live submission

- Added shared capture of high-value groups, responses to contested captures, and hunting on maps dominated by a harmless gem group.
- Submitted as `38ea3cf0-e36d-4020-ab46-4ff925ca0758`; last CLI verification reported v20 active/live. Frozen source: `bots/apex20`.
- Historical local tests supported the change on the_line, but they do not establish an online fix or absence of regressions. Details: [apex-v20](strategies/apex-v20.md).

## Earlier strategies

- [titan v19](strategies/titan-v19.md): reference Rust bot.
- [C++ main v1-v18](strategies/main-cpp-v1-v18.md) and [squad](strategies/squad-cpp.md): earlier implementations.
- [Experiment log](strategies/experiments-apex.md): local variants, results and limitations.
