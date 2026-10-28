# 00the_line - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **1-4**.

## Map evidence

- 33x33; 1 altars; 193 static gems
- Largest group: 161 gems, summed base strength 0

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | loss | 0/1022 | 18/2 | 483 | 4a751422-dc9d-4fc4-bcf7-2b33a20452d1 |
| eclipsed Sunlight | b | loss | 161/1106 | 13/5 | 342 | fb4bca8a-6ffe-45fb-9371-172329a3330a |
| The World Machine | a | loss | 81/1094 | 20/2 | 261 | 1ed04c6c-dbdd-4d03-bc1e-a8fbc5568093 |
| Princess Donut the Queen Anne Chonk | b | win | 1030/511 | 8/18 | 104 | f7fd0ebe-0135-47d6-812b-c6078aa1d710 |
| Knoobs | a | loss | 0/1070 | 36/1 | 169 | dbb6973a-5436-491e-9974-e723ad20c54e |

## Interpretation and next experiment

- Collected 2647; submitted 1272; lost 1359 carried gems.
- Deaths 95 versus 28; fuel exhaustion 0; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Test control and delivery around the dominant gem group; determine whether it needs a raid or capture defense.
- Inspect the single altar's approach, locks and carrier survival.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
