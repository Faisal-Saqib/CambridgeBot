# titan (user's Rust bot), submitted as v19

`bots/titan`. Kept unchanged as the reference opponent.

## Strategy
- Draft by team size: 3–4 picks Vesper, Marcella, Ryth (Tavi); 5 picks Willow, Vesper, Ryth, Tavi, Marcella.
- Shared memory: bytes 0–5 hold each champion's claimed camp group, byte 6 the team's focus target, byte 7 the monolith-gate assault flag.
- Job score = value / (travel + respawn wait + clear time + HP cost priced as trips home) / claimants. Dangerous camps attract helpers; harmless clusters spread the team out. Stays off the enemy side early; avoids places where enemies were seen or we died.
- One champion captures each group; Marcella is preferred within 8 tiles. Steps off spawn tiles so groups can respawn.
- Banks at 40–60 gems (Marcella or "careful" mode: 20) and cancels a tribute if it would die first.
- Fights decided by comparing how fast each side can kill the other; joins teammates' fights; ranged champions hold position for a clean shot.
- Retreats on low HP, recalls when out of reach, heals at spawn. Shopping trips when gold piles up.
- Build: Monster/Jungle/Durability opening, then Bruiser forever. No consumables, no wards.
- Static distance fields copied into wasm memory (cheap fuel); dashes along them.

## Strong points
- Beat our C++ main 24–0. Online 29–1 against teams ranked 430–530.
- Efficient farming: usually reaches 1000 gems by round 700–1700.

## Weak points
- the_line: lost every time online. One champion captures the whole 161-gem row and walks to the single altar alone.
- 3-pick maps against aggressive Vesper/Vendetta/Marcella or Heart of Ruin teams: 20–25 deaths, no kills.
- Big gem hauls before banking; no wards; no altar locks or crystals; fuel stalls on some maps.
- Lost 1–4 twice to Ascendance (rank ~290).
