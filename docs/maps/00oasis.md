# 00oasis - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **3-2**.

## Map evidence

- 29x29; 2 altars; 124 static gems
- Largest group: 36 gems, summed base strength 120

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 110/1022 | 33/5 | 56 | 110d8045-e844-4a06-89c0-decf57c2fe4c |
| eclipsed Sunlight | a | win | 1008/772 | 47/44 | 91 | 3b6c4b08-3a45-471d-b1f3-50892521e870 |
| The World Machine | b | win | 1020/108 | 15/38 | 98 | 8841163c-6782-4232-9a52-75509081810b |
| Princess Donut the Queen Anne Chonk | a | win | 1006/208 | 8/25 | 12 | 2883d4ac-5685-41c2-9138-8cc7dc1791c6 |
| Knoobs | b | loss | 198/818 | 64/16 | 144 | a2c8fbf7-5239-4c5a-9950-118160f802f8 |

## Interpretation and next experiment

- Collected 3787; submitted 3342; lost 401 carried gems.
- Deaths 167 versus 128; fuel exhaustion 0; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
