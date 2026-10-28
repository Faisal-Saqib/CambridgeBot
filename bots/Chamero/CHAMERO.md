# Chamero

Our own bot line, kept in this folder only (no other files in the repo were edited).

## v1 (platform v25, submission 3b0b5c5c-2678-4703-bcf0-092db6c7ef4b, uploaded 2026-10-28)

Source = `bots/forge-shop` exactly: live v24 "guarded support" plus the engine-2.0
item build in `src/shop.rs` (Monster, Capture, Jungle/Durability Health, Collectors,
Prospector, then Bruiser; Vesper adds Treasure; casters and Heart of Ruin build Focus).

Why this base (local broad gate, all 70 maps, both sides):

| Bot | vs apex (v24) | vs apex22 (v22) | Total |
| --- | --- | --- | --- |
| forge-shop = Chamero v1 | 75/140 | 60/140 | 135/280 |
| forge (new draft + shop) | 23/140 | 26/140 | 49/280 |
| v24 reference | - | 50/140 | - |

### Online batch 1 (2026-10-28): 0/5

Opponent Intercontinental Fish, rank 2 when the group was created (ladder saved in
`online/ladder-before-g1.json`; Live 25 / Selected 25 checked just before, saved in
`online/live-before-g1.txt`). Group `7614fbf5-7063-40d8-8fc4-0a84af1998d0`, created with
`--source-group 45794a53-7c33-4441-98d3-fe510800b398`, so it played the same opponent
bot, maps and sides as the saved v22 top-20 baseline. Raw files in `online/`.
Version attribution: the platform does not report a submission per match; v25 was the
only live version before and after the games.

| Map | Side | Result | Gems for-against | Deaths | Kills | Camp damage us/them | v22 baseline |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| 00the_line | a | loss | 0-1030 | 23 | 0 | 3.5k / 39.5k | 0-1022, 21 deaths |
| 00anvil | b | loss | 84-1005 | 20 | 1 | 7.6k / 102k | 176-1132, 18 deaths |
| 00stampede | a | loss | 0-1120 | 45 | 1 | 6.8k / 141k | 0-1040, 40 deaths |
| 01starfish | b | loss | 52-1010 | 26 | 4 | 30.6k / 143k | 23-1010, 26 deaths |
| 00expanse | a | loss | 410-1022 | 1 | 0 | 85k / 161k | 503-1015, 1 death |

Bot faults: 0 in all five. Same result as v22 against this bot (0/5); no improvement shown.

On Expanse (pure farming, almost no fighting) they did twice our camp damage. Their
items: every champion bought Monster + Jungle Health, then stacked **Power** emblems on
its main stat (Varg 12 Power-Strength, Vendetta 10, Heart of Ruin 8 Power-Focus). They
bought no Capture, Collectors, Prospector or Durability. Draft: Vesper, Vendetta, Heart
of Ruin, Varg, Cassi & Issac. Candidate for Chamero v2: shop = Monster(main),
Jungle(Health), then Power(main) for the rest of the game.

## v2 (platform v26, submission 11187ba5-9f2f-4b52-b752-c8c06e5ba091)

Source frozen in `versions/v2/src`. Two changes on top of v1:

1. **Respawn-wait bug fix** (`farm.rs`, `bot.rs`). When a champion's best job was a
   respawning camp it stood still wherever it was; after 6 idle turns the stuck guard
   banned that camp for 30 rounds, so it walked off just before the respawn. Now it
   walks to within 2 tiles and waits, and waiting does not count as stuck. On a
   300-round Expanse run, stuck events went from 15 to 0.
2. **Value gold early** (`farm.rs` job value): gold weight 0.4 before round 400, 0.15
   before 800, 0.03 after (was 0.15 / 0.08 / 0.03 with switches at 300 and 800).

Why: in the v25 online Expanse game we matched the rank-2 team's gold at round 200
(1100 vs 1063) but then stalled. From round 200 to 500 they added 48k camp damage and
we added 16k (`online/curves-g1.txt`).

