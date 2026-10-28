# 00crater - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **3-2**.

## Map evidence

- 61x61; 1 altars; 158 static gems
- Largest group: 64 gems, summed base strength 120

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | win | 1000/514 | 15/20 | 118 | f6cb8346-5512-4ce7-bd63-756ae203de67 |
| eclipsed Sunlight | a | loss | 68/1013 | 31/4 | 165 | 640531d5-e8a6-4ee2-8233-cc9b0f26b9f4 |
| The World Machine | b | win | 1035/36 | 5/28 | 96 | e53e7afe-fc28-4ce8-bbe1-25c62d1ea5bb |
| Princess Donut the Queen Anne Chonk | a | win | 1034/151 | 9/29 | 139 | cd3dc45d-99e6-41a6-ac67-391753bdf7ed |
| Knoobs | b | loss | 29/1003 | 36/7 | 344 | 38562e7a-8d7d-4a93-af89-824e7e8e5001 |

## Interpretation and next experiment

- Collected 4115; submitted 3166; lost 862 carried gems.
- Deaths 96 versus 88; fuel exhaustion 0; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect the single altar's approach, locks and carrier survival.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
