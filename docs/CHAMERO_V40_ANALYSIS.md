# Chamero v40–v43 Analysis + Peer-Batch Results (2026-10-29)

Scope: all online games from v40 onward — `top5-v40/v41/v43` + `panel2-v40/v41/v43`
(135 games vs ranks ~2–11) — plus a new 35-game batch vs 1700–1800-rated teams
queued for this report (ranks ~138–212). Total: **170 games analyzed, 0 faults.**

Live bot: **v43 (pinned, "v17 + teleport crystals to cut-off camps")**.

Prior report: `CHAMERO_V30_ANALYSIS.md` (v30–v39, 400 games).

## 1. Version scoreboard — v40+

| Version | Change | Games | Wins | Score | Deaths | Kills | Camp dmg | Gold | Gems lost |
|---|---|---|---|---|---|---|---|---|---|
| v39 (ref) | high-HP camps | 45 | 0 | 165–1054 | 16.0 | 0.8 | 46k/124k | 2.2k/8.2k | 75 |
| v40 | farm draft everywhere + health build | 45 | 0 | 138–1050 | 15.5 | 0.5 | 44k/120k | 1.9k/8.1k | 103 |
| v41 | 2000 HP + grouping + Prism/Marcella/Vendetta draft | 45 | 0 | 140–1088 | **18.7** | 0.8 | 41k/136k | 1.8k/9.1k | 120 |
| v43 | v17 + TP crystals | 45 | 0 | 130–1063 | 15.4 | 0.7 | 44k/125k | 1.8k/8.3k | 106 |

**All three versions: 0/45.** Score got *worse* than v39 (165 → 130–140). Against
top-10 opposition, v40–v43 changed nothing measurably — the same maps lose the
same way (the_line, stampede, anvil, crater, starfish all ~0–42 avg score).

## 2. New peer batch — first real wins since v31/v35

Seven 5-game groups vs 1700–1800-rated teams: **4/35 (11%)**.

| Opponent | Rating | Result |
|---|---|---|
| Just for fun | 1701 | **1/5** (win: 02tangle 1029–961) |
| Antarktier | 1720 | **1/5** (win: 00galaxy 1012–0 — opponent scored zero) |
| Stranger Danger | 1781 | **1/5** (win: 00great_wall 1006–898) |
| The something | 1800 | **1/5** (win: 00oasis 986–488, 38 kills) |
| Kamikaze | 1796 | 0/5 |
| cache_v2 | 1775 | 0/5 |
| Doxford | 1761 | 0/5 |

Averages vs peers: score 412–946, kills **4.5** (vs ~0.7 vs top-10), deaths 15.9,
collected 508 vs 1,061, camp damage 59k vs 126k, gold 2.9k vs 8.0k.

**The bot is rating-banded correctly**: ~1700–1800 opponents yield competitive
games (4 wins, several close losses like 807–1095, 908–1000); top-10 opponents
are unwinnable. The panel used to measure versions is far above our level —
**all version comparisons since v30 have been measured against teams we cannot
beat, which is why every version reads 0/45.**

## 3. Improvements made since v39 (what actually changed)

Measured, not claimed:

- **TP crystals now work — and the panel can't see it.** v43 bought **27
  crystals vs peer teams** (0.8/game) but **0 vs top-10** — because the fixed
  panel map set (line/wall/boss/expanse/crater/anvil/stampede/starfish/galaxy/
  fields) contains **no gap-separated maps**. The feature fires only where it
  matters (islands/pond-type terrain), which the test panel never visits.
- **Health itemization landed**: Bruiser Health 33.9/game + Bruiser Emblem
  Health 5.2 — matches opponent tank itemization (they buy ~41 + 7.8).
- **New draft deployed**: HoR+Marcella+Prism+Varg+Vendetta on 5-pick;
  Marcella+Prism+Vendetta on 3-pick — now a real meta draft instead of
  Vesper+Ryth+Tavi.
- **Kills tripled vs peers** (4.5/game) — the Vendetta/Marcella damage draft
  converts at peer level even though it can't vs top-10.
- **Wins exist**: galaxy 1012–0 is the first clean shutout ever recorded;
  oasis was a 38-kill brawl win — proof the fight kit can work vs equals.

## 4. Still lacking — the measured gaps

### L1. Deaths unchanged across 10 versions

15.4–18.7 deaths/game in every version v30–v43 vs top teams, and still **15.9
vs peers**. Opponent deaths: 1.3–1.8 (top-10), ~14 (peers). Our champions die
3.1–4.3×/game *each*; the respawn-muster and grouping changes moved nothing.
This is the single most stable broken metric in the bot.

### L2. Per-champion output is ~1/3 of opponents on every metric

v43 vs top-10, our best vs their best:
- our Marcella: 9.9k camp, 76 col — their Marcella: 23.4k, 354 col
- our Vendetta: 7.7k camp, 0.2 kills — their Vendetta: 30.5k, **4.2 kills**
- our Heart of Ruin: 5.4k camp — theirs: 20.0k
- our Prism "carry": **3.7 deaths, 0.2 kills, 37 collected** — the carry dies
  most and farms least on the team.

