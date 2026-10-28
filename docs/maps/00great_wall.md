# 00great_wall - map strategy worksheet

<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->

Fixed baseline: v22. Coverage: **5/5 opponents**. Record: **2-3**.

## Map evidence

- 50x40; 4 altars; 1404 static gems
- Largest group: 414 gems, summed base strength 400

Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.

## Results

| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |
| --- | --- | --- | --- | --- | --- | --- |
| Ascendance | b | loss | 981/1003 | 7/15 | 143 | efe95216-f2de-451d-8935-cc249a3e9b62 |
| eclipsed Sunlight | a | loss | 793/1019 | 10/25 | 302 | cd33eb2b-fe3a-4d11-9ede-d38bb82df49c |
| The World Machine | b | win | 1009/0 | 6/26 | 45 | 05a5863b-14f6-4ca4-908a-8cdeacc28daa |
| Princess Donut the Queen Anne Chonk | a | loss | 993/1009 | 12/5 | 268 | b16e938c-252a-415a-b5c2-511b4822612e |
| Knoobs | b | win | 1011/625 | 9/5 | 169 | da9743b8-dabd-47ac-921a-5d8dbc16ee62 |

## Interpretation and next experiment

- Collected 6045; submitted 4787; lost 927 carried gems.
- Deaths 44 versus 76; fuel exhaustion 26; bot faults 0.
- Investigate a dedicated map profile before changing global behavior.
- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem.

These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.
