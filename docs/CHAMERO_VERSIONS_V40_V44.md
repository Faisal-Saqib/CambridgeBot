# Chamero v40–v44 — Per-Version In-Depth Reports

All online match data for platform versions 40–44. Panels: `top5-*` = ranks ~2–5,
`panel2-*` = ranks ~6–11. Plus one peer batch (v43 vs 1700–1800-rated teams).
Zero bot faults in all 175 games.

Live: **v44** (pinned). v42 was submitted but skipped — no campaign data.

Quick scoreboard:

| Version | Tagline | Games | W/L | Score | Deaths | Kills | Camp dmg | Gold | Lost |
|---|---|---|---|---|---|---|---|---|---|
| v40 | farm draft + health build | 45 | 0/45 | 138–1050 | 15.5 | 0.5 | 44k/120k | 1.9k/8.1k | 103 |
| v41 | 2000HP + grouping + new draft | 45 | 0/45 | 140–1088 | 18.7 | 0.8 | 41k/136k | 1.8k/9.1k | 120 |
| v42 | (skipped, untested) | — | — | — | — | — | — | — | — |
| v43 | + TP crystals | 45 | 0/45 | 130–1063 | 15.4 | 0.7 | 44k/125k | 1.8k/8.3k | 106 |
| v43 vs peers | same bot, ~1750 rating | 35 | **4/35** | 412–946 | 15.9 | 4.5 | 59k/126k | 2.9k/8.0k | — |
| v44 | + muster on 2 deaths | 40 | 0/40 | 122–1034 | 13.2* | 0.5 | 48k/125k | 1.9k/8.1k | 127 |

\* v44 split: top5 maps **9.3 deaths** (muster works), panel2 fight maps 19.9.

---

## v40 — "v15 + farm draft everywhere + health build" (platform v16)

- **Result: 0/45** (25 top5 + 20 panel2). Score 138–1050.
- **Draft:** Marcella+Ryth+Tavi+Vesper+Willow ×36 (old farm draft forced on all
  maps incl. brawls), Marcella+Ryth+Tavi+Vesper ×5, Marcella+Ryth+Vesper ×4.
- **Items/game:** Monster Str 13.0, Jungle HP 11.6, Bruiser HP 10.6, Durability
  8.2, Bruiser Focus 6.9, Bruiser Str 6.4 — the health build landed but the
  Monster/Jungle farming stack remains the core.
- **Consumables: ZERO** (locks died here — regression). Opponents: 185 locks +
  79 crystals.
- **Per-champ (all ours ~1/3 of opponent same-champ):** Vesper d3.6/k0.1/8.2k
  camp; Ryth d3.6/k0.1/9.9k; Marcella d3.0/k0.2/10.5k/97col; Tavi d3.3;
  Willow d3.0/7.2k.
  Opponents' Marcella 24.2k/382col, Vesper 37.5k/353col, Vendetta 26.4k/4.0k.
- **Maps:** the_line 0–1039 (d17.6), stampede 0–1025 (**d31.0**), crater
  7–1023 (d21.4), starfish 39–1040 (d29.2), anvil 18–1050 (d19.8),
  boss_battle 0–1218 (112k camp but 0 banked), expanse 490–1020,
  great_wall 475–1028 (lowest deaths d4.6).
- **Verdict:** farming the same draft on brawl maps confirmed fatal (deaths
  20–31 on stampede/crater/starfish). Health shards bought without the kill
  conversion to use them. Lock loss went unmeasured.

## v41 — "2000 HP + strong grouping + Prism/Marcella/Vendetta" (v17)

- **Result: 0/45.** Score 140–1088. **Deaths 18.7 — worst version on record.**
- **Draft:** HoR+Marcella+Prism+Varg+Vendetta ×28 (new meta draft),
  **Cassi+Issac+Ryth+Varg+Vendetta+Vesper ×8** (linked-body experiment),
  Marcella+Prism+Varg+Vendetta ×5, Marcella+Prism+Vendetta ×2, C&I variant ×2.
- **Items/game:** Bruiser HP 28.7 + Emblem HP 4.5 — heavy tank; Strength
  collapsed to 7.0. Pure-tank without damage.
- **Consumables: ZERO.** Opponents: 180 locks, 45 crystals.
- **Per-champ:** Cassi d7.1 / Issac d7.1 (linked-feeding disaster, dropped
  after); Vesper d6.8 (when drafted); Vendetta d3.9/k0.2/8.2k (can't pilot);
  Varg d3.3/k0.1; **Prism d3.3/k0.2 — the "carry" dies most**; Marcella
  d2.8/10.9k; HoR d2.3/6.4k.
- **Maps:** stampede **d45.2** (worst deaths ever recorded, 0–1073),
  starfish d37.0, anvil d28.0, crater d21.4, galaxy d20.0 — the "strong
  grouping" rule herded champs into 1v5 feeds. boss_battle 10–1443 (worst
  enemy score ever). Expanse 488–1029 stayed flat.
