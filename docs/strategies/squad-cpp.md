# squad (C++ experiment, never submitted)

`bots/squad`, built on main's engine with three switches turned on: `rally`, `beacon` and `ranged_standoff`.

## Strategy
- Two-tier farming. Cheap camps solo; camps a lone champion can't clear without dying are farmed by a squad.
- Rally via the 8-byte shared memory. v1: one team-wide rally slot. v2: tank leader + damage follower pairs (two squads).
- Squad members wait at a staging ring just outside the camp's aggro until a partner stands with them, then engage.
- Beacon: share the latest enemy sighting so carriers route around it and nearby champions answer distress calls.
- Ranged champions fight camps from max range so the melee in front draws the hits.

## Strong points
- Deaths roughly halved against starter-cpp (22–26 vs 42–60).

## Weak points
- Champions spent about 30% of the match waiting for partners who often never came (53 of 88 calls abandoned).
- Fewer gems: 381–493 vs starter-cpp's 477, and 474 vs main's 651.

## Status
Shelved once titan turned out far stronger. The pairing idea carries over to apex v22 (`docs/PLAN.md`, P3), this time with partners that stay together instead of meeting up.
