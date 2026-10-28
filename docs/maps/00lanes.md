# 00lanes - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **3-2**.

## Map evidence

- 90x30; 18 altars; 294 static gems
- Largest group: 22 gems, summed base strength 60

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 948/1001 | 10/5 | 4 | 5c7efdfd-aa7e-40a0-aadd-d4d5026c5f28 |
| eclipsed Sunlight | a | win | 1019/916 | 4/9 | 4 | 32da544b-d154-4fa5-b6a6-aabc0e8452d3 |
| The World Machine | b | loss | 962/1009 | 6/7 | 99 | 6b9a1d15-2927-4bb6-bc68-e75980d8e1cc |
| Princess Donut the Queen Anne Chonk | a | win | 1006/847 | 5/9 | 0 | 4f487bd0-6cd9-4e27-a765-990788d3ab9a |
| Knoobs | b | win | 1006/867 | 16/6 | 126 | 66d05a3f-48f7-41ca-babc-1f6a635849e7 |

## Interpretation and next experiment

- Collected 5229; submitted 4941; lost 233 carried gems.
- Deaths 41 versus 36; fuel exhaustion 762; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
