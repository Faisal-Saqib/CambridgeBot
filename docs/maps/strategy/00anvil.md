# 00anvil strategy

**Class:** jackpot | **Size:** 37x31 | **Picks:** 3 | **Altars:** 1 | **Camp groups:** 13

## Map facts [derived]

- Gems 258 (86/champ → **gem-normal**), gold 740 (247/champ → **gold-poor**), camp HP per gem 108.
- Gem concentration: top 78%, center 78%, monolith-held 78%, harmless camps 16%.
- Camp density 224.9; brawl flag: False.
- **Unreachable on foot:** 0/258 static gems (0%) sit outside our spawn's walkable component [derived] — reachable only by a dash (if the gap is short) or a teleport crystal.

## What top-20 teams did here [measured]

- Sample: 14 team-games, 7 wins.
- Winning drafts: Heart of Ruin, Marcella, Vesper Vale (3w); Heart of Ruin, Ryth, Vesper Vale (2w); Heart of Ruin, Marcella, Vendetta (1w)
- Champions in winning drafts: Heart of Ruin (7w), Vesper Vale (6w), Marcella (4w), Ryth (2w), Vendetta (2w)
- Winners: kills 13.0, deaths 3.0, tribute 33.8 gems, wards 114, farm spread 15.4 tiles.
- Winner item families: Bruiser×571, Jungle×77, Durability×63, Other×50, Prospector×48, Capture×24
- Winner consumables: Altar Lock×29

## Our record here [measured]

- v22 campaign vs five ~peer teams: 1/5 wins (results/b*.json).
- Chamero vs top-5: 0/2 wins (avg 52-1098).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Heart of Ruin, Marcella, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin** — melee-heavy deathball for the contested objective [hypothesis]. Ryth's AoE stun + bodies for trades; drop Willow/Tavi.

### Camp targets

- One group holds ~78% of the map's 258 gems [derived]. That group IS the map: send the whole team at round 0, clear it together, escort the carrier to the altar. Conceding it = conceding the game (our the_line record: 0 points in 25 straight games [measured]).
- After the jackpot, farm outward in a cluster — do not spread solo while enemies are alive [hypothesis].
- 78% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).
- 78% of gems sit in one top region [derived] — treat it as the jackpot objective even if the map is otherwise spread out.
- **Gated altar warning**: 78% of gems are monolith-held and only 1 altar(s) exist [derived]. Do NOT hold gems waiting for a group gate assault — bank through open altars early; if all altars are gated, break the gate around round 400-700 like top teams (not 900+), then tribute 200+ at once [measured].

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Buy a **Tribute** emblem for the designated carrier — bigger banked hauls decide jackpot maps [hypothesis].
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 4.1 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Move as one group; nobody farms alone beyond ~6 tiles from the nearest ally. Escort carriers to the altar; fight only with 3+ bodies present.
- Bank at the nearest of 1 altars; tribute when a carrier holds ~34 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*