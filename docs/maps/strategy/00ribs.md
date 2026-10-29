# 00ribs strategy

**Class:** sparse | **Size:** 51x85 | **Picks:** 5 | **Altars:** 2 | **Camp groups:** 13

## Map facts [derived]

- Gems 100 (20/champ → **gem-starved**), gold 380 (76/champ → **gold-poor**), camp HP per gem 72.
- Gem concentration: top 43%, center 100%, monolith-held 0%, harmless camps 14%.
- Camp density 23.1; brawl flag: False.
- **Unreachable on foot:** 0/100 static gems (0%) sit outside our spawn's walkable component [derived] — reachable only by a dash (if the gap is short) or a teleport crystal.

## What top-20 teams did here [measured]

- Sample: 36 team-games, 19 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (5w); Heart of Ruin, Marcella, Tavi, Vendetta, Vesper Vale (4w); Heart of Ruin, Marcella, Vendetta, Vesper Vale, Willow (3w)
- Champions in winning drafts: Heart of Ruin (18w), Marcella (18w), Vesper Vale (18w), Vendetta (16w), Ryth (10w), Tavi (5w), Willow (4w), Prism (2w)
- Winners: kills 25.1, deaths 8.8, tribute 35.8 gems, wards 138, farm spread 24.4 tiles.
- Winner item families: Bruiser×825, Jungle×215, Durability×203, Other×192, Monster×114, Prospector×113
- Winner consumables: Teleport Crystal×98, Altar Lock×64

## Our record here [measured]

- v22 campaign vs five ~peer teams: 3/5 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Tavi** — low-economy map; carry + efficient clearers, skip Willow [hypothesis].

### Camp targets

- Only 20 gems/champ [derived]. Take high-value camps within ~15 tiles of spawn; skip far low-value trips (travel dominates on sparse maps).
- 100% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Tavi (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 8.5 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Wide spread (one champ per camp cluster, matching the measured winner spread above), regroup on enemy sighting within ~12 tiles.
- Bank at the nearest of 2 altars; tribute when a carrier holds ~36 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*