The draft is now correct but **the pilots can't fly the champions** — Vendetta
without dive logic is just a frail farmer; Prism without escort logic is a free
kill.

### L3. Consumables collapsed to zero in team games

Since v40: **0 Altar Locks purchased in 135 panel games** (opponents: ~4/game,
185 total). v30–v39 bought ~0.7 locks/game — the lock logic was lost when the
item build changed to Bruiser-health. Locks cost 10 gold; this is a regression.

### L4. Item balance over-rotated to pure tank

v41/v43 buy 29–34 Bruiser Health shards but only **6–7 Bruiser Strength** —
opponents buy 62–65 Strength *and* 41–44 Health. We tank without damage: kills
stay ~0.2/champ while theirs hit 3–4. On peers we also buy 0 Power-family items
(opponents buy **30.2 Power Strength + 15.1 Power Health/game** — a whole item
family we ignore).

### L5. Camp damage plateau ~44k vs their ~125k

Unchanged since v30 across six versions and two draft overhauls. Camp selection
was fixed (v15); the bottleneck is now **clear speed + survival**: champions die
mid-clear (3+ deaths each), walk too far between camps, and can't contest the
rich camps. Related: boss_battle camp damage improved to 139k (v43) but score
still 23–1259 because all that damage doesn't reach the gate objective.

### L6. Cassi & Issac experiment confirmed bad, quietly dropped

v41 drafted them 10× — both bodies died **7.1/game** (linked feeding). v43
removed them. Correct call, but cost 8 games to learn.

### L7. Deterministic panel blindness

v41 and v43 share identical stats on several maps (the_line 16–1034, crater
22–1029, great_wall 388–1066) — `--source-group` replays make the same game
appear in both version rows. The "45 games" per version is really ~10–15 unique
matchups.

## 5. Mistakes identified

1. **Testing every version vs unwinnable opponents.** All v30–v43 data is vs
   ranks 2–11. Zero wins in 400+ games means the panel provides no signal — a
   10% improvement can't be seen. The peer batch (4/35) produced more
   information in 35 games than the last 400 top-10 games combined.
   → **Test each version vs ~our rating (±200) AND one top-team group.**
2. **Shipping a headline feature the test panel can't exercise.** TP crystals
   work — on maps the panel never plays. → Panel must include gap-separated
   maps (islands, pond, ambush, gemcombat4/5) or feature testing is blind.
3. **Draft adoption without pilot behavior.** Vendetta/Prism/HoR are drafted
   because they're meta, but the bot lacks: dive/burst timing (Vendetta),
   escort+retreat carry logic (Prism), and HoR's positioning. Draft changes
   without behavior changes just rename which champions die.
4. **Item rotation without kill conversion.** Going from all-offense to
   34-health shards cut deaths only 16→15.4 while kills stayed ~0.5 — we
   survive longer inside losing fights. Tank items only pay off paired with
   focus fire + a finisher.
5. **Lost the lock logic in the item refactor** — silent regression nobody
   measured because panels don't track consumables.

## 6. Recommendations — ordered

| # | Change | Evidence |
|---|---|---|
| 1 | **Retier the test panel**: 1700–2000-rated opponents for iteration signal; keep 1 top-5 group for aspiration. The peer batch already produced 4 wins. | §2, §5.1 |
| 2 | **Add gap-maps to the panel** (islands, pond, ambush) so crystal logic is exercised; crystals already work — verify with 2–3 games there. | §3 |
| 3 | **Serial-death breaker** (2 deaths in 80r → regroup until ≥3 alive). Deaths are the #1 stable broken metric across 10 versions. | §4-L1 |
| 4 | **Pilot the drafted champions before drafting them**: Vendetta needs dive/finish rules; Prism needs escort + retreat-at-threat; HoR needs positioning rules. Measure per-champ kills/camp vs opponent same-champ (currently ~1/3). | §4-L2 |
| 5 | **Restore Altar Locks** (~4/game on altar maps) — free regression fix. | §4-L3 |
| 6 | **Rebalance items: Bruiser Health ~20 + Strength ~25**, add Power main-stat for Marcella after round ~400. Pure tank = slow death. | §4-L4 |
| 7 | **Kill-conversion focus fire**: lowest-HP target in range; kills 0.7 vs top-10 / 4.5 vs peers vs opp 14–17. Damage exists; finishing doesn't. | §4-L2 |
| 8 | **Boss_battle objective step**: camp damage is finally real (139k) but score 23 — the gate needs a break-and-tribute window, not more clearing. | §4-L5 |

## 7. Verification protocol for next version

- Fixed version, ≥5 online games vs ~our rating before any tweak (per standing
  rule) — the peer batch satisfies this for v43 as baseline: **4/35, kills 4.5,
  deaths 15.9, collected 508**.
- Track consumables + per-champion metrics every batch (the two things that
  silently regressed this cycle).
- Success for the next version: deaths <13 vs peers OR camp damage >75k vs
  peers — not "0/45 → still 0/45 vs top-10".