- **Verdict:** the right draft names with no pilot behavior made things
  *worse*. Grouping without an engage rule = feeding together. Took deaths
  from 15.5 → 18.7.

## v42 — skipped

Submitted (`93932fdd`) but **never pinned, never tested** — no campaign dir, no
note. Likely a superseded intermediate. No data exists; nothing to analyze.

## v43 — "v17 + teleport crystals to cut-off camps" (v18) [was live]

- **Result: 0/45 vs top-10; 4/35 vs 1700–1800 peers.**
- **Draft:** standardized HoR+Marcella+Prism+Varg+Vendetta ×36,
  Marcella+Prism+Varg+Vendetta ×5, Marcella+Prism+Vendetta ×4.
- **Items/game:** Bruiser HP 33.9 + Emblem 5.2 — max tank; Strength 6.0.
- **Consumables:** panel games 0 crystals — **but the feature works**: it
  bought **27 crystals in the 35 peer games** (0.8/g). The top5/panel2 map set
  contains no gap-separated maps, so the trigger never fires there. Locks
  still 0 (regression open).
- **Per-champ:** Prism d3.7/k0.2/10.3k/37col (still the dying carry);
  Vendetta d3.6/7.7k; Marcella d3.1/9.9k/76col; Varg d3.1/13.0k; HoR d2.8/5.4k.
- **Peer-batch detail:** kills 4.5 (6× the top-10 rate), wins on galaxy
  (1012–0 shutout), oasis (38 kills), tangle, great_wall. Close losses
  807–1095, 908–1000. Draft works against equals.
- **Verdict:** crystals are real but unverifiable on the standard panel;
  score got slightly worse vs top-10 (130 vs v40's 138). Deaths back to 15.4.

## v44 — "v18 + pull back home and muster when 2+ die in 40r" (v19) [LIVE]

- **Result: 0/40** (25 top5 + 15 panel2 — panel2 looks still running or
  partial: 3 games/map).
- **The first death fix that moved the number: top5-panel deaths 9.3** — down
  from 15.5–18.7 across all previous versions. Muster-on-2-deaths works on
  the big/top5 maps.
- **But panel2 fight maps still feed: 19.9 deaths** (stampede 0–1059, anvil
  10–1019, starfish 34–1014, galaxy 74–1007, fields 130–1039). On maps where
  the enemy hunts continuously, "muster at home" isn't enough — they die
  regrouped instead of alone.
- Camp damage on top5 maps **61k — best on record** (was 44k): survivors farm
  more when they stop respawn-walking into fights.
- Gems lost 171 on top5 (higher — retreating while carrying).
- **Items:** same tank-heavy build (Bruiser HP 35.2, Str 6.6). **Consumables
  still ZERO** — locks never restored; crystals 0 on panel (no gap maps).
- **Per-champ:** deaths per champ down to 2.5–3.2 (from 3.1–3.7): Prism
  d3.2/k0.0/10.9k; Marcella d2.6/9.4k; Vendetta d3.0/8.5k; Varg d2.6/**14.5k
  camp** (best farmer now); HoR d2.5/5.4k. Kills still ~0 — tank without
  teeth.
- **Verdict:** first version with a measurable improvement (deaths 16→9.3 on
  big maps, camp damage +39%). Fight-map feeding and zero offense remain.

---

## Cross-version trajectory

| Metric | v30–v39 avg | v40 | v41 | v43 | v44 | Direction |
|---|---|---|---|---|---|---|
| Score vs top-10 | ~160 | 138 | 140 | 130 | 122 | **worse** |
| Deaths | ~16 | 15.5 | 18.7 | 15.4 | **9.3/19.9** | **improving** (split) |
| Camp dmg | ~46k | 44k | 41k | 44k | **61k** | **improving** |
| Kills | ~1.0 | 0.5 | 0.8 | 0.7 | 0.5 | flat-bad |
| Locks | ~0.7 | 0 | 0 | 0 | 0 | **regressed, unrestored** |
| Crystals | 0 | 0* | 0* | 27 (peers) | 0* | works, panel-blind |
| Draft | farm | farm | meta | meta | meta | meta since v41 |

\* panel maps contain no gap-separated terrain; feature can't fire.

**Bottom line:** v44 is the first version since v31 with a real improvement
(deaths + camp damage on big maps). Everything else — kills, score, locks,
pilot quality on the meta draft — is still unfixed. Next measured targets:
fight-map muster variant, focus fire for kill conversion, restore locks, and
a peer-rated panel for iteration signal (4 wins vs ~1750 teams vs 0 wins vs
top-10 means the panel, not the bot, was the bottleneck for seeing progress).
