# 00vault strategy

**Class:** jackpot | **Size:** 31x31 | **Picks:** 4 | **Altars:** 2 | **Camp groups:** 7

## Map facts [derived]

- Gems 359 (90/champ), gold 400 (100/champ), camp HP per gem 35.
- Gem concentration: top 96%, center 96%, monolith-held 0%, harmless camps 96%.
- Camp density 373.6; brawl flag: True.

## What top-20 teams did here [measured]

- Sample: 33 team-games, 18 wins.
- Winning drafts: Heart of Ruin, Marcella, Vendetta, Vesper Vale (5w); Heart of Ruin, Marcella, Prism, Ryth (4w); Heart of Ruin, Marcella, Ryth, Vesper Vale (3w)
- Champions in winning drafts: Marcella (17w), Heart of Ruin (16w), Ryth (12w), Vendetta (10w), Vesper Vale (10w), Prism (5w), Tavi (2w)
- Winners: kills 7.1, deaths 2.8, tribute 167.7 gems, wards 47, farm spread n/a tiles.
- Winner item families: Bruiser×159, Other×66, Jungle×66, Prospector×60, Treasure×57, Durability×48
- Winner consumables: Altar Lock×30, Teleport Crystal×24

## Our record here [measured]

- v22 campaign vs five ~peer teams: 3/4 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella** — melee-heavy deathball for the contested objective [hypothesis]. Ryth's AoE stun + bodies for trades; drop Willow/Tavi.

### Camp targets

- One group holds ~96% of the map's 359 gems [derived]. That group IS the map: send the whole team at round 0, clear it together, escort the carrier to the altar. Conceding it = conceding the game (our the_line record: 0 points in 25 straight games [measured]).
- After the jackpot, farm outward in a cluster — do not spread solo while enemies are alive [hypothesis].
- 96% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).
- 96% of gems sit in one top region [derived] — treat it as the jackpot objective even if the map is otherwise spread out.
- 96% of camps are harmless [derived] — free farming; take them first while the enemy fights dangerous camps.

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Buy a **Tribute** emblem for the designated carrier — bigger banked hauls decide jackpot maps [hypothesis].
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 3.0 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Move as one group; nobody farms alone beyond ~6 tiles from the nearest ally. Escort carriers to the altar; fight only with 3+ bodies present.
- Bank at the nearest of 2 altars; tribute when a carrier holds ~168 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*