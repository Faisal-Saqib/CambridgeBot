# Got Cooked — Map-Wise Strategy & Fight Improvement Guide

Built from all 200 analyzed games (84 wins over 61 maps). Every number below is
measured from match summaries. The brief: **they lose most of their fights** —
this guide identifies where fights happen, why they lose them, and the concrete
per-map + global fixes.

Data: `matches/gotcooked/summaries/`, aggregates in `matches/gc-recent100-analyzed.json`.

---

## 1. The fight problem in one table

Split all 61 played maps by what actually decides the game:

| Cluster | Maps | Record | Signature |
|---|---|---|---|
| **A. Fight & win** | vault 5/5, split 4/5, collision 3/3, gemcombat1/2/5 11/11, corners 2/2, hooks 2/2, crater/quarry/gemfight/the_line/starfish/ribs/etc. | ~45W | High kills (15–30+), wins follow kills |
| **B. Fight & lose** | anvil 6/14, eight 0/2, gold_rush 1/2, elk_arena 0/1, monolith 1/13, guardians 0/4, gem_fields 0/2, lost_world 0/2, dunes 1/2, lanes 3/14, uncharted_lands 2/2*, pilgrimage 1/3 | ~18W | High deaths (14–30+), fights happen and are lost |
| **C. Farm & lose** | expanse 2/14, rows 2/7, fields 0/5, geodes 0/5, tangle 1/4, quadrants 1/3, big_world 0/3, corridors 0/2, gift_wrapping 0/2, the_pond 0/2, islands 0/1, ambush 0/1, great_wall 0/1, famine 1/4 | ~7W | Low kills (<4), out-collected 1.5–18× |
| **D. Mixed/close** | packs 6/14, stampede 3/4, crossing 2/3, elkring 1/2, interlock 1/2, famine 1/4 | ~14W | Both levers matter |

Cluster B is the user's observation made precise: **anvil, eight, gold_rush,
elk_arena, monolith, guardians, gem_fields, lost_world, lanes** — these maps
force fights and GC loses them. ~39 losses trace to this cluster.

Cluster C is a different bug (terrain access + camp clearing — covered in
`GOT_COOKED_FARMING_REPORT.md`), but it interacts with fights: on pure-farm maps
there is nobody to kill, so the brawl kit is dead weight.

---

## 2. Why fights are lost — the four measured causes

### 2.1 The frontline dies; the carry watches

Per-champion deaths (recent 100): Tavi 2.4, Ryth 2.4, Vesper 2.6 — but Marcella
only **1.5** with 4.1 kills. Fights open with Ryth/Tavi/Vesper trading into a
group, dying, and Marcella cleaning up or retreating. On fight-loss maps deaths
hit 15–30/game: that is serial 1-for-1 trading plus respawn re-engagement, not
one lost teamfight.

### 2.2 Zero healing, zero sustain items

**0 healing done across the last 100 games** while opponents heal ~2k/game (more
on brawl maps). No Willow in any draft. Item buys are Bruiser Strength + Focus
with a token 19 Durability-Health shards — the frontline has damage, not bulk.
In a sustained fight they lose the attrition race every time: same damage, less
effective HP, no recovery between engagements.

### 2.3 No retreat discipline — respawn-die loops

anvil averages **20.5 deaths/game**, eight **30**, elk_arena **47**, gold_rush
**28**. Those numbers are only possible if dead champions walk straight back
into the fight alone. Each death also costs ~60 rounds of farming + carried gems.
The pattern in loss replays: first death ~round 200, then staggered re-entries
that feed the same enemy group 3–5 times.

### 2.4 No Vendetta — no finishing power

Vendetta was dropped from every draft. Recent drafts are Marcella+Ryth+Vesper
(+Varg)(+Tavi) — sustained brawlers with **no execute**. Opponent drafts run
Vendetta in ~50% of games and Heart of Ruin in ~70%. Result: GC wins damage
exchanges but enemies escape at low HP and heal — their 27k champ damage
converts to only 9 kills, while opponent 28k converts to 10.8 kills (on GC's
deaths). Damage without finishing is wasted fuel.

