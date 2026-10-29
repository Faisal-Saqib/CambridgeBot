# 01gold_rush strategy

**Class:** jackpot | **Size:** 31x31 | **Picks:** 3 | **Altars:** 4 | **Camp groups:** 15

## Map facts [derived]

- Gems 266 (89/champ → **gem-normal**), gold 1100 (367/champ → **gold-normal**), camp HP per gem 121.
- Gem concentration: top 75%, center 79%, monolith-held 75%, harmless camps 0%.
- Camp density 276.8; brawl flag: False.
- **Unreachable on foot:** 0/266 static gems (0%) sit outside our spawn's walkable component [derived] — reachable only by a dash (if the gap is short) or a teleport crystal.

## What top-20 teams did here [measured]

- Sample: 26 team-games, 12 wins.
- Winning drafts: Heart of Ruin, Vendetta, Vesper Vale (6w); Marcella, Ryth, Vendetta (2w); Heart of Ruin, Marcella, Varg (2w)
- Champions in winning drafts: Heart of Ruin (10w), Vendetta (9w), Vesper Vale (7w), Marcella (5w), Ryth (2w), Varg (2w), Prism (1w)
- Winners: kills 13.2, deaths 2.7, tribute 42.8 gems, wards 177, farm spread 7.4 tiles.
- Winner item families: Bruiser×1420, Other×145, Jungle×99, Durability×99, Treasure×58, Monster×51
- Winner consumables: Teleport Crystal×176, Altar Lock×37

## Our record here [measured]

- No recorded online results for our bots on this map.

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin** — melee-heavy deathball for the contested objective [hypothesis]. Ryth's AoE stun + bodies for trades; drop Willow/Tavi.

### Camp targets

- One group holds ~79% of the map's 266 gems [derived]. That group IS the map: send the whole team at round 0, clear it together, escort the carrier to the altar. Conceding it = conceding the game (our the_line record: 0 points in 25 straight games [measured]).
- After the jackpot, farm outward in a cluster — do not spread solo while enemies are alive [hypothesis].
- 79% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).
- 75% of gems sit in one top region [derived] — treat it as the jackpot objective even if the map is otherwise spread out.

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Buy a **Tribute** emblem for the designated carrier — bigger banked hauls decide jackpot maps [hypothesis].
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 17.8 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Move as one group; nobody farms alone beyond ~6 tiles from the nearest ally. Escort carriers to the altar; fight only with 3+ bodies present.
- Bank at the nearest of 4 altars; tribute when a carrier holds ~43 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*