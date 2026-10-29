# 02treasure_box strategy

**Class:** rich | **Size:** 35x35 | **Picks:** 5 | **Altars:** 1 | **Camp groups:** 34

## Map facts [derived]

- Gems 449 (90/champ → **gem-normal**), gold 3070 (614/champ → **gold-rich**), camp HP per gem 156.
- Gem concentration: top 14%, center 47%, monolith-held 0%, harmless camps 25%.
- Camp density 366.5; brawl flag: False.
- **Unreachable on foot:** 0/449 static gems (0%) sit outside our spawn's walkable component [derived] — reachable only by a dash (if the gap is short) or a teleport crystal.

## What top-20 teams did here [measured]

- Sample: 18 team-games, 9 wins.
- Winning drafts: Heart of Ruin, Marcella, Vendetta, Vesper Vale, Willow (4w); Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (2w); Heart of Ruin, Marcella, Tavi, Vendetta, Vesper Vale (2w)
- Champions in winning drafts: Vesper Vale (9w), Heart of Ruin (9w), Marcella (9w), Vendetta (8w), Willow (4w), Ryth (3w), Tavi (3w)
- Winners: kills 10.8, deaths 4.7, tribute 38.9 gems, wards 36, farm spread 5.8 tiles.
- Winner item families: Bruiser×1211, Other×136, Jungle×125, Durability×118, Prospector×116, Treasure×79
- Winner consumables: Teleport Crystal×43, Altar Lock×18

## Our record here [measured]

- v22 campaign vs five ~peer teams: 3/5 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Vendetta, Vesper Vale, Willow** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Tavi** — fast clear + one banker [hypothesis].

### Camp targets

- 90 gems/champ across 34 groups [derived]. Spread-farm: each champ claims a camp cluster, top teams' farm spread here was 5.8 tiles.
- 47% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Tavi (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 6.8 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Wide spread (one champ per camp cluster, matching the measured winner spread above), regroup on enemy sighting within ~12 tiles.
- Bank at the nearest of 1 altars; tribute when a carrier holds ~39 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*