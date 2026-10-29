# 01elk_arena strategy

**Class:** jackpot | **Size:** 50x50 | **Picks:** 5 | **Altars:** 2 | **Camp groups:** 29

## Map facts [derived]

- Gems 72 (14/champ → **gem-starved**), gold 1260 (252/champ → **gold-normal**), camp HP per gem 167.
- Gem concentration: top 100%, center 100%, monolith-held 0%, harmless camps 0%.
- Camp density 28.8; brawl flag: False.
- **Unreachable on foot:** 0/72 static gems (0%) sit outside our spawn's walkable component [derived] — reachable only by a dash (if the gap is short) or a teleport crystal.

## What top-20 teams did here [measured]

- Sample: 31 team-games, 15 wins.
- Winning drafts: Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale (6w); Marcella, Ryth, Tavi, Vendetta, Vesper Vale (2w); Cassi & Issac, Heart of Ruin, Marcella, Vendetta, Vesper Vale (2w)
- Champions in winning drafts: Marcella (15w), Vesper Vale (15w), Vendetta (12w), Heart of Ruin (12w), Ryth (10w), Tavi (4w), Cassi & Issac (3w), Prism (2w)
- Winners: kills 29.1, deaths 12.3, tribute 40.2 gems, wards 405, farm spread 16.6 tiles.
- Winner item families: Bruiser×2276, Other×543, Durability×221, Jungle×190, Prospector×149, Treasure×134
- Winner consumables: Altar Lock×69, Teleport Crystal×38

## Our record here [measured]

- No recorded online results for our bots on this map.

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella, Ryth** — melee-heavy deathball for the contested objective [hypothesis]. Ryth's AoE stun + bodies for trades; drop Willow/Tavi.

### Camp targets

- One group holds ~100% of the map's 72 gems [derived]. That group IS the map: send the whole team at round 0, clear it together, escort the carrier to the altar. Conceding it = conceding the game (our the_line record: 0 points in 25 straight games [measured]).
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
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 7.1 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Move as one group; nobody farms alone beyond ~6 tiles from the nearest ally. Escort carriers to the altar; fight only with 3+ bodies present.
- Bank at the nearest of 2 altars; tribute when a carrier holds ~40 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*