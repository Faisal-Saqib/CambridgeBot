# 02geodes strategy

**Class:** normal | **Size:** 89x71 | **Picks:** 5 | **Altars:** 5 | **Camp groups:** 14

## Map facts [derived]

- Gems 402 (80/champ → **gem-normal**), gold 1060 (212/champ → **gold-poor**), camp HP per gem 84.
- Gem concentration: top 23%, center 46%, monolith-held 0%, harmless camps 3%.
- Camp density 63.6; brawl flag: False.
- **Unreachable on foot:** 0/402 static gems (0%) sit outside our spawn's walkable component [derived] — reachable only by a dash (if the gap is short) or a teleport crystal.

## What top-20 teams did here [measured]

- Sample: 28 team-games, 14 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (4w); Heart of Ruin, Marcella, Tavi, Vendetta, Vesper Vale (3w); Heart of Ruin, Marcella, Vendetta, Vesper Vale, Willow (2w)
- Champions in winning drafts: Heart of Ruin (13w), Vendetta (13w), Marcella (13w), Vesper Vale (11w), Ryth (6w), Tavi (5w), Willow (3w), Varg (3w)
- Winners: kills 1.6, deaths 2.1, tribute 51.9 gems, wards 118, farm spread 20.8 tiles.
- Winner item families: Bruiser×246, Jungle×187, Prospector×113, Capture×97, Monster×87, Durability×81
- Winner consumables: Altar Lock×63, Teleport Crystal×43

## Our record here [measured]

- No recorded online results for our bots on this map.

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Tavi** — fast clear + one banker [hypothesis].

### Camp targets

- 80 gems/champ across 14 groups [derived]. Spread-farm: each champ claims a camp cluster, top teams' farm spread here was 20.8 tiles.
- 46% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Tavi (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 7.6 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Wide spread (one champ per camp cluster, matching the measured winner spread above), regroup on enemy sighting within ~12 tiles.
- Bank at the nearest of 5 altars; tribute when a carrier holds ~52 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*