# 00gemfight - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **3-2**.

## Map evidence

- 30x30; 2 altars; 200 static gems
- Largest group: 78 gems, summed base strength 40

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | a | win | 1025/82 | 1/19 | 25 | 71bed804-0a6a-4d27-a502-2c9ac7f423bf |
| eclipsed Sunlight | b | loss | 201/1011 | 10/4 | 180 | f2822927-3143-485b-b567-951d1bfb4b0e |
| The World Machine | a | win | 1008/139 | 5/6 | 46 | fa24dfb7-f295-4427-a28b-7ef0b0bd19d2 |
| Princess Donut the Queen Anne Chonk | b | win | 1080/770 | 17/18 | 255 | 53394b20-5123-4c8d-ae39-c6cb5d4613ba |
| Knoobs | a | loss | 110/1012 | 44/6 | 342 | 4bad5db6-1299-441f-8026-a26d3e55285a |

## Interpretation and next experiment

- Collected 4435; submitted 3424; lost 848 carried gems.
- Deaths 77 versus 53; fuel exhaustion 60; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
