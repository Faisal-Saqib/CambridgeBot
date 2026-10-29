# Got Cooked — full match analysis

Team: **Got Cooked**, rank **392**, rating ~1514 (peer band, ±~50 of ours).
Data: **all 200 finished matches** in their history (100 ranked + 100 unranked),
downloaded 2026-10-29 via `cambc matches list/summary`. Raw data:
`matches/gotcooked/` (ignored by git), analyzer inline in
`matches/gotcooked/analysis.json`.

## Record

- Overall: **81–119** (ranked ~51–49 per list; unranked ~30–70).
- They are an **iterating team like us**: their unranked history concentrates on
  five practice maps — 00anvil (22), 00packs (21), 00monolith (21), 00lanes (20),
  00expanse (20) — played repeatedly against peer bots including **our own
  "Quantum Wardens" (they went 3/10 vs us)** and "Titanv1" (7/15).

## Draft

Core in every game: **Vesper Vale + Vendetta + Marcella**. Fifth/sixth picks:
Ryth (116), Tavi (115), Heart of Ruin (13), Varg/Willow/Cassi+Issac (rare).
They essentially never draft Heart of Ruin — unusual vs the top-20 meta where it
appears in ~90% of drafts.

## Items (their buys vs their opponents' buys)

- **Bruiser shard dump:** 66.2 Strength + 41.5 Focus + 12.3/7.9 emblems per
  game — far more than anyone else (top teams ~55 total Bruiser).
- **Zero Power items** (opponents buy 36.5 Power Strength + 20.1 Power Focus per
  game against them). **Zero Bruiser Health** too — all damage, no health in
  that family.
- Opening is standard (Monster ~15 Str, Jungle Health ~18, Durability ~19).
- **Zero Teleport Crystals in 200 games** (opponents buy 1.5/game vs them).
  They buy **~10 Altar Locks per game** (2033 total) — extreme lock usage.

## Champions (per game)

Marcella is the carry: 4.5 kills, 218 collected, 195 submitted, 1749 gold.
Vesper 2.5k kills / Vendetta 2.9 — they fight a lot. Supports Ryth/Tavi ~1.0-1.4
kills. Every champion dies 2.1–3.5×/game (team total 12.1 deaths/game — very
high; top teams die ~6).

## Win vs loss profile

| | Deaths us/them | Kills us/them | Camp us/them | Gold us/them | Submitted us/them |
| --- | --- | --- | --- | --- | --- |
| Wins (81) | 8.4 / 23.1 | 18.6 / 5.4 | 87k / 71k | 6676 / 3772 | 970 / 431 |
| Losses (119) | 14.6 / 9.8 | 6.8 / 12.4 | 75k / 140k | 4693 / 7964 | 459 / 961 |

They win by **brawling**: in wins they get 18.6 kills and force the enemy into
23 deaths. They lose by being **out-farmed**: in losses the enemy does ~2x camp
damage and earns 70% more gold while dying only ~10 times.

## Map record (>=3 games)

Strong: 00anvil 12/22, 00packs 12/21, 00lanes 8/20, adgato_gemcombat1 3/3,
00collision 3/3, 01shortcut 3/5, 02stalactites 3/4, 02treasure_box 3/4.
Weak: **00monolith 3/21, 00expanse 2/20**, 00stampede 0/3, 00great_wall 0/3,
00ambush 0/3, 01concentrated_wealth 0/3, 00rows 0/2, 00reverse_spiral 0/2,
02the_pond 0/2.

Pattern: they win on small fight/jackpot maps and lose on **big farming maps and
boss maps** — consistent with a fight-first bot that under-farms and skips
monolith objectives.

## Weaknesses to exploit (if matched against them)

1. **No teleport crystals ever** — on gap-separated maps (01islands 61%,
   02the_pond 47%, quadrants, big_world, ambush, shortcut) they physically
   cannot contest disconnected gems. Their record confirms: 0 wins on
   pond/ambush/concentrated_wealth.
2. **Monolith maps (3/21)** — they rarely crack monoliths; holding a boss-map
   lead and banking wins by default.
3. **No Power items** — their champions cap out on Bruiser; long games favor
   the opponent's scaling.
4. **Heavy altar-lock users** — expect ~10 locks/game; bring the fight away
   from locked altars or break locks early rather than rerouting.
5. **They die a lot (12+/game)** — their style trades bodies; a coordinated
   defense that doesn't feed serial 1v3s starves their only win condition.
6. **Under-farmed economy in losses** — surviving the early brawl then
   out-farming wins: they concede camp control when fights don't go their way.

## Strengths to respect

- Real kill pressure: 11.6 kills/game average, 18.6 in wins. Do not feed them
  isolated champions.
- Lock coverage slows tribute routes — our carriers must check lock status
  before pathing to altars.
- Marcella carry gets real gold concentration (1.7k/game); shutting her down
  removes ~30% of their damage.
