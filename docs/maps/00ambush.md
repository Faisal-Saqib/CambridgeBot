# 00ambush - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **4-1**.

## Map evidence

- 100x100; 4 altars; 270 static gems
- 28/270 static gems were recorded outside the spawn walkable component
- Largest group: 51 gems, summed base strength 120

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | win | 1034/251 | 2/8 | 0 | 8248d602-f358-44e3-b890-7934e36c3c7e |
| eclipsed Sunlight | b | win | 1021/961 | 14/4 | 0 | d5980250-bdf4-4cc3-a4db-d109dde31df6 |
| The World Machine | a | win | 1015/516 | 1/15 | 0 | a9cbecfe-76ae-4efc-b765-f9b2fd258735 |
| Princess Donut the Queen Anne Chonk | b | loss | 946/1055 | 5/4 | 51 | 509f70fd-5187-4b36-86bd-05012a1947d9 |
| Knoobs | a | win | 1002/411 | 15/4 | 0 | 35bb3dc8-3e78-4b87-b689-11954acc9512 |

## Interpretation and next experiment

- Collected 5153; submitted 5018; lost 51 carried gems.
- Deaths 37 versus 35; fuel exhaustion 73; bot faults 0.
- Preserve v22 as this map's reference.
- Compare travel time and solo farming against grouping on this large map.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
