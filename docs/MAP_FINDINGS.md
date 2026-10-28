# Map findings - first completed block

Scope: five maps, five distinct real-team bot snapshots per map, retained v22. This is the first 25 results, including five compatible historical Ascendance games; it is not the completed 70-map campaign. Current coverage is in [MAP_MATRIX.md](MAP_MATRIX.md).

| Map | Wins-losses | Our submitted gems | Our carried gems lost | Our deaths | Deaths to champions/camps | Initial direction |
| --- | --- | --- | --- | --- | --- | --- |
| [00the_line](maps/00the_line.md) | 1-4 | 1272 | 1359 | 95 | 95/0 | Dedicated objective-control and delivery profile |
| [02treasure_box](maps/02treasure_box.md) | 3-2 | 4475 | 1059 | 123 | 122/1 | Close-range combat decisions and fuel investigation |
| [02crossing](maps/02crossing.md) | 2-3 | 3869 | 506 | 92 | 91/1 | Route/fight selection around multiple altars |
| [00expanse](maps/00expanse.md) | 5-0 | 5109 | 44 | 3 | 3/0 | Preserve efficient v22 farming as reference |
| [01starfish](maps/01starfish.md) | 2-3 | 2881 | 2162 | 170 | 145/25 | Carrier protection and encounter selection, with camp safety |

## What the evidence supports

The same bot performs very differently by map. Expanse's five wins, three deaths and 44 lost gems give no reason to replace its farming behavior globally with permanent regrouping. The Line's four losses, 95 champion-caused deaths and 1359 gems lost to champions justify a separate investigation of objective control and delivery. Its dominant 161-gem group is harmless; this is not primarily a problem of surviving damaging camps.

On Treasure Box, champion damage taken totaled approximately 223,829 versus 79,879 camp damage, and there were 618 fuel-exhaustion events. These establish symptoms worth tracing; they do not yet identify a particular expensive code path or prove the timing of the suspensions caused deaths.

Starfish lost 1838 gems to champion kills and 324 to camps. That is a combined carrier/encounter problem; stronger camp clearing alone would not address most recorded losses. Crossing lost 499 gems to champions and 7 to camps.

## Candidate profiles to test after the baseline

- Expanse: keep v22's spread farming and shorter tribute hauls as the reference.
- The Line: test control of the concentrated gem objective and safer delivery to its single altar, including capture position, pursuit decisions and carrier cover.
- Treasure Box: inspect early close encounters and fuel usage before choosing a defensive or coordinated profile.
- Crossing: compare safer routes and fight selection without forcing every champion into one group.
- Starfish: evaluate protection after large captures, avoiding bad fights, and safe exits from hard camps.

These are candidate directions, not validated optimal strategies or gameplay changes. Each map currently has only one game per opponent with a 3/2 side split; side and opponent effects remain. Finish the fixed v22 baseline before uploading a new profile, then use matched follow-up games.

## Provenance

The generated per-map worksheets list every match ID and side. Frozen input records: matches/map-campaign-v22-20261028/results/b00-p0.json through b00-p4.json. New cause/damage analysis: first-five-map-mechanisms.json in that campaign folder, including input hashes. Death cause uses death-event target.kind; gem-loss cause sums gemLoss values by target.kind. No cause was inferred solely from a final score.

See also [TACTICAL_CANDIDATES.md](TACTICAL_CANDIDATES.md): additional user-proposed tactics and source findings; not yet validated or enabled.
