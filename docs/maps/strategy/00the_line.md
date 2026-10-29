# 00the_line strategy

**Class:** jackpot | **Size:** 33x33 | **Picks:** 4 | **Altars:** 1 | **Camp groups:** 9

## Map facts [derived]

- Gems 193 (48/champ), gold 480 (120/champ), camp HP per gem 75.
- Gem concentration: top 83%, center 83%, monolith-held 0%, harmless camps 83%.
- Camp density 177.2; brawl flag: True.

## What top-20 teams did here [measured]

- Sample: 25 team-games, 12 wins.
- Winning drafts: Cassi & Issac, Heart of Ruin, Vendetta, Vesper Vale (3w); Marcella, Ryth, Vendetta, Vesper Vale (2w); Heart of Ruin, Ryth, Vendetta, Vesper Vale (1w)
- Champions in winning drafts: Heart of Ruin (9w), Vesper Vale (8w), Vendetta (8w), Marcella (8w), Ryth (6w), Cassi & Issac (4w), Prism (2w), Tavi (1w)
- Winners: kills 14.0, deaths 6.2, tribute 66.1 gems, wards 155, farm spread 27.9 tiles.
- Winner item families: Bruiser×548, Jungle×143, Durability×104, Prospector×91, Capture×71, Monster×65
- Winner consumables: Altar Lock×46, Teleport Crystal×25

## Our record here [measured]

- v22 campaign vs five ~peer teams: 1/5 wins (results/b*.json).
- Chamero vs top-5: 0/25 wins (avg 0-1040).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Cassi & Issac, Heart of Ruin, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella** — melee-heavy deathball for the contested objective [hypothesis]. Ryth's AoE stun + bodies for trades; drop Willow/Tavi.

### Camp targets

- One group holds ~83% of the map's 193 gems [derived]. That group IS the map: send the whole team at round 0, clear it together, escort the carrier to the altar. Conceding it = conceding the game (our the_line record: 0 points in 25 straight games [measured]).
- After the jackpot, farm outward in a cluster — do not spread solo while enemies are alive [hypothesis].
- 83% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).
- 83% of gems sit in one top region [derived] — treat it as the jackpot objective even if the map is otherwise spread out.
- 83% of camps are harmless [derived] — free farming; take them first while the enemy fights dangerous camps.

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Buy a **Tribute** emblem for the designated carrier — bigger banked hauls decide jackpot maps [hypothesis].
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 5.9 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Move as one group; nobody farms alone beyond ~6 tiles from the nearest ally. Escort carriers to the altar; fight only with 3+ bodies present.
- Bank at the nearest of 1 altars; tribute when a carrier holds ~66 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*