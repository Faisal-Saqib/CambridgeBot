# Combined Top-3 Strategy — the merged "best version"

Synthesis of `docs/TOP3_STRATEGIES.md` (299 ranked games: Mite 66/99,
Intercontinental Fish 62/100, newer team 57/100). Sections marked
[measured] = present in the data; [derived] = combining evidence;
[hypothesis] = proposal to validate.

## The three styles at a glance

| | Mite (66%) | Intercontinental Fish (62%) | newer team (57%) |
|---|---|---|---|
| Signature draft | HoR+Marcella+Tavi+Vendetta+Vesper (66/99) | **C&I**+HoR+Vendetta+Vesper+flex (68/100) | HoR+Marcella+**Prism**+Vesper+**Willow** |
| Edge | Tavi support + ~200 wards + early banking | 2 free bodies + locks 5–8/g + raw damage | Prism poke + Willow heal + Prospector econ |
| Early buys | Jungle Str/Foc | Treasure Str + Bruiser | Prospector HP + Hunter |
| Mid | Bruiser HP spam | Bruiser Str + Jungle | Prospector HP, Durability |
| Late | Bruiser HP + Durability | **Bruiser Str 11–30/g** + Power Foc | Bruiser HP + Capture |
| Wards | **150–290/game** | 60–170 | 60–100 |
| Tributes | 25–45/g, avg 25–40, **first ~r44–65** | 10–38/g, avg 27–105 | 24–30/g, avg 33–48, first ~r70–87 |
| Fight style | support-grouped mid brawls | body-count overwhelm | kite/heal, fewest deaths (1.5) |

## What ALL THREE share — the non-negotiable core

1. **Draft core: Heart of Ruin + Vendetta + Vesper Vale.** Present in every
   top-3 signature. Marcella in 2 of 3 (Fish swaps her for C&I bodies).
   [measured]
2. **Buy SOMETHING before r150** — every winning game opens with cheap shards
   (Jungle/Prospector/Treasure, 30–50 gold). Never save early gold. [measured]
3. **Bank early and often** — first tribute ~r44–87 across all three, not
   end-game dumps. Small tributes only work because they never die carrying —
   the tribute habit must come with carrier protection. [measured]
4. **Ward continuously** — minimum ~60/game, Mite hits 290. Wards on gates,
   altar approaches, and last-seen-enemy lines. [measured]
5. **Frontline = Bruiser Health; carry = Strength.** All three bulk Ryth/HoR
   with HP and stack Str/Foc on the carry. [measured]
6. **Deaths stay low** — winners die 1.5–5/game. Deaths, not camp speed,
   separate them from us. [measured]

## The combined best version [derived]

### Draft (map-dependent)

- **Default 5-pick:** Heart of Ruin + Marcella + Tavi + Vendetta + Vesper
  (Mite's — highest win rate, best balance).
- **Brawl/3-pick maps** (the_line, anvil, stampede, arena): swap Tavi →
  **Cassi & Issac** (Fish's extra bodies dominate small maps; first kill ~r64).
- **Attrition/kite maps** (open farm maps, guardians): swap Tavi → **Willow**
  (newer team's heal = their lowest deaths, 1.5/game).
- **Prism** only if we build real escort logic — newer team makes her work
  (57%) but our v41/v43 data shows she dies 3.3–3.7/game unprotected.
- **Never draft Varg** on fight maps — none of the top 3 use him there; our
  Varg underperforms everywhere (0.1 kills/game).

### Opening (r0–150)

- First 2–3 champs to the nearest safe camp cluster (per `docs/maps/plan/*` —
  winners open within r150 on every map).
- Buy 1–2 **Jungle/Prospector shards** the moment gold allows (~r40–80).
- Ward the nearest altar approach + enemy-spawn direction immediately.
- [Fish] On brawl maps, converge all bodies — first kill median r43–77.

### Mid game (150–500)

- Farm in **spread pairs**, not solo, not deathball — fighters screen
  collectors.
- Buy order: Bruiser HP on frontline first (~5–7 shards), then carry Str/Foc.
- Tribute every ~25–40 gems at the nearest owned altar; **locks ~4–8/game**
  on altar maps (Fish's habit — we buy zero).
- On gap maps, buy 1–2 **TP crystals** and dedicate one hopper (Mite bought
  7/game on gemfight — treats crystals as routine).
- Fight only with body advantage or a confirmed kill; the twins count as two.

### Late game (>500)

- Shift to **Bruiser Str + Power main-stat on the carry** (Fish's late spike —
  they buy 11–30 Bruiser Str late; we currently buy ~6 and zero Power).
- Carrier concentration: one champ holds the big bag, everyone else zones —
  the universal top-team pattern.
- Push score past 1000 by r800–1000; all three finish games ~r900–1200.

### Defense rules (from all three — they barely die)

- Retreat at ~35% HP; never re-enter a lost fight alone (they die 1.5–5/game
  vs our 15–19).
- Carrier drops a tribute before any fight it might join.
- Camp damage is a means, not the goal: newer team wins games with 25–55k camp
  damage by banking what they take — our 60k+ means nothing at 0–1000 scores.

## Adoption order for Chamero

1. Draft core (HoR+Vendetta+Vesper+Marcella+Tavi/C&I-by-map) — already
   partially live; fix the 5th slot by map class.
2. Restore early purchases + locks (regressions vs all three).
3. Early-tribute routine (~r50 onward, 25–40 gems) with carrier protection.
4. Ward habit — currently we buy almost none.
5. Late-game Power/Str item spike on Marcella.
6. Escort/kite rules before any future Prism draft.

Sources: matches/top20-scout summaries · docs/TOP3_STRATEGIES.md ·
docs/TOP20_STRATEGY_CENSUS.md · docs/maps/plan/.
