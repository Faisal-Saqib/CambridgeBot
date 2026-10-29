# Chamero independent analysis — versions v30–v39 (400 games)

Independent re-analysis of every match played by our bot from platform
version v30 onward: `online/top5-v30..v39` (240 games vs ranks 1–10) +
`online/panel2*` (160 games vs ranks 6–11). All unranked, fixed maps/sides.
Analyzer: `scripts/chamero_analysis.py` → `matches/chamero-analysis.json`.
Overall: **4 wins, 396 losses, 0 bot faults.**

| Platform | Chamero | Change | Games | Wins | Avg score | Deaths | Camp us/them | Gold us/them |
| --- | --- | --- | ---: | ---: | --- | ---: | --- | --- |
| v30 | v6 | patient gate (900) | 15 | 0 | 194–1092 | 10 | 63k/145k | 3.1k/7.6k |
| v31 | v7 | ≤2 champs/danger camp | 25 | **1** | 228–1033 | 11 | 76k/156k | 3.7k/8.3k |
| v32 | v8 | cheap wards (off) | 25 | 0 | 212–1084 | 10 | 74k/152k | 3.5k/8.0k |
| v33 | v9 | locks + gate@500 | 50 | 0 | 147–1037 | 17 | 43k/116k | 2.2k/8.0k |
| v34 | v10 | Bruiser build | 50 | 0 | 156–1048 | 18 | 48k/123k | 2.4k/8.5k |
| v35 | v11 | fight call | 50 | **1** | 156–1065 | 18 | 48k/126k | 2.5k/8.6k |
| v36 | v12 | respawn muster | 50 | 0 | 158–1060 | 16 | 46k/124k | 2.4k/8.4k |
| v37 | v13 | chase hurt enemies | 45 | **1** | 153–1053 | 16 | 47k/125k | 2.4k/8.4k |
| v38 | v14 | top-team draft, fight maps | 45 | **1** | 157–1050 | 16 | 48k/125k | 2.4k/8.4k |
| v39 | v15 | farm high-HP camps | 45 | 0 | 165–1054 | 16 | 46k/124k | 2.2k/8.2k |

## Strengths (what improved and works)

1. **Boss Battle transformation.** Camp damage 60k → 156k avg, score 20 →
   139 (v39 avg 253, best of any version). The patient-gate + high-HP camp
   changes genuinely work — this went from "0 points ever" to competitive
   economy. Still loses because opponents crack the gate and bank 1000+.
2. **Expanse is near-parity.** Only ~1 death/game, 104k vs 168k camp
   damage. All 4 wins are Expanse vs print dont int (v31/v35/v37/v38).
   The farm engine works when nothing fights us.
3. **Great Wall survivability.** 5 deaths/game, 401 avg — we survive on
   boss maps even while losing on score.
4. **Gem-loss discipline improving.** Lost carried gems: 150/game at v30 →
   75/game at v39. Deaths on fight maps also trending down (stampede
   41→31, starfish 31→28 since v36 muster).
5. **Zero faults in 400 games.** Protocol/fuel handling is solid.

## Weaknesses (persistent across all 10 versions)

1. **the_line: 0 points in 48 consecutive games.** Across ten versions we
   have never submitted a single gem on this map. The 83%-of-gems center
   group is conceded every time. This is the single most broken behavior
   in the bot.
2. **Fight maps are massacres.** stampede 35 deaths/game, starfish 30,
     anvil 21, crater 20, galaxy 19 — while the enemy loses 1–3. We average
   **~1 kill per game everywhere** vs 15–17 for them. Fights start ~round
   30 and we lose every one.
3. **Same champion, 3–4× output gap.** Enemy Vesper does 40.1k camp damage
   vs our 10.3k; enemy Marcella 25.8k + 2,700 gold vs our 12.5k + 938.
   Enemy champions die 0.2–0.4×/game; ours die 3.0–3.6×/game. The draft we
   added in v38 made it worse: our Heart of Ruin does 2.0k camp and dies
   4.8×/game vs enemy HoR's 20.1k/0.4 — **we cannot pilot these champions.**
4. **Item economy still incomplete.** Zero Power, Jungle Str/Focus items
   still bought (opponents: ~23/game combined). Critically: opponents buy
   **44 Bruiser Health + 15.5 Durability Health shards per game; we buy
   1.5 + 2.9**. They tank up; we don't — a big part of why every exchange
   ends 1-for-5.
5. **Consumables near-zero.** 0.7 locks/game vs their 4.4; **0 teleport
   crystals in 400 games** (them: 688). None of the panel maps are
   gap-separated so crystals haven't mattered *here*, but it remains a
   missing feature for ranked maps.
6. **No finishing power.** We deal 14–29k champion damage but get ~1 kill;
   they heal/shield 7–14k/game and hurt targets escape. Chase (v13) didn't
   move kills.
7. **Score plateau.** Avg score 147→165 across v33–v39 — six versions of
   changes, no movement on the metric that decides games.

## Improvements (priority order)

1. **the_line needs a dedicated profile, anything is an upgrade.** 0/48
   means zero downside to experimentation: (a) send all 4 champs at the
   center group at round 0 and fight for it — we lose these fights anyway,
   but contesting costs nothing vs conceding; (b) alternatively speed-run
   the edge camps and bank the ~17% free gems early for a low-but-nonzero
   score. Pick one, measure vs saved opponents.
2. **Survival-first on brawl maps.** We lose fights we don't have to take:
   farm the far half, retreat when enemies within ~8 tiles regardless of
   "winnable" scoring, bank every ~15 gems. Deaths 30→~10 would
   mechanically double farm turns. v36 muster proved the direction;
   extend it to *avoiding* the fight, not just re-grouping after it.
3. **Buy Health.** Match the opponent mix: ~40 Bruiser-Health + ~15
   Durability-Health per game. Our champs die at nearly full item slots
   filled with offense they can't survive to use.
4. **Stop drafting what we can't pilot.** v38's HoR/Vendetta draft gives
   those champs 2–3k camp damage and ~5 deaths/game. Either teach their
   job scoring to use these champions' abilities, or revert fight maps to
   the farm draft — the experiment measurably hurt.
5. **Focus-fire the wounded healer.** Their sustain (7–14k healing/game)
   converts our damage into escapes. Target lowest-HP or the Willow/Tavi
   support in range rather than nearest; combine with existing chase.
6. **TP crystals + more locks.** Crystals for carrier escapes on brawl
   maps (3-tile blink ignores terrain — a stampede carrier could escape
   the hunt); locks on the altar our carriers actually use.
7. **Boss Battle: contest the gate timing.** They break the gate ~470–720
   and bank 1000+. Our improved economy now reaches ~250 — next step is
   either breaking our own gate ~500–600 first or sending one champ to
   steal their post-break haul (kill the carrier at the altar).

## Process notes for future iterations

- All 4 wins are the **same deterministic matchup** (Expanse vs
  print dont int). The panel has effectively one winnable game; version
  deltas on it are 1-bit signal. Widening the opponent band (rank 10–20)
  would make versions distinguishable again.
- Scores are stable across versions partly because fixed seeds replay
  identically where code doesn't diverge — treat per-map score deltas,
  not the 25-game average, as the signal.
- The 46k→48k camp-damage plateau vs their 124k says the remaining gap
  is no longer *which* camps we choose (v15 helped: boss_battle 146→253
  score) but **how fast we clear them** — items (Health→more trips home,
  missing Power) and time lost to deaths.