Local gate (280 games, both sides, vs apex and apex22), per game for our team:

| Version | Wins | Gems | Camp damage | Gold | Deaths |
| --- | --- | ---: | ---: | ---: | ---: |
| v1 | 135/280 | 723 | 66.3k | 4.8k | 13.9 |
| v1 + respawn fix | 126/280 | 733 | 69.0k | 4.9k | 14.4 |
| v2 (+ gold early) | 128/280 | 746 | 74.2k | 5.3k | 13.5 |

Wins are within mirror-game noise. The farming numbers all improved; v2 was uploaded
for the online test. By map class (v2 vs v1 wins): jackpot 23 vs 18, rich 35 vs 37,
boss 15 vs 15, normal 20 vs 30, sparse 35 vs 35. The normal-map dip needs checking.

### Online batch 2 (v26, 2026-10-28): 0/5

Same opponent bot (Intercontinental Fish, rank 2 at creation; `online/ladder-before-g2.json`),
same maps and sides as batch 1. Group `a5b632bf-d900-411e-9c93-09a5113d46e1`. Live 26 /
Selected 26 before creation (`online/live-before-g2.txt`). Full table: `online/g2-summary.txt`.

| Map | v25 (batch 1) | v26 (batch 2) |
| --- | --- | --- |
| 00the_line | 0-1030, 23 deaths | 0-1014, 22 deaths |
| 00anvil | 84-1005, 20 deaths | 21-1192, 25 deaths |
| 00stampede | 0-1120, 45 deaths | 0-1120, 37 deaths |
| 01starfish | 52-1010, 26 deaths, camp 30k | 74-1043, 20 deaths, camp 33k |
| 00expanse | 410-1022, camp 85k vs 161k | 352-1001, camp 81k vs 166k |

Bot faults 0. Camp damage by round 500 rose on Expanse (33k -> 35k) and Starfish
(17k -> 26k), but the gap is still about 2x. The farming fixes are not the main gap.

What the two batches show about their advantage:
- **Fight maps** (the_line, anvil, stampede, starfish): they start killing us before
  round 100 and never stop; we earn almost no gold there (0-1400 per game). We cannot
  farm while losing every fight, so economy changes alone cannot help on these maps.
- **Farming maps** (expanse): their melee-heavy draft (Vendetta 40k, Varg 44k camp
  damage) out-farms ours (Willow 12k, Tavi 13k), with 6 bodies from 5 picks (Cassi &
  Issac). Local mirror tests said this draft was worse for our bot (49/280), but those
  opponents are our own old bots, not top teams.

## Top-5 report: v26 vs ranks 1-5 (2026-10-28): 0/25

One unranked group per team, rank rechecked before each create (`online/top5/groups.json`,
script `online/top5/queue.py`). Live 26 / Selected 26 throughout. Maps cover every class:
00the_line (jackpot), 00great_wall (boss), 01boss_battle (rich, monolith-gated altar),
00expanse (normal), 00crater (sparse). Sides a,b,a,b,a for ranks 1/3/5 and b,a,b,a,b for
2/4. Full table: `online/top5/report.txt`; data: `online/top5/analysis.json`.

Teams: Mite (1), Intercontinental Fish (2), newer team (3), Ad Astra (4), print dont int (5).
Result **0 wins, 25 losses, 0 bot faults**.

| Map | Avg score | Our deaths / kills | Camp damage us/them | Gold us/them | Camp dmg at r100 / r300 / r600 (us/them) |
| --- | --- | --- | --- | --- | --- |
| 00the_line | 0-1021 | 20 / 1 | 4k / 39k | 193 / 3811 | 0/3k, 2k/15k, 3k/37k |
| 00great_wall | 292-1024 | 2 / 0 | 39k / 119k | 1702 / 5197 | 9k/9k, 20k/31k, 30k/72k |
| 01boss_battle | 0-1178 | 12 / 0 | 42k / 191k | 1442 / 9610 | 10k/16k, 29k/63k, 39k/160k |
| 00expanse | 301-1023 | 2 / 0 | 72k / 170k | 4332 / 9245 | 6k/11k, 17k/35k, 40k/88k |
| 00crater | 16-1007 | 25 / 1 | 12k / 78k | 443 / 6594 | 2k/5k, 6k/21k, 8k/49k |

