# 00breadcrumbs - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **1-4**.

## Map evidence

- 29x29; 1 altars; 154 static gems
- Largest group: 7 gems, summed base strength 0

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 210/1001 | 17/0 | 84 | b1c30a4d-1adb-4725-bcec-c25f5067a965 |
| eclipsed Sunlight | a | loss | 336/1036 | 16/6 | 154 | 747316c1-87bd-4ea4-8c8a-a52fed301857 |
| The World Machine | b | loss | 490/1015 | 15/7 | 126 | 98142c41-efae-4f4b-8496-c60720bda98f |
| Princess Donut the Queen Anne Chonk | a | win | 1001/378 | 4/16 | 21 | ee25d860-a4d9-4680-9a83-2579fc935836 |
| Knoobs | b | loss | 721/805 | 27/27 | 189 | e1635bc9-05a7-4808-bd57-c0611aec85d7 |

## Interpretation and next experiment

- Collected 3388; submitted 2758; lost 574 carried gems.
- Deaths 79 versus 56; fuel exhaustion 378; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect the single altar's approach, locks and carrier survival.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
