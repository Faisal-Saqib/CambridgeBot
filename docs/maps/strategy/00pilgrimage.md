# 00pilgrimage strategy

**Class:** sparse | **Size:** 50x65 | **Picks:** 5 | **Altars:** 4 | **Camp groups:** 23

## Map facts [derived]

- Gems 184 (37/champ → **gem-starved**), gold 1740 (348/champ → **gold-normal**), camp HP per gem 160.
- Gem concentration: top 48%, center 84%, monolith-held 0%, harmless camps 0%.
- Camp density 56.6; brawl flag: False.
- **Unreachable on foot:** 0/184 static gems (0%) sit outside our spawn's walkable component [derived] — reachable only by a dash (if the gap is short) or a teleport crystal.

## What top-20 teams did here [measured]

- Sample: 21 team-games, 11 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (8w); Cassi & Issac, Heart of Ruin, Ren, Vendetta, Vesper Vale (1w); Heart of Ruin, Marcella, Tavi, Varg, Vendetta (1w)
- Champions in winning drafts: Heart of Ruin (11w), Vendetta (11w), Marcella (10w), Vesper Vale (10w), Ryth (8w), Tavi (2w), Cassi & Issac (1w), Ren (1w)
- Winners: kills 9.3, deaths 5.1, tribute 48.3 gems, wards 191, farm spread 21.0 tiles.
- Winner item families: Bruiser×1891, Other×320, Durability×217, Jungle×181, Prospector×167, Capture×116
- Winner consumables: Teleport Crystal×153, Altar Lock×33

## Our record here [measured]

- v22 campaign vs five ~peer teams: 5/5 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Tavi** — low-economy map; carry + efficient clearers, skip Willow [hypothesis].

### Camp targets

- Only 37 gems/champ [derived]. Take high-value camps within ~15 tiles of spawn; skip far low-value trips (travel dominates on sparse maps).
- 84% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Tavi (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 16.9 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Wide spread (one champ per camp cluster, matching the measured winner spread above), regroup on enemy sighting within ~12 tiles.
- Bank at the nearest of 4 altars; tribute when a carrier holds ~48 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*