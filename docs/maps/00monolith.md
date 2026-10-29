# 00monolith strategy

**Class:** boss | **Size:** 50x50 | **Picks:** 5 | **Altars:** 6 | **Camp groups:** 20

## Map facts [derived]

- Gems 670 (134/champ), gold 1940 (388/champ), camp HP per gem 111.
- Gem concentration: top 38%, center 76%, monolith-held 76%, harmless camps 0%.
- Camp density 268.0; brawl flag: False.

## What top-20 teams did here [measured]

- Sample: 41 team-games, 21 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (5w); Heart of Ruin, Marcella, Ryth, Varg, Vesper Vale (3w); Marcella, Ryth, Varg, Vendetta, Vesper Vale (2w)
- Champions in winning drafts: Marcella (21w), Vesper Vale (20w), Heart of Ruin (17w), Vendetta (16w), Ryth (14w), Varg (5w), Tavi (4w), Willow (4w)
- Winners: kills 6.2, deaths 4.4, tribute 40.8 gems, wards 58, farm spread 20.6 tiles.
- Winner item families: Bruiser×1601, Jungle×322, Durability×269, Prospector×215, Other×202, Monster×175
- Winner consumables: Altar Lock×164, Teleport Crystal×21

## Our record here [measured]

- v22 campaign vs five ~peer teams: 4/5 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Ryth** — sustain clear comp for long monolith sieges [hypothesis].

### Camp targets

- Monoliths hold 76% of gems [derived]. Prioritize the nearest monolith camps; use sustained chipping (camps keep damage between visits) + death-blacklist so a killed champ does not immediately re-die to the same camp.
- Do NOT hold gems for a group gate assault vs real teams — bank through open altars early; break gate camps around round 400-700 like top teams, not 900+ [measured].
- 76% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Ryth (support): Bruiser Health shards/emblems as main stack; Durability Health for tankiness.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 8.8 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Two loose pairs beat one ball here: one pair sieges monoliths, one pair farms side camps + banks. Regroup within ~12 tiles when enemies appear.
- Bank at the nearest of 6 altars; tribute when a carrier holds ~41 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*