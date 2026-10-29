# Got Cooked — gem outfarming diagnosis (AI implementation brief)

Purpose: hand this document to a coding AI to fix the "Got Cooked" bot's gem
economy. Everything marked **[measured]** comes from all 200 of their finished
matches (100 ranked + 100 unranked, downloaded 2026-10-29). **[derived]** =
computed from map data. **[hypothesis]** = unverified proposal.

## Context for the implementing AI

- Game: Cambridge Battlecode. Teams draft champions, clear monster camps for
  gems + gold, and win by tributing gems at altars. Death costs ~60 rounds
  out of play; PvP killers steal carried gems; camp kills destroy them.
- Bot: "Got Cooked" (rank ~392). Identity: fight-first brawler.
  Draft core every game: Vesper Vale + Vendetta + Marcella (flex: Ryth,
  Tavi). Marcella is the carry (4.5 kills, 218 collected, 1749 gold avg).
- Record: 81–119. Wins are kill-fests (18.6 kills/game); losses are farm
  deficits (opponent does ~2x camp damage).

## The stated problem, verified

"They do OK on gold but get outfarmed on gems" — **[measured]** per game:
gold 5,496 vs 6,266 (–12%), **collected gems 770 vs 873 (–12%), submitted
666 vs 746 (–11%)**. Banking conversion is 86% vs 86% — **the loss happens
at collection, not delivery.**

### Where the gem deficit lives (per game, [measured])

| Map class | Games | Wins | Gold us/them | Collected us/them | Camp dmg us/them | Deaths |
| --- | ---: | ---: | --- | --- | --- | --- |
| boss | 31 | 5 | 6225/8124 | **745/1107** | 96k/157k | 15 |
| jackpot | 33 | 12 | 4732/6030 | 616/731 | 55k/80k | 20 |
| normal | 57 | 16 | 5650/7525 | **746/959** | 105k/146k | 8 |
| rich | 37 | **25** | 4677/3906 | **932/800 (ahead)** | 63k/74k | 10 |
| sparse | 42 | **23** | 6073/5452 | **800/759 (ahead)** | 68k/90k | 10 |

**Key pattern:** they out-farm opponents exactly where they already win
(rich/sparse — fights go their way, kills buy map control). They are
outfarmed 28–48% on boss/normal maps where they die *little* (8 deaths on
normal) — so the deficit is **clearing efficiency and objective access,
not just deaths**.

## Diagnosis — why they get outfarmed, ranked

1. **Fewer camps cleared per game [measured].** 80k vs 112k monster damage
   (–28%). On normal maps with only 8 deaths they still trail 105k vs
   146k — this is routing and clear speed, not survival. Likely causes
   [hypothesis]: travel-dominated turns (walking to far camps instead of
   cluster trips), waiting beside respawning camps without a cap, job
   thrash between two camps mid-route, and contested camps abandoned to
   the enemy.
2. **Objective camps conceded [measured+derived].** Boss maps: opponents
   collect 1107 vs 745 — they take the monolith-held gems (~50–76% of
   those maps' totals) while Got Cooked either ignores them or dies
   attempting them (15 deaths/game). 00monolith record: 3/21.
3. **Disconnected gems unreachable [measured].** 0 teleport crystals in
   200 games. On gap-separated maps (islands 61% of gems, pond 47%,
   quadrants/big_world/ambush/shortcut) up to half the economy is
   physically unreachable — a pure concession.
4. **Fighting time isn't farming time [measured+hypothesis].** 11.6
   kills + 12.1 deaths per game means a large share of champion-turns go
   to combat and ~60-round respawns. 12 deaths × 60 ≈ 720 champion-rounds
   dead per game (~10% of team turns) on top of the turns spent chasing.
   In losses they collect barely half their winning total (560 vs 1079).
5. **Mono-stat itemization [measured].** 0 Power items, 0 Bruiser Health;
   66 Bruiser Strength shards/game. Opponents' Power+Health mix clears
   camps faster per gold spent later in the game — compounding the
   collection gap after round ~600.

## What to implement (concrete)

### A. Cluster-trip job assignment (fixes cause 1)
Score **trips, not camps**. For each champion:
```
trip_value = Σ_camps in cluster (gems + 0.3*gold) * safety / (walk + clear + hp_cost + respawn_wait)
safety = dist_enemy_spawn / (dist_enemy_spawn + dist_our_spawn)
respawn_wait capped at ~30 rounds
```
Claim all camps in the chosen cluster in shared memory; keep the claim for
the whole trip (mild 1.25x commitment bonus — 1.5x proved too sticky in
our own experiments). Targets: camp damage +25% on normal maps, walking
share of turns visibly down in a logged run.

### B. Monolith siege pair (fixes cause 2)
On boss maps: two highest-damage champions chip the *lowest HP-per-gem*
monolith between fights (camp damage persists across visits); blacklist
the camp ~80 rounds for a champion that dies to it. Everyone else farms
free camps and banks normally. Alternatively concede monoliths and race
the free economy — but pick one; currently they do neither well (3/21 on
00monolith).

### C. Island hopper (fixes cause 3)
If map scan shows gems outside the spawn walkable component: buy 1–2 TP
crystals after opening items, assign one champion to channel across and
claim the disconnected region. Cheap and isolated — implement first.

### D. Fight only when it pays (fixes cause 4)
Engage only if `our_bodies_within_6 >= their_bodies` OR a kill is
completable this turn; otherwise withdraw toward allies/spawn. Carriers
with >15 gems never fight — altar first. If 2 allies died within ~80
rounds, team regroups (stops serial 1-by-1 feeds; their deaths come in
waves [measured]).

### E. Item build v2 (fixes cause 5)
Opening stays Monster-Str + Jungle-Health. Then: Bruiser <mainstat> capped
~25–30 → **Power <mainstat>**; melee frontline (Vendetta, Ryth) gets
Bruiser/Durability Health so they tank while Marcella cleans up.
Add a Tribute emblem on the dedicated carrier for jackpot maps.

### F. Draft tweak (supporting fix)
5-pick maps: add Heart of Ruin — their best-stat champion (0.8 deaths,
3.2 kills) yet drafted only 13/200 times; 5-pick drafts with HoR won 54%
vs 25% without. Drop Willow (0 kills, worst per-game output).

## What NOT to change

- 3-pick brawl draft (59% win rate — their best mode).
- Altar-lock buying habit (~10/game; locks cost only 10g — keep them,
  just place where we control the approach).
- Tribute conversion — already 86%, banking is not the problem.

## Verification protocol for the AI

1. Local mirror matches vs a frozen copy of the current bot on the same
   map + both sides; judge changes on the full-map gauntlet, never one
   game (mirror games are noisy even with identical code).
2. Metrics that must move: monster damage/game on normal+boss maps
   (80k→100k+), collected gems on those maps (+25%), deaths/game (12.1→~9),
   gem-loss rate (77→<50).
3. Metrics that must NOT regress: kills/game in wins (≥15), submitted on
   rich/sparse maps.
4. Online check afterwards: unranked 5-map panel vs peer bots (their
   existing loop — Quantum Wardens, Titanv1, Sneaky Wardens are in their
   match history).

## Caveats

- No replay-level position data was used; causes 1–2 are inferred from
  outcome metrics, not watched behavior. Verify with one instrumented
  local game logging walk-vs-clear time per champion before large refactors.
- Opponent bots in unranked games are unknown versions; treat directional
  gaps as robust, exact magnitudes as approximate.
