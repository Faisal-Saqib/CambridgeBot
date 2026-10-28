# 00anvil - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **1-4**.

## Map evidence

- 37x31; 1 altars; 258 static gems
- Largest group: 200 gems, summed base strength 200

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 196/1000 | 20/10 | 154 | cf2a7952-5865-4cd0-846d-e826b9dcc1b6 |
| eclipsed Sunlight | a | loss | 67/1068 | 32/22 | 158 | b890e463-bd4c-43da-a792-ecacb3346901 |
| The World Machine | b | loss | 188/1006 | 28/17 | 57 | e3da2c87-c81e-4855-8004-bebdbdcb8834 |
| Princess Donut the Queen Anne Chonk | a | win | 1002/659 | 24/22 | 33 | c558a623-785c-42dc-8e89-6e47d5d21742 |
| Knoobs | b | loss | 42/969 | 47/3 | 49 | c78eaa39-3578-48a8-9264-87d828aae229 |

## Interpretation and next experiment

- Collected 1946; submitted 1495; lost 451 carried gems.
- Deaths 151 versus 74; fuel exhaustion 0; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Test control and delivery around the dominant gem group; determine whether it needs a raid or capture defense.
- Inspect the single altar's approach, locks and carrier survival.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
