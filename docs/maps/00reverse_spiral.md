# 00reverse_spiral - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **2-3**.

## Map evidence

- 30x30; 2 altars; 334 static gems
- Largest group: 72 gems, summed base strength 160

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | loss | 594/1002 | 19/15 | 169 | 7e6a34a3-c7d6-4234-83b7-20d25e3f976d |
| eclipsed Sunlight | b | loss | 360/1006 | 31/20 | 169 | 94cb6a77-4ff4-4918-9762-feb1370d856c |
| The World Machine | a | win | 817/21 | 10/23 | 91 | df4c4ee2-fe46-4736-bf5a-1d9041609c14 |
| Princess Donut the Queen Anne Chonk | b | loss | 905/929 | 15/15 | 120 | 59909d5a-b1e5-415c-8f58-91044ce8ef9e |
| Knoobs | a | win | 1054/157 | 6/27 | 35 | f46d5a02-58eb-4a70-94be-05534fc85c6e |

## Interpretation and next experiment

- Collected 4485; submitted 3730; lost 584 carried gems.
- Deaths 81 versus 100; fuel exhaustion 0; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
