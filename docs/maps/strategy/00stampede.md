# 00stampede strategy

**Class:** jackpot | **Size:** 60x50 | **Picks:** 5 | **Altars:** 2 | **Camp groups:** 13

## Map facts [derived]

- Gems 160 (32/champ), gold 1180 (236/champ), camp HP per gem 122.
- Gem concentration: top 100%, center 100%, monolith-held 0%, harmless camps 0%.
- Camp density 53.3; brawl flag: False.

## What top-20 teams did here [measured]

- Sample: 24 team-games, 11 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (3w); Heart of Ruin, Marcella, Tavi, Vendetta, Vesper Vale (2w); Heart of Ruin, Marcella, Ryth, Varg, Vesper Vale (2w)
- Champions in winning drafts: Heart of Ruin (11w), Vesper Vale (11w), Marcella (11w), Vendetta (7w), Ryth (5w), Willow (3w), Tavi (2w), Varg (2w)
- Winners: kills 16.9, deaths 9.5, tribute 120.3 gems, wards 282, farm spread 29.9 tiles.
- Winner item families: Bruiser×2099, Other×519, Durability×190, Jungle×131, Prospector×122, Capture×97
- Winner consumables: Altar Lock×27, Teleport Crystal×5

## Our record here [measured]

- v22 campaign vs five ~peer teams: 1/5 wins (results/b*.json).
- Chamero vs top-5: 0/2 wins (avg 0-1120).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Ryth** — melee-heavy deathball for the contested objective [hypothesis]. Ryth's AoE stun + bodies for trades; drop Willow/Tavi.

### Camp targets

- One group holds ~100% of the map's 160 gems [derived]. That group IS the map: send the whole team at round 0, clear it together, escort the carrier to the altar. Conceding it = conceding the game (our the_line record: 0 points in 25 straight games [measured]).
- After the jackpot, farm outward in a cluster — do not spread solo while enemies are alive [hypothesis].
- 100% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).
- 100% of gems sit in one top region [derived] — treat it as the jackpot objective even if the map is otherwise spread out.

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Ryth (support): Bruiser Health shards/emblems as main stack; Durability Health for tankiness.
- Buy a **Tribute** emblem for the designated carrier — bigger banked hauls decide jackpot maps [hypothesis].
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 2.9 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Move as one group; nobody farms alone beyond ~6 tiles from the nearest ally. Escort carriers to the altar; fight only with 3+ bodies present.
- Bank at the nearest of 2 altars; tribute when a carrier holds ~120 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*