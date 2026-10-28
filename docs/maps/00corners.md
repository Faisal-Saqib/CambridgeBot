# 00corners - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **2-3**.

## Map evidence

- 71x71; 5 altars; 396 static gems
- Largest group: 48 gems, summed base strength 140

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | loss | 170/1003 | 24/4 | 152 | 12168761-5cc3-442b-804d-3890227a8209 |
| eclipsed Sunlight | b | loss | 484/1005 | 10/7 | 111 | 9e3bac27-db2b-4187-bdb6-0e771929bf3c |
| The World Machine | a | win | 1019/371 | 3/22 | 0 | 7b425d68-1d0a-4506-b638-cbb1038c2974 |
| Princess Donut the Queen Anne Chonk | b | loss | 488/1038 | 12/10 | 74 | 619b2744-58d0-4f1a-a517-5010ffb6a678 |
| Knoobs | a | win | 1001/440 | 16/7 | 52 | 3d6d1b96-5c37-4327-b1a8-9890e1403284 |

## Interpretation and next experiment

- Collected 3643; submitted 3162; lost 389 carried gems.
- Deaths 65 versus 50; fuel exhaustion 252; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Compare travel time and solo farming against grouping on this large map.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
