# Got Cooked — improvement program (deep suggestions)

Evidence base: all 200 finished matches (see `GOT_COOKED_ANALYSIS.md` for the
raw tables). Each suggestion cites the measured problem, the fix, and how to
implement/verify it.

## P0 — Buy teleport crystals (biggest single gap)

**Measured:** 0 crystals in 200 games; opponents buy ~1.5/game against them.
Their record on gap-separated maps: the_pond 0/2, ambush 0/3,
concentrated_wealth 0/3, islands 0/1 — **0 wins on every map where >5% of
gems are unreachable on foot** (islands 61%, pond 47% gap-separated).

**Fix:** consumable purchasing rule — on any map where the static map scan
shows gems outside the spawn's walkable component, buy 1–2 TP crystals after
the opening items (they cost little vs the 40–370 gems they unlock). Assign
the disconnected region to one crystal-carrying champion ("island hopper")
that channels in, clears, and banks on return. Short gaps may instead be
crossed by a dash-capable champion — but measure per map: if the gap exceeds
dash range, crystal is the only answer.

**Verify:** replay islands/pond games; the hopper should collect >40% of
disconnected gems by round 800.

## P1 — Rebalance the item build: add Power, add Health

**Measured:** 0 Power-family purchases in 200 games (opponents: 36.5 Power
Strength + 20.1 Power Focus + 4.4 Power Health per game). 0 Bruiser Health.
They buy 66.2 Bruiser Strength shards/game — a single-stat mono-build.

**Fix (build order):**
1. Opening: Monster Str + Jungle Health (they already do this — keep it).
2. Mid: continue Bruiser <mainstat> but cap it ~25–30 shards; then add
   **Power <mainstat>** — every strong opponent they face buys Power;
   it is presumably better gold-per-stat in the late game or stacks
   multiplicatively with shards.
3. **Frontline health:** Vendetta and Ryth die 3.5/2.7 per game. Give the
   melee frontline Bruiser/Durability Health shards (opponents buy 23
   Bruiser Health + 13.4 Durability Health per game vs them) so they
   survive long enough for Marcella to clean up.
4. Carry split: Marcella → Focus items (she does 19.4k camp dmg and 4.5
   kills — she IS the carry), Vesper/Vendetta → Strength.

**Verify:** mirror-match A/B on anvil/packs: deaths/game should drop from
12.1 toward ~8, and camp damage/game should rise from 80k toward 100k+.

## P2 — Draft Heart of Ruin on 5-pick maps

**Measured:** HoR appears in only 13/200 games but is their best champion
per game: 0.8 deaths (lowest), 3.2 kills, 168 collected, 142 submitted.
The 5-pick draft *with* HoR won 54% (7/13); the standard
Marcella+Ryth+Tavi+Vendetta+Vesper 5-pick won only **25% (24/96)**.
Meanwhile their 3-pick draft wins **59% (34/58)** — the problem is not the
core, it's what they add on bigger maps.

**Fix:** 5-pick draft → **Vesper, Vendetta, Marcella, Heart of Ruin, Ryth**
(the exact top-20 core; also the most-frequent winning draft in our census).
Drop Tavi to 6th / maps with heavy ranged demands; drop Willow entirely
(4 games, 0 kills, 11.4k camp — their worst champion).

**Verify:** the HoR-containing 5-pick already shows 2x the win rate of the
current one — confirm over 10+ games that it isn't small-sample noise.

## P3 — Stop feeding when behind (retreat tuning)

**Measured:** every champion dies ~50% more in losses than wins (Vendetta
3.9/g, Vesper 3.7/g in losses). Their style is fight-first: kills 18.6 in
wins but they take 14.6 deaths in losses — they keep committing to losing
fights. Gem loss doubles in losses (14% vs 7% of collected) — they die
carrying.

**Fix:**
- Retreat rule: outnumbered within ~8 tiles OR projected to lose the
  exchange → withdraw toward allies/spawn, not toward the next camp.
- Carriers: if holding >15 gems, never take a fight — route to the altar
  first. The 14%-of-collected loss rate in losses is recoverable points.
- Serial-death breaker: if 2 allies died in the last ~80 rounds, the whole
  team regroups instead of feeding one at a time (their deaths come in
  1-by-1 waves — same pattern our own bot had on the_line).

**Verify:** deaths/game in losses should drop from 14.6 toward ~9 without
kills/game in wins dropping below ~15.

## P4 — Fix the two broken map classes

**Monolith/boss (3/21):** they barely crack monoliths. Options:
- Patient siege: pick the *lowest-HP-per-gem* monolith, chip it with the
  two highest-damage champions between fights (camp damage persists),
  blacklist it for ~80 rounds after any death there.
- Or concede it: on 00monolith, 76% of gems are monolith-held but 24%
  still isn't — take the free 24%, bank it, and win on kills. The current
  play appears to do neither well.

**Farming maps (expanse 2/20):** out-farmed ~1.5x (91k vs 135k camp damage
in unranked). Fix = wider spread (one champ per camp cluster), plus the
P1 item changes (Power items make clears faster). Also consider drafting
Varg on pure-farm maps: he does 43.9k camp/game for top teams.

## P5 — Spend less on locks, more deliberately

**Measured:** 2,033 altar locks ≈ 10/game. Locks only help if the team
controls the altar approach; in losses the enemy banks 961/game anyway.

**Fix:** buy locks only when (a) we hold the altar's approach, or (b) an
enemy carrier is expected within ~20 rounds. Cap ~3–4/game and redirect
the saved gold into items — 6+ locks/game is a significant item budget
burned on a consumable that isn't converting into wins.

## P6 — Preserve what already works

- **3-pick brawl style (59%)** — keep it; on small maps their fight-first
  identity is genuinely good (anvil 12/22, packs 12/21).
- **Marcella as carry** — already concentrated (1749 gold, 4.5 kills).
  Push it further: let her solo-capture while allies zone (top teams do
  this 93% of captures).
- **Lock usage instinct** — they already understand altars matter; just
  buy fewer and time them better (P5).
- **Altar awareness** — they tribute 666/game avg, better than most peers.

## Suggested implementation order

1. TP crystals (P0) — cheap, isolated, measurable on 4 known maps.
2. Power + frontline health items (P1) — pure shop config change.
3. HoR in 5-pick drafts (P2) — one-line draft-order change.
4. Retreat/carrier rules (P3) — medium effort, biggest death reduction.
5. Map-class plans for monolith/farm maps (P4).
6. Lock throttling (P5) — one counter + conditions.

Each change should go through their existing loop (unranked 5-map panel
vs peer bots, including us — their 3/10 vs Quantum Wardens is a useful
regression check).