### 2.5 Secondary: tiny tributes during fights

4,269 tributes at avg **17 gems** in the recent 100 — on fight maps, carriers
break off mid-fight to bank trivial amounts, arriving late or not at all. Top-20
census correlation: small-frequent-tribute habit → 35% win rate.

---

## 3. Global fight rules to implement (before any map logic)

These five rules address every cause above and are map-independent:

1. **Engage only with a body advantage or a confirmed kill.** Count enemies
   within ~10 tiles; if not (allies ≥ enemies+1) AND no enemy under ~40% HP
   reachable in 2 turns, disengage. This single rule kills the serial-death
   loop: outnumbered champs simply never enter.
2. **Death-stagger breaker.** If 2+ allies died in the last ~80 rounds, survivors
   hold near spawn/the rear camp cluster until the group is ≥3 bodies. Nobody
   walks back in alone. (This is what turns anvil's 20 deaths into ~8.)
3. **Frontline gets health, carry gets damage.** Move ~40% of the Bruiser
   Strength budget on Ryth/Varg into Bruiser/Durability Health; stack Marcella's
   Strength/Focus + a Power main-stat. Dead champs do 0 DPS — their frontline
   currently buys glass.
4. **Retreat wounded, not dead.** Any champ under ~35% HP with enemies in range
   disengages toward spawn; carriers with >15 gems never fight at all. A live
   champ at half HP re-enters in 20 rounds; a dead one in ~60 and drops the bag.
5. **Bring back a finisher.** Re-add **Vendetta on fight maps** (3-pick brawls
   especially — their old Vesper+Vendetta+Marcella core) OR give Marcella a
   strict kill-target priority: lowest-HP enemy in focus-fire range, not
   nearest. Their damage is fine; the conversion to kills is not.

Optional but high-value: **Willow instead of Tavi on 5-pick fight maps.** Tavi is
the measured weak link (0.9 kills, 2.4 deaths, least gold) and GC fields zero
healing while every opponent heals. A healing support behind a Ryth/Varg wall is
exactly what sustained brawls reward.

Also: **tribute threshold ≥30 gems on fight maps** — carriers bank only
meaningful amounts and stay for the fight that decides the map.

---

## 4. Per-map strategy — Cluster B (fight & lose)

These are the maps where fight improvement converts directly to wins.
Ordered by games played.

### 00anvil — 6/14, kills 10.0 vs 17.4, **deaths 20.5**

- The worst fight map. Tiny arena, one approach; their frontline meets the enemy
  group head-on and respawn-feeds.
- Plan: **contest center as a full group once, not continuously.** First
  engagement with all 3 bodies + focus fire on lowest HP. If it fails, concede
  the arena, farm the two side camps in pairs, and re-contest only when respawns
  align (all 3 alive within ~30 rounds of each other).
- Draft: restore Vendetta for Tavi/Ryth flex — anvil rewards burst, not sustain.
- Items: frontline health first (anvil fights start ~round 150 — first buys
  should be 2× Durability/Bruiser Health on Ryth, not Strength).

### 00monolith — 1/13, deaths 14.0, collected 697 vs 1,183

- Double failure: they fight AND lose the farm. The boss camp guards the gems;
  they neither clear it (108k vs 165k camp dmg) nor survive the skirmishes.
- Plan: **decide one identity — siege or raid.** Recommended raid: skip the
  monolith entirely, take the outer camps (which opponents leave while sieging),
  and fight ONLY defensively — engage enemy champs that leave the siege line,
  never dive into it. 14 deaths/game means they keep charging the fortified
  group.
- If sieging: 2-champ chip protocol (hit, back off at 50% HP, rotate), never
  3-in; the 3rd farms. One death at the boss = abandon for 80 rounds (their
  death-blacklist window).

### 00lanes — 3/14, kills 3.2, deaths 8.3, camp 107k vs 156k

- Fights are scattered (3.2 kills is low) and they lose the farm anyway — lanes
  punishes their grouping because the map rewards lane-splitting.
- Plan: **one lane per champ, never collapse.** Ryth top, Marcella mid (nearest
  the altar), Vesper/Varg bottom. Fight only intruders in your lane; do not
  rotate to help — a rotation on lanes means two lanes of camps go dark for
  ~40 rounds each.
- This map alone argues against their "group up" instinct — it's the opposite
  of anvil.

### 02guardians — 0/4, deaths 16, camp **17k vs 136k**

- Worst camp-damage ratio in the dataset. Guardian camps shred them (16 deaths,
  many to camps not players) and they still don't clear them.
- Plan: **don't fight the guardians early.** Farm the free outer ring first;
  engage guardian camps only with 2+ champs and purchased Health shards (2–3
  before first attempt). If a champ dies to a camp, blacklist it — camps
  preserve damage, so 2 champs chipping beats repeated solo suicides.
- This map alone justifies the frontline-health item change.

### 00eight — 0/2, **deaths 30**, 232 vs 1,050 collected

- The purest serial-feeding case: 30 deaths means champions re-engage within
  seconds of respawning, ~15 times each.
- Plan: apply the death-stagger breaker hard — after 2 team deaths, NOBODY
  crosses mid-map until 3 alive. Ban solo initiations. If the center group is
  lost once, play the edge camps for the rest of the game; a farmed loss (600
  vs 1,050) beats a fed loss (232).

### 01gold_rush — 1/2, deaths 28 vs opp 22.5

- Mutual-slaughter map where they lose the exchange rate.
- Plan: they actually out-brawl here historically (stampede shows the kit works
  when ahead). Same fix as anvil: group-engage once, then pairs. Priority
  target = enemy carrier (killer steals the bag — on gold_rush one steal can
  swing 100+ gems).

### 02gem_fields — 0/2, deaths 15.5, collected 932 vs 1,060

- Collect nearly enough but die 15.5 times — fights cost the difference.
- Plan: this map doesn't need fights at all (gems are open). Farm-and-dodge:
  champs retreat at 8+ tiles from enemies, tribute at ≥30. The 932→1,200 needed
  to win comes from 15.5 deaths × ~20 rounds dead time returned to farming.

### 00lost_world — 0/2, kills 21.5 vs deaths 23.5

- They fight fine (21.5 kills!) and still lose — deaths erase it. The win is in
  the respawn management, not damage.
- Plan: same staggered-respawn rule. Also: after winning a fight, scatter to
  camps for ~40 rounds instead of pushing the enemy spawn — spawn-adjacent
  chases are where the 23.5 deaths come from.

### 01elk_arena — 0/1, **60 kills but 47 deaths**, 636 vs 828

- Literal coin-flip slaughter — 60 kills should never lose. They lost the
  exchange because deaths feed gems: every death hands the enemy the bag.
- Plan: on pure-arena maps, **empty pockets before fighting** — tribute ≥15
  gems BEFORE engaging, never carry >10 into a brawl. 47 deaths × stolen bags
  is the entire margin.

### 00dunes — 1/2, deaths 18.5 vs only 8.0 opponent kills

- Deaths exceed opponent kills 2:1 → **most deaths are to camps.** Self-inflicted.
- Plan: camp-HP awareness — don't solo camps above ~60% of champ HP in damage
  output; pair up for the two big dune camps or leave them. Chasing kills here
  is secondary to not suicide-chipping.

### 02uncharted_lands — 2/2 wins but 18 deaths/game

- They win despite 18 deaths — the brawl works but is fragile; one bad exchange
  flips it.
- Plan: keep the aggression, add the wounded-retreat rule only. Don't fix what's
  winning.

### 00pilgrimage — 1/3, 14.3 kills vs 8 deaths, collected 461 vs 649

- Weird profile: decent fight numbers, low everything else. Long map, they win
  skirmishes but can't cover ground.
- Plan: pair-champ escorts (fighter+carrier per camp cluster) — single carriers
  get picked off on the long walk to the altar, which is where the 8 deaths and
  low submission come from.

---

## 5. Per-map strategy — Cluster A (fights already win — protect them)

These are the identity maps. The goal is **don't regress** while fixing B/C.

- **00vault (5/5, 16.8 kills, 4.4 deaths):** the template — small map, group
  engage, low deaths. Whatever the bot does here (grouped 3-man engagements with
  focus fire) should be exported to anvil/eight. Diff the movement/engage logic
  on vault vs anvil to find what differs.
- **00split (4/5, 13.6 kills, 18 deaths):** wins on kills but feeds — the
  wounded-retreat rule alone probably takes this to 5/5.
- **00stampede (3/4, 33.8 kills!):** proof the kit can dominate a forced-brawl
  map when ahead. Keep the round-0 converge.
- **adgato_gemcombat 1/2/5 (11/11 combined), 00collision, 00corners, 00fragment,
  02treasure_box, 01hooks, 00crater, 00quarry, 00gemfight, 00swirl, 00the_line,
  01starfish, 00contest, 00ribs, 01shortcut:** mixed win rates with high kills.
  No structural change; apply only the carrier-banking rule (empty pockets
  before engaging) — these are already won on kills, losses come from bag-steals.

---

## 6. Per-map strategy — Cluster C (farm & lose — different fix)

Brief — detailed farming fixes are in `GOT_COOKED_FARMING_REPORT.md`; listed
here for completeness with the one-line fix:

| Map | Record | One-line fix |
|---|---|---|
| 01islands | 0/1 | **TP crystal hopper** — 58 vs 1,058; 61% of gems unreachable on foot |
| 02the_pond | 0/2 | Same — 0 vs 519 collected, 47% gap-separated |
| 00ambush, adgato_gemcombat4 | 0/1, 2/4 | Crystal for the 10–17% separated pocket |
| 00expanse | 2/14 | Pure-farm: wider spread, faster items, tribute ≥40; fights don't exist (1.4 opp kills) |
| 00rows | 2/7 | Same — 174k camp dmg already, need route efficiency not fights |
| 02fields / 02geodes / 02tangle / 00quadrants | 1/17 | Big-map spread farming; the 5-pick draft (12/61) is the root — Varg+Tavi travel too slow together |
| 01big_world / 01corridors | 0/5 | Catastrophic (99 vs 1,103 / 74 vs 1,025): champs get lost in the maze — needs BFS distance fields, not fight logic |
| 02gift_wrapping / 00great_wall / 02famine | 0/4 | Out-collected ~2× with few fights — routing + spread, same as expanse |
| 01concentrated_wealth / 01yellow_brick_road | 0/2 | Boss/center-gem maps — need siege pairs + contest timing |
| 00stampede (lost 1) | 3/4 | Already works; the loss was out-camped 196 vs 320 |

---

## 7. Priority order (effort vs measured impact)

1. **Engage-rule + death-stagger breaker** — one shared-memory rule; directly
   targets ~39 cluster-B losses and the 15–30-death maps. Highest impact.
2. **Frontline health items + wounded retreat** — item-weight change only;
   fixes the attrition gap on every fight map and halves camp suicides (dunes).
3. **Carrier-banking discipline** (tribute ≥30, empty pockets on arena maps) —
   stops feeding the enemy bag; converts elk_arena/lost_world losses.
4. **Vendetta back on 3-pick brawl drafts** (anvil/gold_rush/the_line) or
   kill-priority targeting for Marcella — converts their damage lead into kills.
5. **TP crystal hopper** — fixes the 0-win gap-separated maps entirely.
6. **5-pick big-map plan** (lane-splitting + spread farm) — 12/61 is the largest
   single pool of losses, but the hardest fix; do after 1–5.
7. **Willow-for-Tavi on 5-pick fight maps** — experiment after #1; measured
   weakest link vs zero healing coverage.

## 8. Verification criteria

For each change, on ~10+ games vs comparable opponents:

- Team deaths/game must drop (anvil 20→≤10, eight 30→≤12) **without** kills/game
  dropping below ~80% of current (9.1→≥7).
- Win-rate by cluster: B-cluster maps should move from ~30% toward ≥45%; A-cluster
  must not regress below current (guard the vault/split/stampede results).
- Collected-gems gap on cluster C must narrow ≥30% before claiming a routing fix.
- Marcella's kills/game (4.1) is the canary — if engagement rules push it below
  ~3, the rules are too passive.
