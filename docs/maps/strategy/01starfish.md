# 01starfish strategy

**Class:** normal | **Size:** 50x50 | **Picks:** 5 | **Altars:** 2 | **Camp groups:** 16

## Map facts [derived]

- Gems 334 (67/champ), gold 1860 (372/champ), camp HP per gem 155.
- Gem concentration: top 35%, center 46%, monolith-held 0%, harmless camps 0%.
- Camp density 133.6; brawl flag: False.

## What top-20 teams did here [measured]

- Sample: 26 team-games, 13 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (5w); Marcella, Ryth, Tavi, Vendetta, Vesper Vale (3w); Heart of Ruin, Marcella, Vendetta, Vesper Vale, Willow (2w)
- Champions in winning drafts: Vendetta (13w), Marcella (13w), Vesper Vale (11w), Heart of Ruin (10w), Ryth (10w), Tavi (4w), Willow (3w), Prism (1w)
- Winners: kills 18.7, deaths 14.2, tribute 46.9 gems, wards 299, farm spread 12.8 tiles.
- Winner item families: Bruiser×1553, Other×227, Durability×176, Jungle×148, Prospector×139, Treasure×103
- Winner consumables: Altar Lock×59, Teleport Crystal×10

## Our record here [measured]

- v22 campaign vs five ~peer teams: 2/5 wins (results/b*.json).
- Chamero vs top-5: 0/2 wins (avg 63-1026).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Tavi** — fast clear + one banker [hypothesis].

### Camp targets

- 67 gems/champ across 16 groups [derived]. Spread-farm: each champ claims a camp cluster, top teams' farm spread here was 12.8 tiles.
- 46% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Tavi (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 5.3 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Wide spread (one champ per camp cluster, matching the measured winner spread above), regroup on enemy sighting within ~12 tiles.
- Bank at the nearest of 2 altars; tribute when a carrier holds ~47 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*