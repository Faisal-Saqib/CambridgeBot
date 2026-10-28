# 02treasure_box - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **3-2**.

## Map evidence

- 35x35; 1 altars; 449 static gems
- Largest group: 61 gems, summed base strength 80

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 845/1002 | 29/14 | 272 | 6823ce52-516c-43f3-a9f5-f87ff610bcd6 |
| eclipsed Sunlight | a | loss | 556/1019 | 36/19 | 210 | bf3e66d2-5c77-48a3-b5c7-8778eaa13cfa |
| The World Machine | b | win | 1000/294 | 26/26 | 299 | 777f9da7-02ea-4ae2-b4cc-95f7c0cc7256 |
| Princess Donut the Queen Anne Chonk | a | win | 1051/233 | 7/11 | 28 | 8ac21ba7-6c3b-40ce-9fce-77eccf465b8f |
| Knoobs | b | win | 1023/667 | 25/38 | 250 | 3abf1cdd-69b5-48f7-921b-311b69e831ea |

## Interpretation and next experiment

- Collected 5639; submitted 4475; lost 1059 carried gems.
- Deaths 123 versus 108; fuel exhaustion 618; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect the single altar's approach, locks and carrier survival.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
