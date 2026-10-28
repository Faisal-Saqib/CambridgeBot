# 00quarry - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **1-4**.

## Map evidence

- 35x29; 2 altars; 114 static gems
- Largest group: 46 gems, summed base strength 20

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 740/1010 | 23/5 | 266 | 124ac2ec-435e-4d93-afe1-6b172e154d1c |
| eclipsed Sunlight | a | loss | 215/1003 | 16/12 | 70 | 03dc8124-5391-4220-872c-6936e4655122 |
| The World Machine | b | loss | 288/1030 | 35/3 | 152 | d3552caa-5170-486c-97a3-22bb155ca4b7 |
| Princess Donut the Queen Anne Chonk | a | win | 1048/146 | 8/24 | 0 | be31fe64-218c-4226-b0d0-7d5a38b6a62f |
| Knoobs | b | loss | 128/1008 | 37/1 | 330 | 686dda22-e29d-4824-b091-3e066781b7e4 |

## Interpretation and next experiment

- Collected 3333; submitted 2419; lost 818 carried gems.
- Deaths 119 versus 45; fuel exhaustion 0; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
