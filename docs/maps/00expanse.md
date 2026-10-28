# 00expanse - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **5-0**.

## Map evidence

- 80x80; 10 altars; 362 static gems
- Largest group: 44 gems, summed base strength 120

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | win | 1000/934 | 0/1 | 0 | eddb5e6a-146d-499e-b584-1762193ccdfd |
| eclipsed Sunlight | a | win | 1008/640 | 2/6 | 0 | b0385b66-bd8d-4f5e-9ecd-d77bb9cdf426 |
| The World Machine | b | win | 1033/708 | 1/16 | 44 | e146bc73-e907-49f1-9596-344f6b8384c9 |
| Princess Donut the Queen Anne Chonk | a | win | 1032/468 | 0/1 | 0 | bb3c4ac3-2ba0-43c3-b650-3c724ac5d842 |
| Knoobs | b | win | 1036/423 | 0/0 | 0 | d20980d8-8c4c-468d-b88a-27dc6e2402ef |

## Interpretation and next experiment

- Collected 5256; submitted 5109; lost 44 carried gems.
- Deaths 3 versus 24; fuel exhaustion 112; bot faults 0.
- Preserve v22 as this map's reference.
- Compare travel time and solo farming against grouping on this large map.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
