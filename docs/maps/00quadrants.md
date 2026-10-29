# 00quadrants strategy

**Class:** rich | **Size:** 45x45 | **Picks:** 5 | **Altars:** 4 | **Camp groups:** 21

## Map facts [derived]

- Gems 763 (153/champ), gold 1320 (264/champ), camp HP per gem 67.
- Gem concentration: top 16%, center 47%, monolith-held 0%, harmless camps 5%.
- Camp density 376.8; brawl flag: False.

## What top-20 teams did here [measured]

- Sample: 24 team-games, 14 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (6w); Heart of Ruin, Marcella, Tavi, Vendetta, Vesper Vale (3w); Heart of Ruin, Marcella, Tavi, Varg, Vendetta (2w)
- Champions in winning drafts: Marcella (14w), Heart of Ruin (14w), Vendetta (13w), Vesper Vale (10w), Ryth (8w), Tavi (6w), Varg (2w), Prism (1w)
- Winners: kills 3.1, deaths 2.5, tribute 52.0 gems, wards 44, farm spread 17.3 tiles.
- Winner item families: Jungle×144, Treasure×135, Bruiser×117, Prospector×108, Durability×90, Monster×51
- Winner consumables: Teleport Crystal×128, Altar Lock×58

## Our record here [measured]

- v22 campaign vs five ~peer teams: 5/5 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Tavi** — fast clear + one banker [hypothesis].

### Camp targets

- 153 gems/champ across 21 groups [derived]. Spread-farm: each champ claims a camp cluster, top teams' farm spread here was 17.3 tiles.
- 47% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Tavi (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 13.3 consumables/game here); TP crystal(s) REQUIRED — this map has terrain-separated camps.

### Traversal / positioning

- Wide spread (one champ per camp cluster, matching the measured winner spread above), regroup on enemy sighting within ~12 tiles.
- Bank at the nearest of 4 altars; tribute when a carrier holds ~52 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*