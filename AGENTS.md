# Battlecode bot working notes

## Commands

- Build: `cambc build main` (ignore the PowerShell `RemoteException` wrapper noise; look for `built ... bot-injected.wasm`).
- Local test: `cambc run main starter-cpp --map <map>` — deterministic, so one run is a reliable comparator.
- Submit: `cambc submit main`; `cambc submissions list` shows live version.
- Online groups: `cambc match-groups create <TEAM_ID>` (5 matches), `quota --json` shows `opponentRanks` (id→global rank) — pick opponents near our `requesterRank`.
- Summaries: `cambc matches summary <MATCH_ID> --json` writes `match-<id>.json`; `.camstat` files need `cambc summary <file> -o out.json`. `matches download` gives replay bundles (team stdout inside the zip).

## Engine/game facts learned

- 100k fuel per champ turn; exhaustion suspends mid-turn. `World::refresh()` was the hog — cached statics + staggered group polls halved it.
- Matches are deterministic locally (same code+map → same result).
- Recall is cancelled by any damage; tribute is NOT cancelled by damage; TP crystals channel 3 ticks and ignore terrain/damage-cancel.
- Killer steals carried gems in PvP; camps destroy carried gems.
- Cassi & Issac = two bodies per draft pick (linked death). Ryth's AoE stun is ground-targeted (needs `ab.use(tile)`).
- Camps stay damaged after partial clears — suicide-chipping works, but deaths cost ~60 rounds + carried gems.

## Strategy evolution (what worked)

- Draft: Vendetta, Vesper, C&I (2 bodies), Varg, Ryth (tank outperforms Willow online), then Willow, Tavi, Marcella, HoR, Ren, Prism, Stellar.
- Group score = value/(walk)/(lives-lost); monolith-class groups need scarcity boost or raid convergence.
- Scarcity raid: group holding >60% of remaining gems gets ×3 score → deterministic full-team converge (stampede 0→640).
- Death-blacklist: champ that died attacking group G avoids it ~80 rounds (kills respawn-die loops vs camped monoliths, e.g. lost_world).
- Flee: under-fire detection uses attack range OR hp-drop with no awake camp in range (catches ability poke). Twins bail earlier (linked death costs 2 bodies).
- Fight-back: when not outnumbered/hurt and carrying ≤3 gems.
- TP crystals bought like locks; used to cross hole-separated components (islands 265→1013) and blink out of hunts.
- Shopping trips on idle gold; Tavi buys anywhere; jungle item family best for us.

## titan (user's Rust bot, live as v19) — current best

- `bots/titan` (Rust, `cambc build titan`). Beat our C++ `main` 24-0 (12 maps, both sides), usually reaching 1000 gems by round ~700-1700.
- Design: per-champion group claims in shared memory (bytes 0-5), team focus target (byte 6), monolith-gate assault flag (byte 7); job score = value / (travel + respawn wait + clear time + HP cost priced as trips home) / claimants; fights decided by time-to-kill comparison; static distance fields copied into wasm memory (cheap fuel).
- Online (v19): ~23-7. Losses: 00the_line every time (opponents with 5 bodies via C&I or heavy melee out-farm us), and 3-pick maps (anvil/arena/gold_rush) against one aggressive Vesper/Vendetta/Marcella team (20-25 deaths, 0 kills).
- Experiments in `bots/apex` (copy of titan), all measured against titan over all 70 maps, both sides (140 games): hunting/aggression 61-79, C&I in every draft 52-88, standoff exit 65-75; Vendetta small-map draft 4-12 and 3-pick deathball 8-8 on 16 small-map games. None beat titan; all are switched off in apex.
- Mirror games are chaotic: tiny fuel/timing changes (even debug logging) flip single games, and identical code splits by side on 4/5-pick maps. Only judge changes on the full 140-game gauntlet (`python scripts\gauntlet.py <a> <b> --jobs 8`), ±6 wins is noise.
- Unreachable-on-foot gems (needs TP crystals): 01islands 372/608, 02the-pond 70/148; every other map < 10%.

## Failure modes seen online

- Elite teams (rank ≤25) out-hunt us 3-5x deaths — do not test only against them; use rank ±~200 peers.
- Maps with all gems inside one boss group (stampede, lost_world, guardians) need raid/blacklist logic.
- Forced-brawl maps (the_line) punish spread farming.

## Current iteration rules (2026-10-27; supersedes historical testing notes)

