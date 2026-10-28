# 00dunes - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **3-2**.

## Map evidence

- 79x79; 2 altars; 238 static gems
- Largest group: 92 gems, summed base strength 120

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | loss | 458/1040 | 22/14 | 251 | 91cf9954-6910-446e-9707-46732c363c0a |
| eclipsed Sunlight | b | loss | 491/1003 | 28/13 | 43 | 0a38e3a9-e63b-404d-9270-07a13a252cf6 |
| The World Machine | a | win | 1016/104 | 16/24 | 196 | 1f215a3f-0080-4e42-9cef-9382fb18421e |
| Princess Donut the Queen Anne Chonk | b | win | 1039/178 | 4/25 | 0 | ee647e02-5727-4435-b1d5-9c7c42a28427 |
| Knoobs | a | win | 1025/589 | 25/17 | 183 | 994e5155-a696-4d06-83fa-b3dfa25f445b |

## Interpretation and next experiment

- Collected 4841; submitted 4029; lost 673 carried gems.
- Deaths 95 versus 93; fuel exhaustion 26; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Compare travel time and solo farming against grouping on this large map.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
