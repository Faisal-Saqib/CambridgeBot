# 00gem_fields - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **3-2**.

## Map evidence

- 50x40; 4 altars; 364 static gems
- Largest group: 71 gems, summed base strength 60

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 537/1004 | 21/8 | 77 | bc2fb23c-760d-4461-af29-b632692fe5fe |
| eclipsed Sunlight | a | loss | 275/1005 | 18/8 | 106 | 4bdf7a45-bb45-486a-99c7-dca5320a8d88 |
| The World Machine | b | win | 1021/365 | 12/10 | 14 | bca789e9-668a-468a-9603-80859cde80f6 |
| Princess Donut the Queen Anne Chonk | a | win | 1040/293 | 5/15 | 14 | 5b62c885-67b0-4b3c-8016-beb66921eb95 |
| Knoobs | b | win | 1063/382 | 14/23 | 184 | 17372c4e-473c-4ca7-b85b-ddc11a4a64ee |

## Interpretation and next experiment

- Collected 4373; submitted 3936; lost 395 carried gems.
- Deaths 70 versus 64; fuel exhaustion 29; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