- User requires at least five completed online matches on a fixed version before each strategy tweak and at least five candidate online matches before the next tweak. Record all finished games, including faults.
- Choose opponents by actual rating within approximately +/-200 points; rank is not rating. Confirm the live submission and preserve per-match attribution; do not infer it from the roster or queue time.
- `bots/apex20` is the frozen source baseline; `bots/apex` is the unbuilt v21 candidate (smaller tribute limits plus wards). v20 was last verified live. Current server state is unverified because Windows Application Control still blocks cambc.
- Preserve user edits to bot sources. No new strategy tweak while fresh online testing is blocked.
- Update docs/CHANGELOG.md, docs/FULL_STRATEGY.md and the candidate version document for every iteration. Workflow: docs/ONLINE_TESTING.md. Historical 52% or +/-6-win heuristics are not proof of improvement.

2026-10-27 update: CLI restored. Baseline v20 and trial v21 each completed ten online games (4/10 and 2/10 wins). v21 source frozen in bots/apex21; working apex is the submitted banking-only v22 trial, frozen in bots/apex22. Last observed Live21/Selected22, v20 rollback rebuild queued. Consult docs/online-cycle-20261027.md and fresh CLI state; the previous Windows-blocked checkpoint is historical.

2026-10-28 retained state: CLI works; pinned Live22/Selected22 confirmed (ff1fc23c-7e9d-42b4-9744-b63a36108c6a). Primary working bot is Rust bots/apex, byte-identical to bots/apex22; it uses smaller tribute limits without wards or the v23 cohesion mode. Forty online matches: v20 4/10, v21 2/10, v22 5/10, v23 3/10. v23 source remains in bots/apex23. Full local v23 gate 72/140, no faults. Keep the user's five-completed-online-matches-before-tweak rule; see docs/online-cycle-20261027.md. Earlier blocked/queued-state notes are historical.

2026-10-28 map-campaign instruction: user requests each published map tested against five real teams before map-specific strategy decisions. Campaign config/state: matches/map-campaign-v22-20261028/. Baseline pinned v22; strict 50 individual unranked matches per rolling hour (count queued matches and reservations, not just group counter). scripts/map_campaign.py may already be running: inspect progress/state and existing process before launching anything; never duplicate a runner or blindly retry an uncertain create. Generated docs/MAP_MATRIX.md and docs/maps/*.md read frozen result records. Do not change the baseline live version during this campaign without explicitly stopping it for the user's new direction.

Quota correction 2026-10-28: the user clarified, and API snapshots confirm, that one five-map group consumes ONE quota unit. Respect 50 outgoing match-group requests per hour using official quota and accepted-group ledger. The earlier 50-individual-match instruction/accounting was incorrect and is superseded. Corrected scripts/map_campaign.py is running; inspect progress.json/PID before any launch. Do not duplicate groups or edit live baseline v22 during the map campaign.

2026-10-28 queue-first/research update: the saved map campaign now runs with `python -X utf8 scripts/map_campaign.py --watch --queue-first`. Queue eligible groups first, then collect; report refreshes occur per completed group. Check PID/state before any resume and never start a second runner or blindly retry an uncertain create. The user also requests analysis of top teams' available games, concentrated upgrades on one champion with support, and Focus/coordinated targeting. This research is separate from the fixed five-peer v22 baseline; preserve live v22 throughout collection.

2026-10-28 latest user direction (supersedes peer selection and continued peer dispatch): EVERY NEW unranked challenge must target a team currently ranked 1-20. Check the current ladder immediately before each create; the earlier +/-200 rating filter no longer applies. The old peer campaign is closed to new requests via dispatch_disabled_reason; collect only already accepted matches. Build and validate a whole-team cohesion candidate, then compare against saved top-20 opponent submissions on matched maps/sides/seeds. Keep the five-completed-online-matches-before-tweak rule, preserve all old results, and never retry an uncertain create without reconciliation.

2026-10-28 authoritative checkpoint: platform v24 (guarded support, submission 758c6fd5-4884-4477-91ed-78f2b61f2e59) is live and selected (Live:24 Selected:24, Mode: PINNED VERSION, confirmed after activating 24), released at the user's explicit request for immediate publication before their Devin weekly quota runs out. bots/apex is the v24 source, byte-identical to bots/guarded; bots/apex22 and platform v22 (ff1fc23c-7e9d-42b4-9744-b63a36108c6a) are the preserved rollback baseline. Experimental: local 50/140 against apex22, three WASI protocol tests passed, zero faults across the 140-game gate, no online v24 results yet. Next gameplay tweak must follow at least five completed v24 online matches, all new opponents currently top20. The old peer campaign is closed; the 25-game top-20 baseline of v22 is complete; 70-map coverage is deferred. Earlier notes calling v22 live are historical. Proposed idea: docs/strategies/prism-carry-plan.md.
