# Cohesion: local whole-team formation experiment

Status: REJECTED (rigid whole-team cohesion, revision r4: 19/280 on the broad local gate, 0 engine-reported faults). Local only and never submitted; source and revisions are preserved for reference. Based on frozen `bots/apex22`. Live and working `bots/apex` remain v22. A smaller follow-up is [guarded-local.md](guarded-local.md).

## Intended behavior

- Elect one stable leader, preferring a melee champion. Preserve that leader while its heartbeat is fresh and it remains alive; replace it after death or a stale heartbeat.
- Broadcast the leader's position and round in the existing eight shared bytes, so allies can rejoin even without direct vision.
- Use one shared camp objective with a six-member claimant mask. Followers adopt the leader's objective instead of choosing distant camps.
- Coordinate banking around a shared altar. A carrier can lead the trip and nearby allies can protect it; small carriers can tribute on that same trip.
- Coordinate recovery trips. Injured champions retain emergency movement rather than being trapped by the normal formation boundary.
- Keep healthy movement near support, and prevent a leader's travel dash from leaving walking allies behind.
- Preserve v22's draft, items, tribute thresholds and combat targeting for this experiment.

## Shared-memory layout

| Byte | Meaning |
| --- | --- |
| 0 | Leader slot + 1, or zero |
| 1–2 | Rally x/y |
| 3 | Shared objective + 1, or zero |
| 4 | Six claimant bits |
| 5 | Combat focus (3 bits), gate flags (2 bits), travel/bank/home mode (2 bits) |
| 6–7 | Rally round as little-endian u16 |

Mode or leader changes clear the previous goal and claims. A full round timestamp avoids treating an old heartbeat as fresh after a byte-sized timestamp wraps. The pure protocol source contains round-trip, bit-isolation, claimant, leader-election and movement tests.

## First local result

The focused panel used both sides against apex22 on The Line, Anvil, Stampede, Starfish, Expanse and Islands.

- 0 wins from 12 games; 464 gems submitted across the candidate's games.
- Zero engine-reported bot faults in all 12 summaries.
- Expanse as Team A collected 26 gems, submitted none and suffered no deaths. That is a coordination/economy failure even without enemy kills.
- The first attempted panel used an underscore in the local The Line filename and ran no games. The completed panel used `00the-line.map26a`; its records are distinct.

Artifacts: `matches/panel-cohesion-20261028-151640/`, including `lead-checked-results.json`. The original non-debug candidate is retained while an instrumented copy is used to trace the failure. Debug traces are diagnostic evidence and are not treated as the same performance sample.

## Risks and next checks

Formation constraints can block useful movement, especially when an escort waits at the same distance that its leader is forbidden to exceed. Capture, banking and recall transitions must make forward progress. A rigid whole-team objective can also reduce farming income; fewer deaths alone do not establish an improvement.

Before promotion, verify movement progress and banking, execute the protocol tests, rerun the focused release panel, and compare a fixed candidate against the saved top-20 opponents. Preserve every failed result. The user's minimum of five completed online games before another gameplay iteration still applies.

## Current state and revisions (r4, local only)

bots/cohesion is LOCAL and UNSUBMITTED; working/live apex remains v22. Nothing here says the candidate is better or activated.

Current behavior: a stable elected leader publishes a shared rally position and objective. Followers regroup beyond 2 tiles; healthy movement normally cannot increase spacing beyond 3, with a bounded margin of 4 after 3 idle turns; emergencies are exempt. Banking and home trips are coordinated, empty escorts clear the altar's neighbors, and followers share the leader's job. Camp scoring uses the actual nearby party's damage for every candidate camp. Travel dashes are disabled while more than one ally lives. Draft, items and tribute limits are unchanged.

Local revisions, all against apex22 on the same six maps, both sides (these are revisions of one local implementation, not four published versions):

| Revision | Focused result | Folder (matches/) | Change |
| --- | --- | --- | --- |
| r1 | 0/12 | panel-cohesion-20261028-151640 | Original implementation. The escort waited at the same 3-tile boundary its banking leader could not exceed. |
| r2 | 3/12 | panel-cohesion-20261028-152721 | Desired regroup distance 2 inside the maximum tether 3, plus a regression test. The trace then showed empty carriers blocking the altar at (13,26) while Ryth held 11 gems at (15,27). |
| r3 | 3/12 | panel-cohesion-20261028-153144 | Altar clearance for empty escorts, plus a regression test. |
| r4 | 0/12 | panel-cohesion-20261028-153845 | Alternative camps no longer valued as solo despite a cohesive party; bounded obstruction margin. |

All revisions are kept; sources are archived under matches/top20-cohesion-20261028/ (r1-r4). Seven pure protocol tests were actually executed under WASI and passed; they cover bitfields/round trips, claims, death/stale leader election, tether recovery, banking progress, altar clearance and the bounded margin. They are not proof of integration correctness.

Weaknesses: grouped farming costs, congestion and possible extra recovery trips. Selected-map results cannot show general superiority. Context: the fresh top-20 v22 baseline won 1/25 games ([top20-cohesion-baseline.md](../top20-cohesion-baseline.md)). The minimum of five completed online games per fixed version still applies before the next gameplay iteration.

Broad local gate (raw counts, not acceptance): `python -X utf8 scripts/panel.py cohesion --opps apex22 titan --jobs 4` covered every published local map on both sides against apex22 and titan (280 games, 280 replay bundles saved, 0 failed). Raw panel output: cohesion vs apex22 5/140 (avg gems 323 - 990), cohesion vs titan 14/140 (avg gems 344 - 966), total 19/280 wins. Folder: matches/panel-cohesion-20261028-154431 (fault-diagnostics.json holds the raw per-game diagnostics). Failed games are left in the result. All 280 games had zero engine-reported faults. The candidate is rejected on these counts.
