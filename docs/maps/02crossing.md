# 02crossing - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **2-3**.

## Map evidence

- 51x51; 3 altars; 458 static gems
- Largest group: 57 gems, summed base strength 120

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | win | 1004/460 | 6/16 | 14 | 25270305-d29f-4eba-bf8b-a6716ead1894 |
| eclipsed Sunlight | b | loss | 574/1006 | 17/6 | 202 | ce068f4e-ae1d-481e-866e-4ae5283f74b9 |
| The World Machine | a | win | 1031/71 | 9/29 | 0 | 535cdf76-d84f-4d04-80c0-725bbd7bfee4 |
| Princess Donut the Queen Anne Chonk | b | loss | 955/1034 | 24/16 | 70 | 3569b929-beb5-407a-a12f-69c609c92cd0 |
| Knoobs | a | loss | 305/1006 | 36/3 | 220 | d9dbe87e-4cfd-4dc7-ba47-213c39a23dda |

## Interpretation and next experiment

- Collected 4493; submitted 3869; lost 506 carried gems.
- Deaths 92 versus 70; fuel exhaustion 41; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
