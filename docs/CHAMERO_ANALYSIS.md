# Independent analysis of Chamero online matches (v25–v30)

Analysis of all 125 unranked match summaries under `bots/Chamero/online/`
(root g1/g2 batches + `top5` through `top5-v30`), produced by
`scripts/chamero_analysis.py` (data: `matches/chamero-analysis.json`).
Our team = "Quantum Wardens". Opponents: current top-5 teams (Mite,
Intercontinental Fish, newer team, Ad Astra, print dont int). **Overall: 1 win,
124 losses, 0 bot faults.**

| Version | Games | Wins | Change |
| --- | ---: | ---: | --- |
| v25/26 | 10 | 0 | forge-shop base + respawn fix + early gold weight |
| v26 | 25 | 0 | (same as above, top-5 panel) |
| v27 | 25 | **1** | regroup limited to 12 tiles |
| v28 | 25 | 0 | retreat earlier |
| v29 | 25 | 0 | gate ward |
| v30 | 15 | 0 | patient gate (only gated maps change; 2 teams skipped — rank dropped below 5) |

## Per-map totals (all 125 games)

| Map | W | Avg score | Deaths us/them | Camp dmg us/them | Gold us/them | Gems lost us/them |
| --- | --- | --- | --- | --- | --- | --- |
| 00the_line | 0/25 | 0–1040 | 18 / 2 | 4k / 38k | 0.2k / 3.7k | 14 / 0 |
| 00crater | 0/23 | 23–1013 | 24 / 2 | 17k / 76k | 0.6k / 6.1k | 92 / 10 |
| 01boss_battle | 0/23 | 20–1140 | 11 / 2 | 60k / 227k | 2.3k / 11.4k | 162 / 87 |
| 00great_wall | 0/23 | 403–1062 | 6 / 3 | 55k / 120k | 2.4k / 5.7k | 100 / 61 |
| 00expanse | **1/25** | 428–1015 | 2 / 1 | 94k / 169k | 5.5k / 9.0k | 4 / 4 |
| 00stampede | 0/2 | 0–1120 | 41 / 2 | 9k / 138k | 1.2k / 16.6k | 0 / 0 |
| 00anvil | 0/2 | 52–1098 | 22 / 1 | 9k / 102k | 0.5k / 7.9k | 42 / 12 |
| 01starfish | 0/2 | 63–1026 | 23 / 8 | 32k / 137k | 1.2k / 9.4k | 72 / 28 |

Gold efficiency: opponents convert 144 submitted gems per 1000 gold earned;
we convert 79. We both earn less AND convert worse.

## Mistakes found (measured)

1. **Zero consumables in 125 games.** We never bought a single Altar Lock or
   Teleport Crystal. Opponents average **4.0 locks and 1.8 crystals per game**
   (496 locks, 223 crystals total). Locks protect tribute routes; crystals cross
   disconnected terrain and escape hunts. This is the single clearest missing
   feature.
2. **Entire item families never purchased.** Across 125 games we bought 0 Power
   shards/emblems (opponents: ~11.5 Power Strength, ~7.9 Power Focus per game),
   0 Tribute items, 0 Jungle Strength/Focus, 0 Treasure Health/Focus. Opponents
   buy **55.6 Bruiser Strength shards/game**; we buy 3.8 and instead over-index
   on Monster Strength (12.7/g vs their 6.9), Jungle Health (10.0/g) and Capture
   Strength (8.5/g) — farming/defense items while they stack combat power and
   snowball.
3. **Draft is off-meta.** Our 5-pick is Vesper+Ryth+Marcella+Tavi+Willow
   (98/125). Opponents draft Vendetta (97 games) and Heart of Ruin (115) —
   champions we essentially never pick. Their Vendetta averages 27.1k camp
   damage + 2.8 kills; their Heart of Ruin 19k + 2.0 kills. Our own draft notes
   (CHAMERO.md) already flagged this but the experiment was rejected on local
   gates vs our own bots (see methodology note below).
4. **Per-champion output gap on the same champion.** On Expanse (pure farm):
   their Vesper does 43.2k camp damage vs our 20.5k; their Marcella 32.1k vs
   19.7k; their Tavi 28.6k vs 17.7k. Only Ryth is equal (22.4 vs 22.3k). Same
   champion, ~2x output — pointing at itemization and job routing, not the
   champion itself.
