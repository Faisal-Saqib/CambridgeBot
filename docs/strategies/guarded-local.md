# Guarded support (v24, live, experimental)

Platform v24, submission `758c6fd5-4884-4477-91ed-78f2b61f2e59` (Live:24 Selected:24, Mode: PINNED VERSION, confirmed after activating 24). Source: bots/apex, byte-identical to the frozen bots/guarded (archive matches/top20-cohesion-20261028/guarded-r1-source). Based on apex22.

v24 guarded support is live at the user's explicit request for immediate publication before their Devin weekly quota runs out. Experimental release: local 50/140 against apex22, three WASI protocol tests passed, zero faults across the full 140-game gate; no online candidate results yet. v22 is the preserved rollback baseline. Next gameplay tweak must follow at least five completed v24 online matches, all new opponents currently top20.

Follows the rejected rigid formation in [cohesion-local.md](cohesion-local.md). A proposed follow-up idea is in [prism-carry-plan.md](prism-carry-plan.md).

## Behavior

- Individual farm claims (six camp-claim bytes) and the combat-focus byte are preserved. Normal farming is unchanged when no alert is active.
- Shared byte 7 is multiplexed: gate flags in bits 0-1, a stable support-leader slot + 1 in bits 2-4, and an alert generation counter in bits 5-7. Writers re-read the byte before masked writes, so one field never clobbers another.
- A generation change refreshes a local 20-round alert; there is no alert initially. Seeing enemies or recent allied deaths keeps the alert alive.
- A living banking carrier leads in preference to the current healthy leader. Recovering champions publish their spawn goal and are excluded from leadership.
- Under an alert, distant followers close to within 3 tiles using ordinary movement. Shooting and retreat decisions, a follower's own banking and active captures take priority. There is no hard movement veto and no shared recall.
- Jobs near the leader's intent are favored (the leader's own camp doubles, camps over 8 tiles from its goal are quartered), and a follower may join the leader's camp even if the normal join cap is full.
- Publishing altar and home intents lets allies follow outside vision using cached fields. Empty escorts step aside at the altar. Travel dashes are disabled while an alert is active.
- Draft, items and tribute limits are unchanged.

## Tradeoff and risks

Selective support aims to help carriers and threatened farmers without forcing the whole team to move together, but it also pulls followers off their own camps and may cost farming income. Alerts triggered by any visible enemy may fire often, and a leader's intent can be wrong. Selected-map results cannot show general superiority.

## Verification

Three pure protocol tests (field isolation, alert-counter wrap, alert expiry) were executed under WASI and passed. Focused local panel against apex22 on The Line, Anvil, Stampede, Starfish, Expanse and Islands, both sides (12 games, 0 failed bundles): guarded vs apex22 2/12, avg gems 509 - 875. Folder: matches/panel-guarded-20261028-160047 (an earlier identical run, before a byte-7 cache synchronization correction, gave the same per-game output: matches/panel-guarded-20261028-155937). The per-game lines are in each folder's run-batch.log and the panel output.

The minimum of five completed online games per fixed version still applies before the next gameplay iteration.

Broad local gate (raw counts): `python -X utf8 scripts/panel.py guarded --opps apex22 --jobs 4` covered every published local map on both sides against apex22 (140 games, 140 replay bundles saved, 0 failed). Raw panel output: guarded vs apex22 50/140 (avg gems 663 - 826). Folder: matches/panel-guarded-20261028-160447 (fault-diagnostics.json holds the raw per-game diagnostics). Source frozen at matches/top20-cohesion-20261028/guarded-r1-source.
