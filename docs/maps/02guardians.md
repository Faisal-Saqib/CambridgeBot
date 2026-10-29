# 02guardians strategy

**Class:** boss | **Size:** 41x41 | **Picks:** 4 | **Altars:** 1 | **Camp groups:** 22

## Map facts [derived]

- Gems 688 (172/champ), gold 2100 (525/champ), camp HP per gem 117.
- Gem concentration: top 29%, center 66%, monolith-held 58%, harmless camps 4%.
- Camp density 409.3; brawl flag: False.

## What top-20 teams did here [measured]

- Sample: 17 team-games, 9 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vesper Vale (3w); Marcella, Ryth, Vendetta, Vesper Vale (2w); Heart of Ruin, Marcella, Vendetta, Vesper Vale (2w)
- Champions in winning drafts: Marcella (9w), Vesper Vale (7w), Ryth (7w), Vendetta (6w), Heart of Ruin (5w), Tavi (2w)
- Winners: kills 17.4, deaths 8.2, tribute 246.2 gems, wards 203, farm spread 22.5 tiles.
- Winner item families: Bruiser×803, Other×126, Jungle×96, Durability×92, Prospector×79, Treasure×56
- Winner consumables: Altar Lock×27, Teleport Crystal×12

## Our record here [measured]

- v22 campaign vs five ~peer teams: 1/5 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella** — sustain clear comp for long monolith sieges [hypothesis].

### Camp targets

- Monoliths hold 58% of gems [derived]. Prioritize the nearest monolith camps; use sustained chipping (camps keep damage between visits) + death-blacklist so a killed champ does not immediately re-die to the same camp.
- Do NOT hold gems for a group gate assault vs real teams — bank through open altars early; break gate camps around round 400-700 like top teams, not 900+ [measured].
- 66% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 4.3 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Two loose pairs beat one ball here: one pair sieges monoliths, one pair farms side camps + banks. Regroup within ~12 tiles when enemies appear.
- Bank at the nearest of 1 altars; tribute when a carrier holds ~246 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*