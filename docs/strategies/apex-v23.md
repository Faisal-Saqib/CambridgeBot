# apex v23 - melee/ranged cohesion (rejected online trial)

Frozen source: bots/apex23. Submitted as 08ae3185-ed3d-447e-b1ac-7d3c62db691a and tested online. This mode is archived; working bots/apex and the live selection were restored to v22.

## Change

Ryth anchors Vesper and Willow; Marcella anchors Tavi. Three-champion drafts put Vesper and Marcella with Ryth. Missing roles fall back to independent play. Followers adopt valid anchor claims for dangerous camps or local threat/brawl conditions; safe clusters retain the original job-scoring rules, although nearby regrouping can still limit separation and farming throughput.

Empty-handed followers may take one ordinary step toward a visible healthy anchor when more than three tiles apart. Immediate enemy danger, carrying gems, capture, healing and channels prevent this extra regroup step. No new path search or waiting timer is added. If no step improves distance, normal behavior continues. Nearby partners may share a multi-tile capture; single-tile captures retain the old policy. Claims clear during non-farm activity and channels to avoid stale assignments.

## Rationale and limits

The banking-only v22 batch finished ten matched online games: 5/10 overall, 3/5 against Ascendance, versus baseline 4/10 and 1/5. Smaller hauls alone still banked zero on the_line against both opponents. This candidate tests local cohesion as a separate change, preserving banking limits, draft, items, abilities and disabled wards.

Camps target the nearest champion; enemies choose their targets freely. These partnerships do not guarantee that a ranged champion is protected, that every reward is shared, or that both partners bank simultaneously. Regrouping may cost farming time. An unseen partner is not chased by position, though a valid shared group claim can still guide farming.

## Verification

Local targeted panel: 7/12 against apex22, zero faults. Both anvil and crossing games won; both expanse games lost. Full local panel: 72/140 on all 70 maps/both sides, zero faults on either side. Initial failed run produced no games and was not counted.

Ten matched online games: 0-5 against Ascendance and 3-2 against QS2 (3/10), versus v22's 5/10. Our submissions fell 7242 to 5633 and deaths rose 125 to 163. Raw gem loss fell 1918 to 1352 alongside lower collection; that is insufficient evidence of better carrier protection.

Decision: reject this implementation for the live bot; preserve it for further investigation. More adaptive grouping may still help, but it needs a separate batch and mechanism evidence. [Full results](../online-cycle-20261027.md).
