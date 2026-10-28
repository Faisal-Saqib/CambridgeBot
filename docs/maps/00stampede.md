# 00stampede - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **1-4**.

## Map evidence

- 60x50; 2 altars; 160 static gems
- Largest group: 160 gems, summed base strength 360

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | loss | 160/1120 | 46/2 | 0 | 3a33954c-253f-4f35-9617-4b22eaaa19bc |
| eclipsed Sunlight | b | loss | 374/1026 | 20/19 | 426 | 9d778e0f-5e56-4eb2-86da-a8915e4b2465 |
| The World Machine | a | loss | 53/1067 | 30/7 | 107 | ebf07a8e-22d2-4f2a-8b62-1ed50256e856 |
| Princess Donut the Queen Anne Chonk | b | win | 867/93 | 8/3 | 133 | e5bae63b-b3b4-4941-b598-23b60788ad9f |
| Knoobs | a | loss | 240/560 | 22/8 | 840 | 8f98dcfa-2219-4e64-a55f-eed4aa817c89 |

## Interpretation and next experiment

- Collected 3253; submitted 1694; lost 1506 carried gems.
- Deaths 126 versus 39; fuel exhaustion 10; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Test control and delivery around the dominant gem group; determine whether it needs a raid or capture defense.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