5. **We die ~9x more.** Our champions average 2.3–3.0 deaths/game each;
   theirs 0.1–0.4. On the_line/crater/stampede/anvil we die 18–41 times per
   game while they die 1–2. v28's earlier-retreat cut the_line deaths
   (103→80) but did not change a single result.
6. **the_line: 0 points in all 25 games.** We never bank once. Same for
   stampede (0/2). On jackpot maps the enemy takes the center and we never
   contest it.
7. **boss_battle: worst score regression in v30.** The "patient gate" change
   produced 0–1838 vs Mite — the largest enemy score in the dataset — while we
   still banked 0 and lost 162 carried gems/game (1,208 lost vs Mite alone).
   Opponents bank 1,000–1,800 by breaking the gate late and tributing 200–865
   at once; waiting past round 900 handed them the whole map.
8. **Carry concentration: they have one, we don't.** Their Marcella averages
   369 collected / 333 submitted / 2,572 gold / 3.9 kills per game — a clear
   carry. Our richest champion (Marcella) earns 708 gold. Flat income, no star.

## Methodology mistakes (process-level)

- **Local gates don't transfer.** v3 looked like a huge win locally
  (128→181/280 vs our own bots) but scored 1/25 online. Every change is
  evaluated against old versions of ourselves; top-5 opponents invalidate the
  mirror assumption. CHAMERO.md itself shows the rejected Varg/HoR/Vendetta
  draft (98/280 local) is exactly what all five opponents play.
- **Determinism hides coverage.** v29 and v30 reused `--source-group` seeds, so
  every non-gated map literally replayed identical games (e.g. Expanse vs newer
  team is 408–1003 in v27 through v30). "25 games" per version is really ~5 new
  data points for v29 and ~10 for v30.
- **Only 5 maps tested, all from one panel.** the_line, great_wall,
  boss_battle, expanse, crater — none of the other 65 published maps were ever
  played online by Chamero.
- **Opponent band too narrow.** All opponents are rank ≤5; every version goes
  0–1 wins, so the online panel can't rank versions at all. It confirms
  "much worse than top 5" but cannot distinguish v27 from v30.

## Suggested improvements (in priority order)

1. **Buy consumables** — altar locks on contested/tribute maps, TP crystals on
   disconnected maps and for carrier escapes. Cheapest missing feature with a
   measured 4+1.8/game usage by every opponent.
2. **Widen the item shop** — add Power (main-stat), Tribute, Jungle Str/Focus
   and Treasure families; shift late-game budget from Monster/Capture/Health
   stacking toward the opponent's Bruiser-Strength-dominant mix.
3. **Draft Vendetta + Heart of Ruin** (both in ~90%+ of opponent drafts) in
   place of Tavi/Willow on brawl-heavy maps; keep Willow only where sustain
   clearly wins. Test against saved top-20 opponent bots, not just our own.
4. **Contest jackpot maps.** 0 points in 25 line games means the current
   spread-farm policy concedes the only objective. Group early, take the center
   camp together, escort the carrier out — losing fights there is already the
   default, so the downside is capped.
5. **Fix gated-altar banking.** Break the gate earlier (round ~400–600 like
   opponents) or bank through a second altar; never end holding 50–1,200
   unbanked gems.
6. **Concentrate economy on a carry** (Vesper or Marcella): solo captures for
   them, allies zone, they buy the combat items. Mirrors the user's Prism plan
   and every top team's reward distribution.
7. **Retreat is still too weak** — 2.3–3.0 deaths/champion vs 0.1–0.4 for
   opponents. Their champions simply do not die; ours die in serial 1-at-a-time
   waves. Needs threat-radius regrouping plus earlier retreat, not just
   earlier retreat.
8. **Widen the test panel** — include rank 5–15 opponents and more maps so
   version deltas are measurable; a 0/25 panel cannot rank candidates.

## Caveats

- Consumable/item counts are purchase events, not usage confirmation.
- The platform does not report which submission played each match; version
  attribution relies on the campaign's own live-version logs.
- All opponents here are top-5; results do not predict performance vs rank
  20–200 teams.
