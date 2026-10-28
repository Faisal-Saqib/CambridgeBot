# apex v22 - smaller tribute hauls (rollback baseline)

Submission `ff1fc23c-7e9d-42b4-9744-b63a36108c6a`. Formerly live/selected; now inactive and preserved in bots/apex22 as the rollback baseline. Current bots/apex is v24 guarded support.

## Behavior

Normal banking thresholds are 30 gems anywhere, 15 within 15 tiles of an altar, 5 within 4. Threatened champions and Marcella use 15/8/5. Threatened means health below 60%, an enemy seen within 14 tiles in the last 40 rounds, or a teammate death in the last 100 rounds. Altar distance includes the existing danger penalty. Heal/fight priority and capture/gate exclusions still apply; a lower threshold alone does not force immediate delivery.

Compared with v21, ward placement is removed. Draft, items, abilities and farming are otherwise the same as the pre-cohesion implementation. v23 partnerships are not active in this version.

## Verification

Local release panel: 4/10 against v20 on five maps, both sides, with zero faults. Matched online panel: 3-2 against Ascendance and 2-3 against QS2 (5/10), versus baseline 4/10. Same maps, sides, seeds and engine build; saved opponent submissions requested. Opponents were within +/-200 rating points.

Across ten online games: 7242 submitted gems, 125 deaths, 1918 gems lost, 338 tributes averaging 21.43 gems, 263 fuel-exhaustion events and 0 bot faults. This was the strongest online result of the four tested versions, not proof of general ladder superiority. [Full comparison](../online-cycle-20261027.md).

## Strengths and weaknesses

- Smaller completed hauls and more frequent banking; improved this panel's score and Ascendance record.
- Total carried-gem loss remains close to baseline; the_line still banked zero against both opponents.
- Extra altar travel can reduce farming. Combat/capture decisions can delay delivery.
- No new ward, consumable or formation behavior is enabled. These require separate evidence and testing.
