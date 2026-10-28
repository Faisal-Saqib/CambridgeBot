# main (C++), submitted as v1–v18

Our first bot line, in `bots/main` (C++). Retired in favour of titan/apex.

## Strategy
- Solo "sector" farming: each champion takes camp groups in its own sector (planned in draft memory).
- Group score = value / walking distance / expected lives lost. Monolith-class groups only get a "scarcity raid" when one group holds >60% of the remaining gems.
- Tribute at 1 gem (later 5). Recall-and-shop trips when gold piles up. Tavi shops in the field.
- PvP: flee when outnumbered, hurt or carrying; fight back when hit and not outnumbered (carrying ≤ 3 gems). Under-fire detection includes ability poke.
- Teleport crystals: island hopping across holes (01islands 265 → 1013 gems vs starter) and escapes.
- Death blacklist: avoid a group for 80 rounds after a camp killed us there (stopped respawn-and-die loops at monoliths).
- Final draft: Vendetta, Vesper, Cassi & Issac, Varg, Marcella (Ryth/Tavi/Willow as fillers).

## Strong points
- Beats starter-cpp on every local map (ambush ~750–795 vs 477, monolith 1000+, stampede 480–640, islands 1013).
- Only bot we have that crosses holes with teleport crystals.
- Crash-free, guarded API calls.

## Weak points
- Loses fights badly against real teams: 10–25 deaths a game, few kills.
- Farms alone, so it is easy to pick off. Captures and banks alone.
- Fuel-hungry on big maps (suspended turns).
- Lost 0–24 to titan (12 maps, both sides).

## Results
- Online against teams ranked ~500–540: roughly 30–40% wins at best (v13–v18).
- Against teams ranked ≤ 25: almost always lost.