### What went wrong

1. **Mid-game farming collapses (all maps).** Early camp damage is close (Great Wall
   9k vs 9k at round 100), then they pull away: from round 300 to 600 on Great Wall we
   added 10k camp damage with five champions while they added 41k. With no fighting at
   all (2 deaths each side), Mite's **Tavi did 21.9k and Marcella 21.8k; ours did 13.8k
   and 9.1k** with the same champions. Their champions earn 800-1900 gold each, ours
   220-620. This is our behavior (walking, waiting, job choice), not only the draft.
   Likely part of it: they clear camps on our side too, so we find fewer live camps.
2. **Boss Battle: we never bank (0 points in all 5 games).** The single altar is
   walled by a monolith, so the old "gate" logic makes the team hold gems and wait for
   a group assault. Against real teams that never succeeds; we lost 92-182 carried
   gems per game and died 7-19 times.
3. **Fight maps (the_line, crater): we lose every fight from the start.** 2-3 deaths by
   round 100, 7-8 by round 300, about 20-25 per game, 1 kill per game on average. We
   earn under 700 gold there, so we never get items.
4. **Draft:** every one of the 25 opponent drafts had Heart of Ruin, 24 had Vesper, and
   most had Vendetta. We never pick Heart of Ruin or Vendetta. (But see v3 below: our
   bot plays those champions badly today.)

### What was good

- 0 bot faults in 25 games; no crashes or fuel failures visible in results.
- On farming maps we rarely die (Great Wall 2, Expanse 2 deaths per game) and lose
  few carried gems there (4-29 on Expanse).
- Early game is competitive on boss/farming maps (round-100 camp damage within ~0-40%).

### Fix order suggested by this report

1. Boss Battle / gated altars: bank another way or attack the gate early; never hold
   gems for a group assault against real opponents.
2. Mid-game farming: measure why champions hit camps so little after round 300
   (contested camps, waiting, walking).
3. Fight maps: avoid losing fights early (retreat, group, do not walk into them).

## v3 (platform v27, submission 2c3eb300-ed0f-483c-915d-8e0018097d79): regroup range

Source frozen in `versions/v3/src`. One change on top of v2, in `src/guard.rs`:
v24's "guarded support" alert (any enemy seen or any ally death) made **every**
champion walk to the support leader, wherever they were, and cut other job scores to
1/4. In a logged Great Wall game this took 51 of 244 sampled turns (21%), often 30+
tiles of walking with no job. Now only champions within 12 tiles of the leader
regroup; the rest keep farming.

How it was found (`scratch/gw1..gw3`): mid-game (rounds 250-500) our champions were
walking ~70% of turns and made 8 captures in 250 rounds. A job-commitment change
(switch only for a 2x better job) halved job switches but did not reduce walking
(rejected, kept in `scratch/farm-commit-variant.rs.txt`); a per-10-round debug log then
showed the regroup walks.

Local gate (280 games):

| Version | Wins | Gems | Camp damage | Deaths |
| --- | --- | ---: | ---: | ---: |
| v2 | 128/280 | 746 | 74.2k | 13.5 |
| v3 | **181/280** (96 vs apex, 85 vs apex22) | 833 | 92.3k | 14.3 |

Every map class improved (wins v2 -> v3): boss 15 -> 23/36, jackpot 23 -> 29/40, normal
20 -> 41/60, rich 35 -> 47/76, sparse 35 -> 41/68.

### Top-5 rematch on v27: 1/25

Same five maps, sides and opponent bots as the v26 top-5 test (`--source-group`), ranks
1-5 rechecked before each create (`online/top5-v27/`). Live 27 / Selected 27.

