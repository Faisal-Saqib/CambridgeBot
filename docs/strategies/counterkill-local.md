# Immediate counter-kill prototype (local only)

Source: bots/counterkill, copied from retained apex22. Not submitted; live v22 and the map campaign remain unchanged.

## Change and rationale

Before the heal/fight decision, a hurt or already-retreating champion may attempt a finishing action already in range. This tests a confirmed ordering weakness: heal precedes fight_enemies, so its low-health retreat can bypass can_finish.

The helper runs below 35% health or while healing, with fewer than 15 carried gems and at least 25000 fuel. It tries lower-health visible enemies outside their spawn. A basic attack uses a conservative 0.75*Strength estimate minus the visible shield, with a one-health margin. This is a heuristic, not an exact damage guarantee. Varg splash is excluded. Direct damage/CC spells must be ready, legal, in range and predicted by the SDK to remove the target's remaining health. Ren retaliation is checked against 0.25*Focus, a margin over the handbook 0.2 value.

No movement, long pursuit, area spells, dash, attack-reset combos, draft, items, wards or formation changes are added. Unknown enemy gems are not used; our own haul limits risk. If no suitable action exists, normal v22 behavior continues. FINISH_NOW traces record attempted finishing actions and observed target death; they consume some fuel and are part of this prototype's tested artifact.

## Risks and verification

A finishing hit does not guarantee survival against other enemies. The basic-damage estimate can be wrong, and the extra checks/logs cost fuel. Wider chase and ambush behavior need separate tests.

Pending a local release panel against apex22 on the_line, anvil, treasure_box, crossing and expanse, both sides. Inspect FINISH_NOW records, outcomes, deaths, gems and fuel. No online improvement is claimed, and the fixed baseline campaign must not be interrupted for this prototype.
