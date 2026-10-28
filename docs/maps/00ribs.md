# 00ribs - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **3-2**.

## Map evidence

- 51x85; 2 altars; 100 static gems
- Largest group: 43 gems, summed base strength 60

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | win | 1042/71 | 3/28 | 0 | 3c93335a-4007-4229-a5ac-138b1c0f8f31 |
| eclipsed Sunlight | a | loss | 71/1006 | 43/6 | 85 | b4e0042e-4418-4d28-968b-e1db5f8723fe |
| The World Machine | b | loss | 57/1001 | 43/15 | 163 | 64068746-4d50-4f60-b2a1-bca95d26a3e8 |
| Princess Donut the Queen Anne Chonk | a | win | 1014/43 | 6/23 | 43 | 0111962d-76c3-4c82-b4ad-850ab9556451 |
| Knoobs | b | win | 1028/0 | 2/3 | 0 | 5d0c6fdd-8e03-432e-ab14-6a30c8e6794f |

## Interpretation and next experiment

- Collected 3517; submitted 3212; lost 291 carried gems.
- Deaths 97 versus 75; fuel exhaustion 20; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
