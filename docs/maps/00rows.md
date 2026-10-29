# 00rows strategy

**Class:** jackpot | **Size:** 50x50 | **Picks:** 4 | **Altars:** 2 | **Camp groups:** 9

## Map facts [derived]

- Gems 584 (146/champ), gold 1680 (420/champ), camp HP per gem 117.
- Gem concentration: top 80%, center 80%, monolith-held 80%, harmless camps 0%.
- Camp density 233.6; brawl flag: False.

## What top-20 teams did here [measured]

- Sample: 26 team-games, 12 wins.
- Winning drafts: Marcella, Ryth, Vendetta, Vesper Vale (3w); Heart of Ruin, Marcella, Tavi, Vendetta (2w); Heart of Ruin, Tavi, Vendetta, Vesper Vale (2w)
- Champions in winning drafts: Vendetta (12w), Vesper Vale (9w), Heart of Ruin (8w), Marcella (7w), Tavi (4w), Ryth (4w), Prism (2w), Cassi & Issac (1w)
- Winners: kills 0.5, deaths 0.7, tribute 58.9 gems, wards 147, farm spread 14.0 tiles.
- Winner item families: Bruiser×1241, Jungle×147, Durability×131, Other×120, Monster×118, Capture×97
- Winner consumables: Teleport Crystal×40, Altar Lock×36

## Our record here [measured]

- v22 campaign vs five ~peer teams: 1/4 wins (results/b*.json).

## Recommended plan

### Draft

- Primary: copy the most-frequent winning draft here — **Marcella, Ryth, Vendetta, Vesper Vale** [measured].
- Fallback: **Vesper Vale, Vendetta, Heart of Ruin, Marcella** — melee-heavy deathball for the contested objective [hypothesis]. Ryth's AoE stun + bodies for trades; drop Willow/Tavi.

### Camp targets

- One group holds ~80% of the map's 584 gems [derived]. That group IS the map: send the whole team at round 0, clear it together, escort the carrier to the altar. Conceding it = conceding the game (our the_line record: 0 points in 25 straight games [measured]).
- After the jackpot, farm outward in a cluster — do not spread solo while enemies are alive [hypothesis].
- 80% of gems are in the center [derived] — contest it early; this is the 'central gems' failure we observed (our bot walked past center gems to side camps).
- 80% of gems sit in one top region [derived] — treat it as the jackpot objective even if the map is otherwise spread out.

### Items / shards / emblems

- Opening (everyone): Monster + Jungle Health for early clear and sustain — matches every top-20 opening [measured].
- Vesper Vale (carry): Bruiser Strength shards/emblems as main stack; add Power Strength once Bruiser caps.
- Vendetta (support): Bruiser Strength shards/emblems as main stack; Durability Health for tankiness.
- Heart of Ruin (support): Bruiser Focus shards/emblems as main stack; Durability Health for tankiness.
- Marcella (carry): Bruiser Focus shards/emblems as main stack; add Power Focus once Bruiser caps.
- Buy a **Tribute** emblem for the designated carrier — bigger banked hauls decide jackpot maps [hypothesis].
- Consumables: Altar Lock on the altar nearest our farm (top teams averaged 6.3 consumables/game here); TP crystal(s) for carrier escapes.

### Traversal / positioning

- Move as one group; nobody farms alone beyond ~6 tiles from the nearest ally. Escort carriers to the altar; fight only with 3+ bodies present.
- Bank at the nearest of 2 altars; tribute when a carrier holds ~59 gems or when an enemy is chasing — losing carried gems is the main way games here are lost.

---
*Unvalidated plan derived from data; test locally before adopting.*