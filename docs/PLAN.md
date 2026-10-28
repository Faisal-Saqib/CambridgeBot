# Strategy plan - Warband

Goal: improve general performance against real teams within approximately +/-200 rating points of our current rating. Focus on protecting gem income and keeping combat partners together. Test Ascendance alongside other opponents when its rating is in range.

Status: v22 retained and confirmed live/selected; working bots/apex matches bots/apex22. Forty online games completed: v20 4/10, v21 2/10, v22 5/10, v23 3/10. See [cycle results](online-cycle-20261027.md), [ONLINE_TESTING.md](ONLINE_TESTING.md), [FULL_STRATEGY.md](FULL_STRATEGY.md) and [CHANGELOG.md](CHANGELOG.md).

## Evidence and limits

Historical Ascendance analysis recorded 2 wins and 8 losses, 2,586 carried gems lost, 184 deaths (30 to camps), no personal wards against 656 enemy ward placements, and a substantial economy gap in several losses. These are historical aggregates; the cached summaries do not identify our platform submission.

Assist records show multiple contributors to many kills, but do not prove simultaneous attacks or exact formation. Purchased locks and crystals show inventory investment, not confirmed use. A stalled team score alone does not prove an altar lock caused it. More item purchases may follow a stronger economy rather than cause it. Replay evidence is needed to distinguish these mechanisms.

## P1 - smaller tribute hauls (active in v22)

| Situation | Anywhere | Altar within 15 tiles | Altar within 4 tiles |
| --- | --- | --- | --- |
| Normal | >=30 gems | >=15 | >=5 |
| Threatened or Marcella | >=15 gems | >=8 | >=5 |

Threatened means an enemy seen within 14 tiles during the last 40 rounds, a teammate death in the last 100 rounds, or health below 60%. Retain the existing endgame banking rule. These are the implemented candidate values; the earlier 25/12/6 proposal was not implemented.

Expected benefit: fewer gems exposed to each death. Risks: longer total travel and interrupted farming. Heal/fight decisions still precede banking, and capture/gate exclusions still apply; verify that carriers actually reach an altar rather than merely lowering a constant.

## P2 - personal wards (tested in v21; disabled in v22)

Use the free ward near an altar or toward the enemy spawn when the current ward is far away. Vision is personal, not shared. Test whether placements reveal useful approaches and change decisions; placement count alone is not evidence that they prevented deaths. Check fuel use and action legality.

## P3 - melee/ranged partnerships (v23 tested and rejected)

v23 implemented Ryth/Vesper/Willow and Marcella/Tavi formations, shared claims and local regrouping. It scored 3/10 online versus v22's 5/10 and is archived. The goals below remain future work; they are not active in the retained bot. Any next attempt must measure farming cost and actual separation, rather than assume grouping is always beneficial.

- Five picks: Ryth with Vesper; Marcella with Tavi; Willow supports an injured nearby pair.
- Four picks: the same two pairs. Three picks: one trio.
- Share a farming objective and keep partners close, with a bounded wait and solo fallback when a partner dies, recalls or banks. Avoid the earlier squad experiment's long staging delays.
- Camps target the nearest champion, so a melee anchor can absorb camp attacks. Enemy bots choose their targets freely; protect ranged partners through positioning, control, retreat paths and focus fire.
- Evaluate shared captures and carrier escort against their travel cost. Coordinate stuns only when ability targeting and cooldowns permit it. Do not add every formation feature in one unmeasured change.

## P4 - altar access and escape (planned)

Detect enemy altar locks. Compare the cost of removing a lock with another altar route; single-altar maps need a reliable lock-breaking path. Trial buying and placing our own locks separately from teleport-crystal escape. Teleports channel for three turns and can still fail through stun or death. Record purchases separately from observed uses.

## P5 - item economy (experimental)

Preserve the combat opening while evaluating Capture and Prospector later in the build. The completed historical apexb3 follow-up won 224/420 local matches (80/140, 75/140 and 69/140 against three related opponents), with no recorded bot faults. [Frozen results](local-panel-followup-2026-10-27.json) preserve the evidence. This is a candidate for online testing, not a proven improvement.

Keep Power/Bruiser stacking and Treasure trials separate from banking and formation changes. Engine metadata exposes passive magnitudes, but does not explain every passive; verify effects before documenting them as mechanics.

## P6 - robustness (planned)

Investigate fuel exhaustion on the maps where it was recorded. Attribute each event to its champion/team and distinguish initialization from repeated turn stalls. Use replay evidence to check whether camp deaths came from insufficient escape health, enemy pressure, pathing or interrupted execution.

## Version order

| Local label | Content | Status |
| --- | --- | --- |
| v20 baseline | Jackpot capture, contested capture, brawl-map hunting | Historical baseline; saved in bots/apex20 |
| v21 | Smaller tribute hauls and personal wards; source bots/apex21 | Rejected, 2/10 online |
| v22 | Smaller tribute hauls without wards; source bots/apex / bots/apex22 | Retained live, 5/10 online |
| v23 | v22 plus melee/ranged cohesion; source bots/apex23 | Archived, 3/10 online |
| Next candidate | One evidence-backed change from partnerships, altar access, items or robustness | Requires the complete current batch and analysis |

Future submission numbers come from the platform; do not reserve or infer them from local labels. Every candidate gets its own explanation with strengths, weaknesses, changes, results and status.

## Verification

Follow [ONLINE_TESTING.md](ONLINE_TESTING.md): five finished online games on a fixed version before each tweak, focused local regressions after implementation, then five candidate online games before another tweak. Preserve match IDs and attribution. Use broader panels for a concrete remaining risk, not to repeat unchanged checks. The previous 52% local threshold was a screening heuristic, not statistical proof or an automatic promotion rule.

## Map-specific profiles: next investigation

The user requested per-map testing against five real teams. The new baseline campaign keeps v22 fixed, covers 70 maps with five opponents each and respects 50 outgoing match-group requests per hour, each containing five games. See [MAP_CAMPAIGN.md](MAP_CAMPAIGN.md) and [MAP_MATRIX.md](MAP_MATRIX.md). The earlier aggregate panels remain historical context; evaluate each map separately before choosing a draft, grouping, farming, banking or traversal profile. Do not assume one global winner or hard-code untested per-map behavior.
