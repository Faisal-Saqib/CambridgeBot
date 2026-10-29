# 00lost_world strategy

**Class:** rich | **Size:** 35x31 | **Picks:** 5 | **Altars:** 3 | **Camp groups:** 34

## Map facts [derived]

- Gems 592 (118/champ), gold 1440 (288/champ), camp HP per gem 82.
- Gem concentration: top 39%, center 77%, monolith-held 39%, harmless camps 40%.
- Camp density 545.6; brawl flag: False.

## What top-20 teams did here [measured]

- Sample: 29 team-games, 15 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (7w); Heart of Ruin, Marcella, Ryth, Tavi, Vendetta (3w); Heart of Ruin, Marcella, Prism, Ryth, Vesper Vale (1w)
- Champions in winning drafts: Marcella (15w), Heart of Ruin (15w), Vendetta (13w), Vesper Vale (12w), Ryth (12w), Tavi (5w), Prism (1w), Cassi & Issac (1w)
- Winners: kills 15.5, deaths 7.0, tribute 20.5 gems, wards 101, farm spread 5.7 tiles.
- Winner item families: Bruiser×211, Prospector×123, Jungle×103, Durability×96, Treasure×66, Monster×38
- Winner consumables: Altar Lock×35, Teleport Crystal×33

## Our record here [measured]

- v22 campaign vs five ~peer teams: 5/5 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Tavi** — fast clear + one banker [hypothesis].

### Camp targets

- 118 gems/champ across 34 groups [derived]. Spread-farm: each champ claims a camp cluster, top teams' farm spread here was 5.7 tiles.
- 77% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).
- 40% of camps are harmless [derived] — free farming; take them first while the enemy fights dangerous camps.

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Tavi (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 4.5 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Wide spread (one champ per camp cluster, matching the measured winner spread above), regroup on enemy sighting within ~12 tiles.
- Bank at the nearest of 3 altars; tribute when a carrier holds ~20 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*