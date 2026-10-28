You are continuing work on my Cambridge Battlecode 2026a (CAMBC) bot in this repo (D:\Downloads\CambridgeBot, Windows, PowerShell). Read AGENTS.md, docs/HANDOFF_PROMPT.md, GameRules.md (use bots/GameRules.md — it is the newer engine-2.0 rules copy) and docs/strategies/guarded-local.md first.

## Current state
- Live on the platform: v24 "guarded support" = bots/apex (also frozen as bots/guarded), submission 758c6fd5-4884-4477-91ed-78f2b61f2e59. Rollback baseline: bots/apex22 (v22, ff1fc23c-7e9d-42b4-9744-b63a36108c6a). Do not edit apex, apex22, guarded or titan.
- v22 went 1/25 against top-20 teams (docs/top20-cohesion-baseline.md).

## What the last session found (evidence in matches/top-team-study-20261028 and matches/top20-cohesion-20261028/baseline)
1. Engine 2.0 added emblem families v24 never buys: Capture (team capture capped at 3 rounds instead of 5), Prospector (+25% of cluster share), Tribute (33% shorter tribute), Hunter, Skirmish (+5% vs champions), Greed, Collectors (+1% dmg per unique family). Top teams buy Monster/Capture/Prospector/Collectors on farmers. Monster is now +15%, Treasure +10%.
2. Expanse (pure farming): we die ~0-2 times but deal ~100k camp damage vs their 130-175k. Our Willow/Tavi are weak farmers; their Vendetta/Varg deal 35-50k each.
3. Anvil (3 picks): we die 20-30 times with 0-1 kills; every winner there drafted two of Marcella / Vesper / Heart of Ruin.

## New candidate bots (built, compile cleanly)
- bots/forge-shop = v24 + new shop build only (src/shop.rs): Monster, Capture, survival emblems (Jungle/Durability Health), Collectors, Prospector, then Bruiser; Vesper adds Treasure; Heart of Ruin uses Focus.
- bots/forge = forge-shop + top-team draft (src/draft.rs: 3 picks Marcella/Vesper/HoR; 4 picks Vesper/Vendetta/HoR/Marcella; 5 picks Vesper/Vendetta/HoR/Varg/Marcella) + guard-leader priority for the new champions (src/guard.rs).
- BROAD GATE RESULTS (280 games each, all 70 maps, both sides): forge-shop 75/140 vs apex (avg gems 740-728) and 60/140 vs apex22 (706-775) — better than v24's own 50/140 vs apex22. forge (with the new draft) 23/140 vs apex and 26/140 vs apex22 — the draft change is strongly negative with our current behaviour code; drop it unless the play logic is adapted to those champions. forge-shop is the promotion candidate (ask me before submitting).
- Focused 24-game local panel (6 maps, both sides, vs apex and apex22): forge-shop 10/24, forge 8/24 — too noisy to judge. A broad gate (all 70 maps, both sides, vs apex and apex22 = 280 games each) was started at 21:34 via the job runner; results are in .claude_jobs/out/004-gate-broad.log and matches/panel-forge-shop-<timestamp>/ and matches/panel-forge-<timestamp>/. For reference, v24 scored 50/140 vs apex22 locally.

## Tooling notes
- Build: `cambc build <bot>`. Local panel: `py -X utf8 scripts\panel.py <bot> --opps apex apex22 --maps <maps> --jobs 8` (omit --maps for all 70). ~1 minute per 24 games.
- Map file names use hyphens: 00the-line, 02treasure-box, 00lost-world, etc. (not underscores).
- .claude_jobs/ holds a job runner the previous session used because it had no shell; you can ignore it (close its PowerShell window "Claude runner" if it is still open, after 004-gate-broad finishes).

## Your task
1. Read the broad gate results (or rerun it). Compare forge-shop and forge against apex and apex22, with per-map breakdowns; check items bought, camp damage, gold, deaths and captures in the stats JSONs to confirm mechanisms, not just win counts.
2. Iterate on these candidates (one change per version, each frozen in its own bots/<name> folder, never edit apex/apex22/guarded). Priorities: (a) farm speed (item order, draft), (b) PvP survival on brawl maps (anvil, the_line, stampede, starfish) — focus fire on killable targets, earlier retreat, carriers banking sooner; (c) map-specific profiles.
3. Local mirror games are a weak proxy (our old bots don't buy the new items). The real test is online vs top-20 teams. Do NOT submit or activate a new platform version without asking me first. When I approve: submit, confirm live, then play at least 5 online games vs teams currently ranked 1-20 (recheck rank before each create, never blindly retry an uncertain create), and record every result.
4. Keep docs updated: docs/CHANGELOG.md, docs/FULL_STRATEGY.md, docs/strategies/<version>.md, AGENTS.md. No claimed improvement without numbers.
