# 00quarry strategy

**Class:** sparse | **Size:** 35x29 | **Picks:** 4 | **Altars:** 2 | **Camp groups:** 14

## Map facts [derived]

- Gems 114 (28/champ), gold 520 (130/champ), camp HP per gem 81.
- Gem concentration: top 40%, center 68%, monolith-held 0%, harmless camps 25%.
- Camp density 112.3; brawl flag: False.

## What top-20 teams did here [measured]

- Sample: 38 team-games, 19 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vesper Vale (3w); Heart of Ruin, Marcella, Vendetta, Vesper Vale (3w); Heart of Ruin, Ryth, Vendetta, Vesper Vale (3w)
- Champions in winning drafts: Heart of Ruin (15w), Marcella (14w), Vesper Vale (14w), Vendetta (13w), Ryth (9w), Willow (3w), Tavi (3w), Cassi & Issac (2w)
- Winners: kills 15.7, deaths 5.7, tribute 36.3 gems, wards 133, farm spread 11.9 tiles.
- Winner item families: Bruiser×1040, Other×211, Durability×201, Jungle×191, Treasure×164, Prospector×128
- Winner consumables: Altar Lock×88, Teleport Crystal×72

## Our record here [measured]

- v22 campaign vs five ~peer teams: 1/5 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella** — low-economy map; carry + efficient clearers, skip Willow [hypothesis].

### Camp targets

- Only 28 gems/champ [derived]. Take high-value camps within ~15 tiles of spawn; skip far low-value trips (travel dominates on sparse maps).
- 68% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 8.4 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Wide spread (one champ per camp cluster, matching the measured winner spread above), regroup on enemy sighting within ~12 tiles.
- Bank at the nearest of 2 altars; tribute when a carrier holds ~36 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*