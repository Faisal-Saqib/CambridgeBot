# 02famine strategy

**Class:** jackpot | **Size:** 91x75 | **Picks:** 5 | **Altars:** 4 | **Camp groups:** 11

## Map facts [derived]

- Gems 380 (76/champ), gold 1160 (232/champ), camp HP per gem 106.
- Gem concentration: top 53%, center 53%, monolith-held 53%, harmless camps 4%.
- Camp density 55.7; brawl flag: False.

## What top-20 teams did here [measured]

- Sample: 19 team-games, 10 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (7w); Heart of Ruin, Marcella, Vendetta, Vesper Vale, Willow (1w); Heart of Ruin, Marcella, Ren, Ryth, Vesper Vale (1w)
- Champions in winning drafts: Vesper Vale (10w), Heart of Ruin (10w), Marcella (10w), Vendetta (9w), Ryth (8w), Willow (1w), Ren (1w), Tavi (1w)
- Winners: kills 5.8, deaths 3.8, tribute 39.0 gems, wards 142, farm spread 35.4 tiles.
- Winner item families: Bruiser×710, Jungle×154, Durability×137, Other×113, Prospector×110, Capture×57
- Winner consumables: Teleport Crystal×69, Altar Lock×41

## Our record here [measured]

- No recorded online results for our bots on this map.

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Ryth** — melee-heavy deathball for the contested objective [hypothesis]. Ryth's AoE stun + bodies for trades; drop Willow/Tavi.

### Camp targets

- One group holds ~53% of the map's 380 gems [derived]. That group IS the map: send the whole team at round 0, clear it together, escort the carrier to the altar. Conceding it = conceding the game (our the_line record: 0 points in 25 straight games [measured]).
- After the jackpot, farm outward in a cluster — do not spread solo while enemies are alive [hypothesis].
- 53% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).
- 53% of gems sit in one top region [derived] — treat it as the jackpot objective even if the map is otherwise spread out.

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Ryth (support): Bruiser Health shards/emblems as main stack; Durability Health for tankiness.
- Buy a **Tribute** emblem for the designated carrier — bigger banked hauls decide jackpot maps [hypothesis].
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 11.0 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Move as one group; nobody farms alone beyond ~6 tiles from the nearest ally. Escort carriers to the altar; fight only with 3+ bodies present.
- Bank at the nearest of 4 altars; tribute when a carrier holds ~39 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*