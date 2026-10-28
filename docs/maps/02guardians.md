# 02guardians - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **1-4**.

## Map evidence

- 41x41; 1 altars; 688 static gems
- Largest group: 200 gems, summed base strength 200

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | loss | 194/806 | 29/33 | 232 | 4a360a90-c1f8-4bc8-8421-e64ca57f27be |
| eclipsed Sunlight | b | loss | 497/580 | 42/49 | 100 | 08fae5f5-2522-4afe-943d-00912fc60654 |
| The World Machine | a | loss | 29/825 | 43/43 | 272 | 558c011b-1c4c-4017-b26a-a186f861abc7 |
| Princess Donut the Queen Anne Chonk | b | loss | 200/218 | 40/4 | 686 | 76486ab2-ccc3-43d9-b791-bebae33f1e9d |
| Knoobs | a | win | 1104/0 | 25/7 | 453 | 822a140a-c664-46aa-9eeb-742a3056994e |

## Interpretation and next experiment

- Collected 3825; submitted 2024; lost 1743 carried gems.
- Deaths 179 versus 136; fuel exhaustion 20; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect the single altar's approach, locks and carrier survival.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
