# 00fragment - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **2-3**.

## Map evidence

- 30x30; 2 altars; 68 static gems
- Largest group: 26 gems, summed base strength 80

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 42/1024 | 36/0 | 40 | a82ac0b3-8598-47df-b886-b4f57867d4b1 |
| eclipsed Sunlight | a | win | 881/365 | 20/42 | 84 | b8798fd2-e261-4d86-b041-fc21ab3b9673 |
| The World Machine | b | loss | 16/1012 | 34/3 | 52 | e1c66cec-9bb6-4e1c-9bb2-dc04324bc995 |
| Princess Donut the Queen Anne Chonk | a | loss | 503/695 | 28/27 | 52 | 4ee44d6a-61e8-442f-a548-088ce9038adf |
| Knoobs | b | win | 736/290 | 19/25 | 80 | 6853643d-39a4-48e4-871f-6e46d29900fb |

## Interpretation and next experiment

- Collected 2502; submitted 2178; lost 308 carried gems.
- Deaths 137 versus 97; fuel exhaustion 0; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
