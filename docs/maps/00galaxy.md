# 00galaxy - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **1-4**.

## Map evidence

- 93x93; 2 altars; 113 static gems
- Largest group: 35 gems, summed base strength 0

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | win | 1012/562 | 13/13 | 98 | 36dfec36-d02f-480a-845f-f3edab2626c1 |
| eclipsed Sunlight | b | loss | 35/1027 | 21/2 | 259 | 72e956ea-b203-47df-8172-23fc90e36aeb |
| The World Machine | a | loss | 294/1026 | 27/3 | 144 | 4f34aa98-2ec2-4d3b-b8ef-4a793ba1dbe1 |
| Princess Donut the Queen Anne Chonk | b | loss | 961/1006 | 25/13 | 165 | 369df107-33e3-4278-b774-c04566013cab |
| Knoobs | a | loss | 165/1002 | 27/0 | 210 | 56f7d9b7-4975-4894-87a3-9d2ca9c34be0 |

## Interpretation and next experiment

- Collected 3413; submitted 2467; lost 876 carried gems.
- Deaths 113 versus 31; fuel exhaustion 28; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Compare travel time and solo farming against grouping on this large map.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
