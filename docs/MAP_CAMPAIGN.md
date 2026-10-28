# Map-specific strategy campaign

Goal: measure retained v22 on each of the 70 published maps against five distinct real-team bot snapshots, then choose and validate a strategy profile for each map. A shared engine can support different drafting, grouping, farming, banking and traversal profiles; these profiles are hypotheses until tested.

## Fixed comparison

- Baseline: pinned v22, submission ff1fc23c-7e9d-42b4-9744-b63a36108c6a; source snapshot bots/apex22.
- Opponents: Ascendance, eclipsed Sunlight, The World Machine, Princess Donut the Queen Anne Chonk, and Knoobs. Four close-rating peers plus the previously tested Ascendance. Actual ratings are checked before each new group, always within +/-200 points.
- 70 maps x 5 opponents = 350 cells. Five compatible historical v22/Ascendance results are reused from the previous frozen analysis; 345 new matches remain at initialization. Related old QS2 results are not mixed into this five-team panel.
- Five maps per group. Each map gets a 3/2 split of our starting sides across its five opponents. First groups establish opponent snapshots; subsequent groups use --source-group to retain those bots.
- Keep v22 fixed throughout the baseline. Do not upload a different strategy halfway through and mix its results into the same matrix.

Eligibility correction: the platform rejected Amba's Strongest Soldiers with HTTP 409 (no eligible bot). No group or result was created for that team. It was replaced by The World Machine before its first accepted request; the rejected intent and original configuration remain archived in the campaign directory.

## Hourly quota and resume safety

The platform permits 50 outgoing match-group requests per hour. Each request schedules five map games, so one five-map group consumes ONE quota slot. The controller reads the official limit/used/resetsAt counter immediately before creation and checks its own recently accepted group IDs as a lower bound against API lag. Incoming challenges do not consume our outgoing quota. A small boundary margin applies to the local ledger.

The earlier 50-individual-game limiter was incorrect and paused the campaign prematurely. At correction, the official counter showed 10 used and 40 available while the old guard reported no room. The user clarified the unit, and raw snapshots also showed one five-game group incrementing used by one. The old configuration/state and evidence are preserved in the campaign directory. All completed results and accepted group IDs were retained; no group was replayed for this correction.

The controller checks live/selected version, source hashes, team identity and ratings before spending. One OS file lock prevents duplicate runners. An ambiguous create outcome is recorded before submission and stops for reconciliation; it is never blindly retried. Successful group IDs are durable. HTTP 429 delays are respected.

If an opponent leaves the rating band, its remaining jobs wait while eligible jobs continue. If the baseline version changes or a request needs reconciliation, the controller stops and records the reason. It never activates a bot or changes Windows settings.

The full 350-game design is 70 five-game groups. One group of compatible historical results is reused, leaving 69 new group requests in the campaign plan. That is two full hourly quota allocations of capacity, not seven; existing usage, rolling expiry, network/runtime and machine sleep affect the actual finish time. See the live matrix for current quota and progress.

The current runner uses `--watch --queue-first`: it submits eligible pending groups before downloading finished summaries. Collection runs after dispatch, or while quota, rating eligibility or an initial opponent snapshot blocks further requests. Live-version, source, rating and quota checks remain in force for each create. Ambiguous requests stop before any further dispatch. Every completed group refreshes the matrix and progress file and prints its collected-result count; read retries print their delay. `queued_groups` means accepted groups awaiting collection, not necessarily games still executing on the server.

The user's additional request to study top teams uses their available historical match data as a separate research sample. The fixed five-peer baseline and its rating band remain intact. Findings about upgrades, Focus and formations need local validation before changing live gameplay.

## Results and analysis

[Live matrix](MAP_MATRIX.md) shows coverage and results. [Preliminary first-block analysis](MAP_FINDINGS.md) covers the first five completed maps only. Each map has a generated worksheet under docs/maps/ with all five opponent results, sides, scores, deaths, carried-gem losses and source match IDs. Before 5/5 coverage the worksheet is explicitly incomplete and makes no strategy decision.

Finished summaries are analyzed once and frozen under matches/map-campaign-v22-20261028/results/. Rendering reads those captures, not newly queried outcomes. Faulty completed games remain in the report. Map layout facts come from the earlier frozen map scan; match hashes remain in stored results for provenance.

After coverage is complete, examine losses by mechanism and propose a profile: objective control and escort on concentrated-gem maps; travel-efficient farming on wide maps; coordinated clears for dangerous groups; traversal for disconnected terrain. Compare each proposed profile against its v22 map baseline locally and then against real teams. Five opponents expose weaknesses; they do not prove an optimal strategy or remove side/opponent effects.

No map-specific gameplay change has been enabled merely by generating these worksheets.

## Commands

Run from D:\Downloads\CambridgeBot:

- Safety checks, no network: `python -X utf8 scripts\map_campaign.py --self-test`
- Initialize/import/render, no online creation: `python -X utf8 scripts\map_campaign.py --prepare`
- One iteration, at most one five-game group: `python -X utf8 scripts\map_campaign.py --step`
- Queue eligible groups before collection, continuing through hourly windows: `python -X utf8 scripts\map_campaign.py --watch --queue-first`
- Re-render saved results only, while no runner holds the lock: `python -X utf8 scripts\map_campaign.py --report`
- Read status without touching the runner: inspect matches/map-campaign-v22-20261028/progress.json and state.json.

Do not launch a second --watch process. Stop normally with Ctrl+C, then resume the same campaign path. If a request is marked submitting/uncertain, reconcile its real group ID before resuming; do not delete the journal to force another request.
