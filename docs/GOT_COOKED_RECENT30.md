# Got Cooked — Last 30 Games Report (2026-10-29 ~11:00 UTC)

The 30 newest finished matches: six 5-game groups vs Quantum Wardens (our bot),
67, Antifreeze, Imagine Winning, slop, Squishy. 25 unranked + 5 ranked.
**Record: 13/30. Zero bot faults.**

Data: `matches/gc-recent30.json` + `matches/gc-recent30-analyzed.json`.
Prior reports: `GOT_COOKED_ANALYSIS.md`, `GOT_COOKED_RECENT100.md`,
`GOT_COOKED_MAP_STRATEGY.md`, `GOT_COOKED_FARMING_REPORT.md`.

## 1. Headline: the deaths are back

| Metric | Recent-100 batch | This 30 | Opponents (this 30) |
|---|---|---|---|
| Kills/game | 9.1 | 12.9 | 14.0 |
| Deaths/game | 9.0 | **15.9** | 14.0 |
| Collected | 809 | 669 | 858 |
| Camp damage | 86k | 60k | 93k |
| Champ damage | 27k | 36k | 40k |
| Gold | 5,414 | 4,799 | 6,076 |
| Healing done | 0 | **0** | 1.3k |

The survival improvement seen in the last batch **regressed**: deaths nearly
doubled (9.0→15.9), and they are out-killed again (12.9 vs 14.0). Wins are now
*bloody* — they win with 13.7 deaths/game, meaning victories come from kill
races, not control. Score 506–681 overall.

Extreme single-game deaths: **the_line 41, eight 34, contest 32, gemfight 26,
crater 25 (a win!), rushbait 23 (win), quarry 22 (win)**. They can win while
dying 20+ times — but only against weaker farmers. Against anyone who also
farms, the deaths hand over the game.

## 2. Per-game results

