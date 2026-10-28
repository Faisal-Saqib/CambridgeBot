# 00monolith - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **4-1**.

## Map evidence

- 50x50; 6 altars; 670 static gems
- Largest group: 256 gems, summed base strength 200

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | win | 1106/862 | 8/7 | 37 | 27460985-e7cb-4a18-b29f-d3099e1109af |
| eclipsed Sunlight | a | loss | 911/1027 | 12/21 | 30 | 11815cf0-c604-4a66-b114-82bec0bda692 |
| The World Machine | b | win | 1060/837 | 5/13 | 0 | 702e7a82-3027-4c97-94c4-671207ff4027 |
| Princess Donut the Queen Anne Chonk | a | win | 1138/643 | 2/2 | 0 | 597eb14a-9712-4ccd-a24a-31f94db922df |
| Knoobs | b | win | 1001/546 | 14/9 | 55 | 95e0efd1-5027-40ec-a750-88c599d4b67a |

## Interpretation and next experiment

- Collected 5617; submitted 5216; lost 122 carried gems.
- Deaths 41 versus 52; fuel exhaustion 35; bot faults 0.
- Preserve v22 as this map's reference.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
