# Got Cooked — Recent 100 Games Analysis (2026-10-29)

Scope: the 100 most recent finished matches (played 10:22–10:40 UTC, all downloaded
and analyzed locally). 85 unranked + 15 ranked. Zero bot faults on either side.

Earlier report for the first 200 games: `GOT_COOKED_ANALYSIS.md`. This doc focuses on
what the newest 100 show and how the team has evolved.

## Record

- **35/100 wins overall.** Ranked: **10/15 (67%)**. Unranked: **25/85 (29%)** —
  unranked is their testing queue (30 games vs our bot, 25 vs top-20-ish teams).
- vs **Quantum Wardens (our live v24): they went 10/30.**
- 94 games ended on gems, 6 on tiebreak gems. No resignations, no crashes.

## Team totals per game (us = Got Cooked)

| Metric | GC | Opponents |
|---|---|---|
| Score (submitted) | 725 | 790 |
| Collected | 809 | 904 |
| Camp damage | 86k | 108k |
| Champion damage | 27k | 28k |
| Gold earned | 5,414 | 5,770 |
| Kills | **9.1** | 7.3 |
| Deaths | **9.0** | 10.8 |
| Healing done | **0** | ~2k |
| Wards | 112 | 112 |

**New development: they now out-kill and out-survive opponents on average** (9.1
kills vs 7.3; 9.0 deaths vs 10.8). The earlier 200-game profile was the opposite
(they died 12+/game). The kill pressure is real — the losses now come from being
out-farmed, not out-fought.

### Win vs loss pattern

| | Wins (n=35) | Losses (n=65) |
|---|---|---|
| Collected | 1,112 vs 495 | 646 vs 1,124 |
| Camp damage | 92k vs 56k | 83k vs **136k** |
| Kills | 18.0 | 4.4 |
| Deaths | 5.8 | 10.8 |
| Gold | 7.0k vs 3.2k | 4.6k vs 7.2k |
| Score | 1016–324 | 567–1042 |

Same signature as before: wins are kill-fests where they also out-farm; losses are
games where the opponent quietly farms 2x while GC kills only 4 champs.

## Draft — changed since the last snapshot

| Draft | Record |
|---|---|
| Marcella + Ryth + Vesper (3-pick) | **18/30 (60%)** |
| Marcella + Ryth + Vesper + Varg (4-pick) | 5/9 (56%) |
| Marcella + Ryth + Tavi + Varg + Vesper (5-pick) | **12/61 (20%)** |

**Vendetta is completely gone** — dropped from every draft. **Varg added** on
4–5-pick maps, Tavi only on 5-pick. The 3/4-pick versions are genuinely good
(~58%); the 5-pick version remains broken at 20% — same split as before, so the
draft change didn't fix their big-map problem.

Opposing drafts: HoR+Vendetta+Vesper+Marcella+flex still dominates (the meta core
we never draft).

## Per-champion (per game)

| Champ | Games | Kills | Deaths | Camp dmg | Collected | Submitted | Gold |
|---|---|---|---|---|---|---|---|
| Marcella | 100 | **4.1** | 1.5 | 19.2k | **234** | 206 | **1,740** |
| Ryth | 100 | 1.6 | 2.4 | 20.1k | 204 | 187 | 1,074 |
| Vesper Vale | 100 | 1.8 | 2.6 | 20.8k | 167 | 150 | 1,354 |
| Varg | 70 | 1.6 | **1.6** | 18.1k | 174 | 161 | 1,037 |
| Tavi | 61 | 0.9 | 2.4 | 21.9k | 135 | 112 | 853 |

Marcella is the carry: best kills, fewest deaths, most gems and gold — the
concentrated-carry model we also want. Varg slots in cleanly (1.6 deaths). Tavi
is now the weak link (0.9 kills, least gold, still dies as much as Ryth) —
consistent with the 5-pick draft underperforming.

## Items & consumables

Still zero Power-family items and **still zero Teleport Crystals in 100 games**
(opponents buy 0.4/game against them). New: Durability Shard of Health appeared
(19/game) — they added some frontline health since the last snapshot. Altar Locks
dropped from ~10/game to **3.7/game** (they read their own over-locking issue or
changed the rule); still above the opponent average (2.8).

## The persistent critical weaknesses — confirmed again

1. **Teleport Crystal = 0, always.** islands: collected **58 vs 1,058**
   (7k vs 134k camp damage — literally can't reach 61% of that map's gems).
   guardians: 512 vs 1,889 (20k vs 204k). stampede: 146 vs 800. Any map with
   gap-separated or boss-gated gems is a forfeited game.
2. **Monolith/boss maps still 0.** monolith **0/10** in this batch; guardians 0/2;
   their camp damage collapses (20k vs 204k on guardians) because they can't/won't
   clear the big camps.
3. **Expanse still bad: 2/12** — the pure-farming map; their camp damage (131k)
   can't match opponents' (164k) with no fighting to bail them out.
4. **5-pick maps: 20%.** Big maps give their brawl no one to fight.
5. **Anvil deaths exploded**: 19.8/game with 20/29/32/33-death blowouts in losses
   — serial feeding when the brawl goes wrong (e.g. 103 gems vs 1,025).
6. **Tributes are tiny**: 4,269 tributes, avg **17 gems** each — the exact
   small-tribute habit that correlates with losses in the top-20 census.
7. **Zero healing** across 100 games — no Willow/medic pick at all while
   opponents heal ~2k/game.

## What changed vs the first-200 snapshot

| Trait | First 200 | Recent 100 |
|---|---|---|
| Draft | Vesper+Vendetta+Marcella | **Vendetta dropped**, Varg added |
| Locks/game | ~10 | 3.7 |
| Kills vs opp | ~equal | **now out-kills** (9.1 vs 7.3) |
| Deaths vs opp | died 12+ | now out-survives (9.0 vs 10.8) |
| TP crystals | 0 | **still 0** |
| Power items | 0 | **still 0** |
| Monolith record | 3/21 | **0/10** |
| Ranked win rate | ~41% overall | 67% (small n) |

They're iterating in the right direction on combat and locks but have not touched
the two biggest levers: terrain access (crystals) and objective camps.

## Direct implications for us (Quantum Wardens)

- **We beat them 20/30 in this batch** — and our biggest wins are exactly the
  crystal/monolith maps: guardians 1,889–512, islands 1,058–58. Our TP/monolith
  logic is a real edge over a peer team.
- Their unranked spam vs us (30 games in 18 min) means **they're actively
  scouting/testing against our live bot** — expect them to adapt to what beats
  them (which right now is terrain access + camp dominance).
- Where they DO beat us is likely the brawl maps (their 18/30 on 3-pick drafts)
  — consistent with our known anvil/packs/lanes fragility.
- If they ever buy crystals, our islands/guardians edge disappears — it's
  borrowed advantage, not a durable skill gap.

Data: `matches/gotcooked/summaries/` + `matches/gc-recent100.json` (match list) +
`matches/gc-recent100-analyzed.json` (per-game aggregates).