| Opp | Map | Result | Score | K/D | Collected | Camp dmg |
|---|---|---|---|---|---|---|
| 67 | big_world | L | 68–1002 | 0/0 | 72/1,023 | 16k/172k |
| 67 | concentrated_wealth | L | 187–1048 | 9/16 | 428/1,122 | 87k/111k |
| 67 | the_farm | L | 138–1091 | 2/12 | 314/1,091 | 39k/117k |
| 67 | fields | L | 908–1000 | 22/21 | 1,072/1,031 | 155k/116k |
| 67 | gift_wrapping | L | **0–1001** | 0/1 | **0/1,001** | 2k/213k |
| Antifreeze | contest | L | 0–1000 | 23/32 | 200/1,000 | 58k/123k |
| Antifreeze | quarry | W | 1044–376 | 26/22 | 1,178/562 | 45k/63k |
| Antifreeze | split | W | 1076–366 | 13/19 | 1,470/529 | 118k/33k |
| Antifreeze | islands | L | **0–1036** | 2/13 | **0/1,036** | 9k/147k |
| Antifreeze | famine | L | 676–1016 | 1/13 | 727/1,132 | 66k/122k |
| Imagine Winning | crater | W | 1005–634 | 12/20 | 1,161/781 | 69k/88k |
| Imagine Winning | fragment | W | 760–267 | 16/13 | 806/377 | 119k/110k |
| Imagine Winning | road_of_riches | L | 299–1002 | 0/12 | 929/1,077 | 53k/72k |
| Imagine Winning | rushbait_v2 | W | 496–161 | 2/23 | 613/460 | 82k/47k |
| Imagine Winning | guardians | W | 0–0† | 4/5 | 131/127 | 8k/11k |
| **Quantum Wardens** | fragment | W | **1001–21** | 29/1 | 1,014/65 | 170k/36k |
| Quantum Wardens | gemfight | L | 155–1005 | 5/17 | 448/1,012 | 27k/38k |
| Quantum Wardens | starvation | L | 242–1018 | 7/21 | 296/1,102 | 24k/98k |
| **Quantum Wardens** | stalactites | W | 1022–224 | 30/16 | 1,099/329 | 19k/5k |
| **Quantum Wardens** | gemcombat4 | W | 1001–707 | 14/7 | 1,155/1,001 | 18k/14k |
| Squishy | crater | W | 1010–166 | 24/25 | 1,158/682 | 54k/60k |
| Squishy | gemfight | L | 740–1060 | 16/26 | 1,281/1,700 | 38k/75k |
| Squishy | lanes | W | 1003–647 | 13/10 | 1,120/1,029 | 130k/160k |
| Squishy | stampede | W | 0–0† | 36/9 | 160/0 | 57k/43k |
| Squishy | the_farm | W | 677–75 | 8/8 | 867/1,488 | 73k/177k |
| slop | collision | L | 296–1023 | 15/10 | 439/1,100 | 74k/118k |
| slop | eight | L | 38–1000 | 3/**34** | 156/1,100 | 34k/150k |
| slop | pilgrimage | L | 386–401 | 23/15 | 504/519 | 88k/91k |
| slop | the_line | L | 144–1001 | 21/**41** | 273/1,045 | 34k/114k |
| slop | crossing | L | 807–1095 | 12/16 | 985/1,227 | 49k/80k |

† 0–0 wins = tiebreak victories (kills tiebreak) on guardians/stampede — won the
fight, banked nothing.

## 3. Issues — ranked by measured damage

### I1. Serial respawn-feeding is back, worse than ever

15.9 deaths/game; individual games of 41, 34, 32, 26, 25 deaths. Per-champion:
Vesper 4.0, Tavi 3.9, Varg 3.9, Ryth 3.8 — the whole team respawn-feeds, not
just the frontline. On **eight** (34 deaths, 38–1000) and **the_line** (41
deaths, 144–1001) one lost fight cascades into 10+ solo re-entries.

**Fix:** death-stagger breaker — after 2 allied deaths within ~80 rounds, all
survivors hold position (or retreat to spawn) until ≥3 bodies are alive. Nobody
re-enters a lost fight alone. This single rule is worth ~8–12 deaths/game on
brawl maps.

### I2. Gap-separated maps remain automatic losses — twice in 30 games

- **islands: 0–1036, collected 0** (9k vs 147k camp damage)
- **gift_wrapping: 0–1001, collected 0** (2k vs 213k)
- Still **zero Teleport Crystals purchased** (opponents buy 0.7/game vs them).

**Fix:** buy 1–2 crystals on any map where >5% of gems are outside the spawn
component; designate one champion as hopper. Two guaranteed-loss maps per 30
games = ~6% of all games forfeited at draft time.

### I3. Big-map navigation collapse

- **big_world: 68–1002**, 16k vs 172k camp damage — champs get lost in the maze
  (0 kills, 0 deaths: they never even found the enemy)
- **the_farm: 138–1091**, 39k vs 117k camp damage
- **concentrated_wealth: 187–1048**

**Fix:** precomputed BFS distance fields + cluster-trip job scoring (score a
region of camps, not one camp). Their champs spend turns walking; on a 41×30
maze map that's the whole game.

### I4. Camp damage deficit on anything that isn't a brawl

60k vs 93k overall; losses show **50k vs 115k**. Even in a won game
(the_farm 677–75) the opponent did 177k camp damage to their 73k — GC won on a
banking technicality (opp collected 1,488 but submitted 75). Varg is the weakest
farmer: **7.8k camp damage/game**, half of Tavi's.

**Fix:** Varg's job scoring/HP accounting — he's being sent to camps he can't
clear or spending fights' worth of HP per camp. Also the trip-cluster scoring
above.

### I5. Damage still doesn't convert to kills

36k champ damage → 12.9 kills; opponents' 40k → 14.0 kills. No execute in the
draft (still no Vendetta; opponents draft her + HoR in most games — one
opponent even ran **Prism**). Wounded enemies escape and heal (GC heals 0,
always).

**Fix:** focus-fire target = lowest-HP enemy in range, not nearest; or restore
Vendetta on 3–4 pick brawl drafts (the_line, eight, contest — exactly where the
41/34/32-death games are).

### I6. Tributes still tiny

737 tributes, avg **21 gems** — carriers still leave fights to bank pocket
change. On the_line/gemfight that's a fighter missing per tribute.

**Fix:** minimum tribute threshold ~30–40 on fight maps, and never interrupt a
contested objective to bank <20.

### I7. Carriers die with the bag

Losing games show collected ≪ opponent even when kills are competitive —
deaths donate bags (killer steals carried gems). On gemfight they collected
1,281 (more than enough to win) but submitted 740 to slop's 1,060 — 26 deaths
bled it away.

**Fix:** carriers retreat at first enemy contact; tribute ≥30 before crossing
mid-map.

## 4. Tailored map guide — every map in this batch

### 00eight (0/1 this batch, 0/3 overall) — THE serial-feeding map
- 34 deaths → 38 points. Champs re-enter the center alone.
- **Plan:** after first lost fight, concede center permanently. Farm edge camps
  in pairs. Re-engage only when all bodies alive simultaneously. Expect a
  500–900 loss instead of 38–1000.

### 00the_line (0/1, 1/2 overall)
- 41 deaths, forced single-lane brawl.
- **Plan:** this map is decided by ONE teamfight — go as a full group at round 0
  behind Ryth, focus-fire the enemy carrier first (bag steal), tribute before
  engaging. If the first fight is lost, farm the rear camps; do NOT re-contest.

### 00contest (0/1)
- 23 kills but 32 deaths — the objective camp fight is unwinnable head-on.
- **Plan:** contest only with full group; if denied, split-farm the outer camps
  (they exist — opponents leave them while contesting). 200 collected is a
  starvation loss; even losing the objective, ~700 is available on the rim.

### 00gemfight (0/2)
- Collected 448 and 1,281 — feast-or-famine. Deaths 17 and 26.
- **Plan:** the gems are there to be taken (Squishy game proved 1,281 exists) —
  the failure is submission. Carriers bank at ≥30 immediately after each pickup;
  fighters screen, never chase past midfield.

### 01islands / 02gift_wrapping (0/2 combined, collected 0 total)
- **Plan:** TP crystal hopper, period. Until purchased these are draft-time
  forfeits — no strategy exists for gems that can't be walked to.

### 00big_world / 01the_farm / 01concentrated_wealth (0/3)
- Navigation/coverage losses, not fights.
- **Plan:** BFS distance fields at init; split champions to quadrant regions via
  cluster-trip scoring; tribute at nearest altar. On the_farm specifically,
  their 73k vs opp 177k camp damage = wrong camp selection (hitting small near
  camps while the farm camps respawn untouched).

### 00fragment (1/1 — **beat US 1001–21**)
- They did 170k camp damage to our 36k and collected 1,014. This is what their
  A-game looks like: grouped fast clear of the fragment clusters, carrier
  escorted.
- **Plan (for them):** repeat whatever this replay does — it's their best tape.

### 02stalactites / adgato_gemcombat4 (2/0 — **both vs us, won**)
- 30 kills on stalactites. Small-map brawl + quick bank. Keep as-is.

### 00stampede (1/0, tiebreak)
- 36 kills, 0–0 → won on kills tiebreak. They banked nothing and collected only
  160 — pure brawl worked but is fragile; one lost fight = 0–1000 instead.
- **Plan:** fine as-is; maybe bank ≥10 per carrier pass for insurance.

### 02guardians (1/0, tiebreak 0–0)
- First guardians win ever — but 8k camp damage says they won a mutual-nothing
  game on kills, not by clearing guardians. The real fix (2-champ chipping +
  health items first) still stands.

### 00quarry / 00split / 00crater / 00rushbait_v2 / 00lanes (5/5 wins)
- Their working set: high-kill brawls (13–26 kills) with enough incidental
  farming. Only flaw: 19–25 deaths in each — apply the retreat-at-35%-HP rule
  and these become clean wins.

### 00collision / 00pilgrimage / 02crossing / 02famine / 00road_of_riches (0/5)
- Mid-size maps lost on farm: collected 439–985 vs 1,000–1,227 with competitive
  kills (12–23). Fights aren't the problem — coverage is.
- **Plan:** spread the farm (their farm radius is too tight on mid-size maps),
  one champ per region, tribute at ≥30.

### 01starvation (0/1 vs us)
- 296 vs 1,102, 24k vs 98k camp. Starvation punishes slow clears — same
  big-map routing fix.

## 5. Improvement guide — ordered implementation

| # | Change | Addresses | Expected |
|---|---|---|---|
| 1 | Death-stagger breaker (2 deaths → no re-entry until ≥3 alive) | I1 | −8 deaths/game on brawl maps; eight/the_line go from 38–1000 to ~600-900 losses or wins |
| 2 | TP crystal hopper on gap maps | I2 | islands/gift_wrapping 0% → 30–50% |
| 3 | BFS fields + cluster-trip job scoring | I3, I4 | +40% camp damage on big maps; fixes big_world/the_farm/starvation |
| 4 | Wounded retreat at ~35% HP + carrier-no-fight rule | I1, I7 | Wins stop costing 20 deaths; gemfight/collected maps stop bleeding bags |
| 5 | Kill-priority targeting (lowest HP) or Vendetta on brawl drafts | I5 | kills/damage ratio 12.9/36k → ~16/36k |
| 6 | Tribute floor ~30–40 + bank-before-fight | I6, I7 | fewer mid-fight exits; stops 0-banking tiebreaks |
| 7 | Varg farm audit (7.8k camp — lowest on team) | I4 | he's either over-claiming hard camps or being pulled into fights; check his job scores |
| 8 | Frontline health items (more Durability/Bruiser Health on Ryth/Varg) | I1 | attrition brawls become winnable — they now buy 15.8 Durability-Health vs opponents' heavier frontline builds |

## 6. Note for us (Quantum Wardens)

They went **3/5 vs our live bot this batch** — fragment 1001–21 (170k vs 36k
camp!), stalactites 1022–224 (30 kills), gemcombat4 1001–707. Our v24 loses to
them on small fast-clear maps where their grouped rush works. Their losses to
us were gemfight/starvation — our wider farming won. **Our edge over them is
farm maps, not brawls** — consistent with everything else in this data.

## 7. Verification

- Re-run this 30-game panel after change #1: deaths/game must drop below ~10
  while kills stay ≥11.
- After #2: islands/gift_wrapping collected must go 0 → 300+.
- After #3: big_world camp damage 16k → 80k+.
- Guard the wins: quarry/split/crater/stalactites must stay ≥60%.
