# 00collision - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **0-5**.

## Map evidence

- 41x41; 2 altars; 280 static gems
- Largest group: 66 gems, summed base strength 180

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | loss | 356/1008 | 20/8 | 209 | 1f386edc-f84d-4df9-b14a-8e511c68d038 |
| eclipsed Sunlight | b | loss | 543/1042 | 17/6 | 119 | 3485a180-7ca7-4d3c-aded-911065224164 |
| The World Machine | a | loss | 133/1041 | 27/5 | 143 | 14822268-e8aa-4f06-9d95-2560182da730 |
| Princess Donut the Queen Anne Chonk | b | loss | 288/1011 | 10/1 | 52 | 51f08d4c-18dc-44a2-807d-3c91dd999c7c |
| Knoobs | a | loss | 0/1001 | 45/1 | 66 | 575c4846-5ce1-4c58-aad2-6a34bd806028 |

## Interpretation and next experiment

- Collected 1946; submitted 1320; lost 589 carried gems.
- Deaths 119 versus 21; fuel exhaustion 13; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
