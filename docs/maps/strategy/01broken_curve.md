# 01broken_curve strategy

**Class:** boss | **Size:** 40x40 | **Picks:** 3 | **Altars:** 4 | **Camp groups:** 22

## Map facts [derived]

- Gems 746 (249/champ → **gem-abundant**), gold 2520 (840/champ → **gold-rich**), camp HP per gem 117.
- Gem concentration: top 27%, center 54%, monolith-held 54%, harmless camps 4%.
- Camp density 466.2; brawl flag: False.
- **Unreachable on foot:** 0/746 static gems (0%) sit outside our spawn's walkable component [derived] — reachable only by a dash (if the gap is short) or a teleport crystal.

## What top-20 teams did here [measured]

- Sample: 28 team-games, 14 wins.
- Winning drafts: Heart of Ruin, Vendetta, Vesper Vale (7w); Heart of Ruin, Marcella, Vendetta (2w); Marcella, Tavi, Vendetta (2w)
- Champions in winning drafts: Vendetta (12w), Heart of Ruin (11w), Vesper Vale (9w), Marcella (5w), Ryth (2w), Tavi (2w), Prism (1w)
- Winners: kills 1.7, deaths 1.4, tribute 39.8 gems, wards 113, farm spread 8.5 tiles.
- Winner item families: Bruiser×989, Jungle×126, Durability×124, Prospector×100, Other×81, Capture×80
- Winner consumables: Altar Lock×33, Teleport Crystal×17

## Our record here [measured]

- No recorded online results for our bots on this map.

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin** — sustain clear comp for long monolith sieges [hypothesis].

### Camp targets

- Monoliths hold 54% of gems [derived]. Prioritize the nearest monolith camps; use sustained chipping (camps keep damage between visits) + death-blacklist so a killed champ does not immediately re-die to the same camp.
- Do NOT hold gems for a group gate assault vs real teams — bank through open altars early; break gate camps around round 400-700 like top teams, not 900+ [measured].
- 54% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 3.6 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Two loose pairs beat one ball here: one pair sieges monoliths, one pair farms side camps + banks. Regroup within ~12 tiles when enemies appear.
- Bank at the nearest of 4 altars; tribute when a carrier holds ~40 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*