# 00elkring - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **3-2**.

## Map evidence

- 30x30; 2 altars; 220 static gems
- Largest group: 22 gems, summed base strength 60

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | win | 1012/858 | 14/17 | 88 | 59b1f74e-1d9e-4d29-b24c-155a05e4dbb6 |
| eclipsed Sunlight | b | loss | 649/1001 | 6/7 | 66 | 8b2d11dc-38c4-4926-a397-116d62938d2b |
| The World Machine | a | loss | 418/1012 | 20/7 | 176 | 32dc6673-f696-4991-90c3-1ecc40bac6c4 |
| Princess Donut the Queen Anne Chonk | b | win | 1012/704 | 6/14 | 44 | 911ce8e1-7dde-4f00-8a62-e9854c22f939 |
| Knoobs | a | win | 1012/616 | 14/17 | 286 | a099e8fc-99f6-41be-99ba-263aca01734e |

## Interpretation and next experiment

- Collected 4895; submitted 4103; lost 660 carried gems.
- Deaths 60 versus 62; fuel exhaustion 0; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