| Map | v26 avg score | v27 avg score | Camp damage v26 -> v27 | Deaths v26 -> v27 |
| --- | --- | --- | --- | --- |
| 00the_line | 0-1021 | 0-1085 | 4k -> 3k | 20 -> 20 |
| 00great_wall | 292-1024 | 462-1084 | 39k -> 60k | 2 -> 5 |
| 01boss_battle | 0-1178 | 17-1197 | 42k -> 55k | 12 -> 13 |
| 00expanse | 301-1023 | 483-1001 | 72k -> 102k | 2 -> 3 |
| 00crater | 16-1007 | 23-1024 | 12k -> 18k | 25 -> 26 |

First win against a top-5 team: **Expanse vs print dont int, 1006-927** (172k vs 181k
camp damage). Bot faults 0. Farming maps improved a lot; fight maps (the_line, crater)
and Boss Battle's gated altar are unchanged and are the next problems.

## v3 draft experiment (not uploaded; superseded name)

Top-team draft on farming maps (normal/rich, 4-5 picks): Vesper, Vendetta, Heart of
Ruin, Varg, Cassi & Issac. Local gate 98/280 vs v2's 128/280. One Expanse check: 413 vs
1019 gems, with similar camp damage but far fewer gems captured; Heart of Ruin 8.5k and
Cassi 9.9k camp damage. Our bot cannot use these champions well yet. Source change is in
`src/draft.rs` and `src/guard.rs` (not live).

## Map classes (`maps/`)

All 70 maps scanned from the bot's own map knowledge (`maps/maps.json`,
`maps/map-classes.txt`). Class by gems per champion and where the gems are:
- **jackpot** (10): one group holds at least half of the map's gems (the_line, anvil,
  stampede, vault, rows, contest...).
- **boss** (9): monoliths hold at least half the gems (great_wall, monolith, guardians,
  split, big_world...).
- **rich** (19): 90+ gems per champion, spread out (the_farm, boss_battle, islands...).
- **normal** (15): 50-90 gems per champion (expanse, starfish, crossing, corners...).
- **sparse** (17): under 50 gems per champion (crater, oasis, ribs, hooks, galaxy...).

## Experiments tried and rejected (source reverted)

3. **Copy the rank-2 team's items** (Monster, Jungle Health, then Power only): 82/280.
   It dropped Capture and Durability; camp damage fell (62.8k vs 66.3k) and deaths
   rose (16 vs 13 per game). Their advantage is not the item list alone.
4. **Power instead of Bruiser after v1's opening**: 110/280.

1. **Varg instead of Willow on 5-pick maps** (42 of 70 maps). 5-pick gate: 49/168
   vs forge-shop's 72/168 on the same maps. Varg out-farms Willow (13.1k vs 7.2k camp
   damage per game), but without Willow's heals every other champion farmed less
   and died more (team deaths per champion ~3.2 vs ~2.6). Folder:
   `matches/panel-Chamero-20261028-215901`.
2. **Stickier jobs** (current-job score bonus 1.25 -> 1.5, `farm.rs`). Full gate:
   103/280 (55 vs apex, 48 vs apex22) vs 135/280. Folder:
   `matches/panel-Chamero-20261028-220210`.

## Observations for next versions

- Profiled one 02tangle game (logging on): each champion spent 600-900 of 1250 rounds
  walking and only 120-250 hitting camps. Travel is the main farming cost.
- Ranged Tavi never captured or banked (melee is always nearer the capture tile).
- forge-shop does less total camp damage than apex/apex22 opponents in the gate
  (18.6M vs 22.9M over 280 games) yet wins more; the gain is not from raw damage.

## Commands

- Build: `cambc build Chamero`
- Gate: `py -X utf8 scripts\panel.py Chamero --opps apex apex22 --jobs 8 --quiet`
- Note: copy `.cargo/` and `.gitignore` too when cloning a bot folder, or the build fails.
