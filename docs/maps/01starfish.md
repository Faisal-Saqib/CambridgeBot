# 01starfish - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **2-3**.

## Map evidence

- 50x50; 2 altars; 334 static gems
- Largest group: 118 gems, summed base strength 360

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | win | 1011/631 | 19/46 | 280 | b1b9607a-8834-4e98-a898-fe40d7ba3f48 |
| eclipsed Sunlight | b | loss | 345/1058 | 29/21 | 353 | c65f9ca5-d7d2-44f2-938e-de9cb5b7e308 |
| The World Machine | a | loss | 337/1033 | 45/40 | 616 | 04ee8a6c-e3f6-4e0a-817a-ee3c5267cbe9 |
| Princess Donut the Queen Anne Chonk | b | win | 1030/212 | 14/33 | 110 | f5115409-0f94-4507-99a9-4c524faae6fd |
| Knoobs | a | loss | 158/880 | 63/32 | 803 | 7b452971-c682-4893-a139-eb1a9f228428 |

## Interpretation and next experiment

- Collected 5336; submitted 2881; lost 2162 carried gems.
- Deaths 170 versus 172; fuel exhaustion 26; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
