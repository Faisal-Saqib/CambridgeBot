# apex v20 - titan + jackpot play (historical baseline)

Frozen source: bots/apex20. This is the historical baseline; working bots/apex and the retained live selection are v22. Current cycle evidence is in ../online-cycle-20261027.md.

## Changes from titan
1. **Jackpot team capture** (`Kb::jackpot`). When a group holds ≥ 35% of the map's gems (e.g. the_line's 161 of 193):
   - there is no join cap;
   - every champion within 12 tiles stands on its tiles, so the reward is split instead of one carrier holding it all.
2. **Contested capture**. When an enemy squats on a group we are capturing, go and remove them instead of holding our tile. If they are out of sight, walk along the group toward the tiles we can't see. A timed-out jackpot capture is retried after 5 rounds instead of being dropped for 100.
3. **Brawl-map hunting** (`Kb::brawl_map`). On maps where a harmless jackpot holds ≥ 50% of the gems, the team fights aggressively: takes even fights, joins teammates from further away, chases hurt enemies.

## Results
- the_line, local: 11 of 12 against titan, its salted copies, the aggressive hunter and main (titan scored 5 of 10).
- All 70 maps, both sides: 146 of 280 against titan + titanj1 (52%, average gems 798–761).
- Historical online reports: 64bit 5-0, LOS HOMOS HERMANOS 4-1, Ascendance 1-4. Exact submission attribution was not preserved for every game.

## Strong points
- Improved the_line in the recorded local panel; online improvement on that map is not yet established.
- The broader historical panel was close to even; map-specific regressions remain possible.

## Weak points (inherited from titan)
- Banks big hauls: 2,586 gems lost on death in 10 games against Ascendance.
- Farms alone; no wards; no altar locks or crystals.
- Loses to strong pack-hunting teams.

Historical match attribution was not archived with all summaries. Do not treat the roster as proof of the platform version.
