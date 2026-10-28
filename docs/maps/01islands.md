# 01islands - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **2-3**.

## Map evidence

- 60x60; 10 altars; 608 static gems
- 372/608 static gems were recorded outside the spawn walkable component
- Largest group: 58 gems, summed base strength 120

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 442/1034 | 11/3 | 16 | d4c986c1-1bce-4473-b464-98d62723b3f8 |
| eclipsed Sunlight | a | loss | 742/1056 | 9/16 | 62 | 4b8c5ba4-f936-4722-a1a7-e852073aa254 |
| The World Machine | b | loss | 630/1032 | 6/10 | 120 | c41513ae-cabc-4e1a-9a14-492722556299 |
| Princess Donut the Queen Anne Chonk | a | win | 1005/296 | 4/9 | 12 | 823a0474-4776-4a5f-bcf3-bb7945a05280 |
| Knoobs | b | win | 1052/0 | 2/0 | 12 | 1af268cd-ec59-425f-a56b-7b1462ed8c52 |

## Interpretation and next experiment

- Collected 4279; submitted 3871; lost 222 carried gems.
- Deaths 32 versus 38; fuel exhaustion 171; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Test terrain traversal and access to disconnected gem sources.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
