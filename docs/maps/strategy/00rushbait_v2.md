# 00rushbait_v2 strategy

**Class:** normal | **Size:** 30x80 | **Picks:** 4 | **Altars:** 2 | **Camp groups:** 18

## Map facts [derived]

- Gems 258 (64/champ → **gem-normal**), gold 1360 (340/champ → **gold-normal**), camp HP per gem 139.
- Gem concentration: top 11%, center 100%, monolith-held 0%, harmless camps 0%.
- Camp density 107.5; brawl flag: False.
- **Unreachable on foot:** 0/258 static gems (0%) sit outside our spawn's walkable component [derived] — reachable only by a dash (if the gap is short) or a teleport crystal.

## What top-20 teams did here [measured]

- Sample: 20 team-games, 11 wins.
- Winning drafts: Heart of Ruin, Marcella, Vendetta, Vesper Vale (3w); Marcella, Prism, Ryth, Vesper Vale (2w); Heart of Ruin, Marcella, Tavi, Vendetta (1w)
- Champions in winning drafts: Marcella (10w), Vesper Vale (8w), Heart of Ruin (8w), Vendetta (6w), Ryth (5w), Prism (2w), Tavi (2w), Stellar (1w)
- Winners: kills 9.0, deaths 3.4, tribute 55.0 gems, wards 86, farm spread 35.2 tiles.
- Winner item families: Bruiser×674, Jungle×120, Durability×117, Prospector×96, Other×91, Treasure×79
- Winner consumables: Altar Lock×69, Teleport Crystal×68

## Our record here [measured]

- v22 campaign vs five ~peer teams: 3/4 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella** — fast clear + one banker [hypothesis].

### Camp targets

- 64 gems/champ across 18 groups [derived]. Spread-farm: each champ claims a camp cluster, top teams' farm spread here was 35.2 tiles.
- 100% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 12.5 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Wide spread (one champ per camp cluster, matching the measured winner spread above), regroup on enemy sighting within ~12 tiles.
- Bank at the nearest of 2 altars; tribute when a carrier holds ~55 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*