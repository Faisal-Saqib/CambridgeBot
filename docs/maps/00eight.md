# 00eight - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **2-3**.

## Map evidence

- 41x30; 1 altars; 230 static gems
- Largest group: 59 gems, summed base strength 180

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 607/1012 | 18/8 | 85 | a4137536-4e81-4ca0-830a-2679cfca7b22 |
| eclipsed Sunlight | a | loss | 998/1002 | 16/26 | 185 | bddefe74-a943-40d7-864c-25bd4cb9d2a0 |
| The World Machine | b | loss | 514/1011 | 19/14 | 126 | 3592b170-f328-4e15-9451-1fecccc68e15 |
| Princess Donut the Queen Anne Chonk | a | win | 1007/811 | 13/17 | 70 | 2daed8c4-9eef-4267-a7c1-403474bb3744 |
| Knoobs | b | win | 1001/669 | 33/26 | 552 | c1412c40-18ce-4a3d-b968-3b02c0638892 |

## Interpretation and next experiment

- Collected 5193; submitted 4127; lost 1018 carried gems.
- Deaths 99 versus 91; fuel exhaustion 0; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect the single altar's approach, locks and carrier survival.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
