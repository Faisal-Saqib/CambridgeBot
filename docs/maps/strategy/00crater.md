# 00crater strategy

**Class:** sparse | **Size:** 61x61 | **Picks:** 5 | **Altars:** 1 | **Camp groups:** 6

## Map facts [derived]

- Gems 158 (32/champ → **gem-starved**), gold 450 (90/champ → **gold-poor**), camp HP per gem 92.
- Gem concentration: top 41%, center 63%, monolith-held 0%, harmless camps 0%.
- Camp density 42.5; brawl flag: False.
- **Unreachable on foot:** 0/158 static gems (0%) sit outside our spawn's walkable component [derived] — reachable only by a dash (if the gap is short) or a teleport crystal.

## What top-20 teams did here [measured]

- Sample: 26 team-games, 13 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (6w); Heart of Ruin, Marcella, Vendetta, Vesper Vale, Willow (2w); Heart of Ruin, Marcella, Varg, Vendetta, Vesper Vale (1w)
- Champions in winning drafts: Heart of Ruin (13w), Marcella (13w), Vendetta (11w), Vesper Vale (11w), Ryth (8w), Tavi (3w), Willow (3w), Varg (2w)
- Winners: kills 19.5, deaths 7.2, tribute 47.4 gems, wards 116, farm spread n/a tiles.
- Winner item families: Bruiser×798, Jungle×138, Other×116, Treasure×79, Durability×78, Prospector×60
- Winner consumables: Altar Lock×78, Teleport Crystal×27

## Our record here [measured]

- v22 campaign vs five ~peer teams: 3/5 wins (results/b*.json).
- Chamero vs top-5: 0/23 wins (avg 23-1013).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Tavi** — low-economy map; carry + efficient clearers, skip Willow [hypothesis].

### Camp targets

- Only 32 gems/champ [derived]. Take high-value camps within ~15 tiles of spawn; skip far low-value trips (travel dominates on sparse maps).
- 63% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Tavi (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 8.1 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Wide spread (one champ per camp cluster, matching the measured winner spread above), regroup on enemy sighting within ~12 tiles.
- Bank at the nearest of 1 altars; tribute when a carrier holds ~47 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*