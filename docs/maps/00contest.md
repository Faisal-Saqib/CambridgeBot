# 00contest - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **1-4**.

## Map evidence

- 50x50; 2 altars; 400 static gems
- Largest group: 200 gems, summed base strength 200

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 200/1000 | 35/5 | 0 | 61f7b367-9324-4fec-bb2e-1269dc415afd |
| eclipsed Sunlight | a | loss | 0/1000 | 59/6 | 200 | 289d3b77-39ef-480b-9b43-cffb7da0068a |
| The World Machine | b | loss | 200/1000 | 48/16 | 400 | c1af771b-4a69-4735-b872-9c3d4871ce06 |
| Princess Donut the Queen Anne Chonk | a | win | 1000/800 | 10/28 | 800 | 65b49fa6-f59c-4958-94ff-bff8cd9ab8fd |
| Knoobs | b | loss | 0/400 | 76/10 | 200 | ce990b4e-7cb7-497c-98c9-c4ede59aa80d |

## Interpretation and next experiment

- Collected 3000; submitted 1400; lost 1600 carried gems.
- Deaths 228 versus 65; fuel exhaustion 0; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Test control and delivery around the dominant gem group; determine whether it needs a raid or capture defense.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
