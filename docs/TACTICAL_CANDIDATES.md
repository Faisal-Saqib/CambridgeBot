# Tactical candidates from map analysis

These are investigations and local-test plans, not enabled gameplay. The live map campaign remains fixed on v22 so map comparisons stay valid. Use completed five-opponent map blocks as evidence before choosing a profile, and document each tested candidate separately.

## Finish a winnable fight before retreating

Confirmed from source: Bot::turn calls heal before fight_enemies. heal can select retreat below 15% health before fight_enemies reaches its can_finish check. This permits a low-health champion to leave without evaluating an available finishing hit. It is a code-path finding; the exact observed incident still needs replay/trace confirmation.

Candidate rule: assess ready damage, target health/shields, attack range, closing time and nearby support before a retreat. Favor a kill achievable this turn, or a short pursuit when survival is clearly sufficient. Do not decide from HP percentages alone. Unknown enemy gem inventory is not required; our own carried gems remain a known risk cost. Do not pursue indefinitely or count distant allies as immediate damage support.

## Fight as a coordinated frontline and backline

Test tighter positions when there is a shared objective or enemy pressure. Healthy melee champions hold the front; ranged damage stays close enough to contribute behind them. Recompute available support when frontline champions die, retreat or channel. Backline champions should withdraw when protection disappears unless a finishing kill remains feasible.

Enemy bots choose their own targets; melee units cannot force attacks onto themselves. The previous v23 regrouping implementation lost online, so another formation needs measured spacing, engagement readiness and farming-cost evidence rather than simply keeping everyone together all game.

## Central gems and alternate flanks

Trace why job scoring chose a side group before assuming the center was ignored by mistake. Check whole-group clear cost, remaining health, path reachability, capture state, enemy pressure and travel to an altar. A harmless central jackpot and a central monolith require different plans.

On a verified symmetric layout, compare mirrored routes/objectives. Fight if the local engagement is favorable; otherwise move toward a useful alternate flank without abandoning the only meaningful gem source. Hold a route choice long enough to avoid oscillating between sides. The user's exact central-gem replay/map is still unidentified.

## Near-spawn bait and counterattack

Use an already injured, empty-handed champion as bait only when healthy allies are close enough and there is a short, clear escape to spawn or cover. Do not deliberately injure allies or build the tactic around a sacrificial death. Respawn takes 60 rounds; safe recall takes 5 and is interrupted by damage or stun. Reaching spawn alive and staying through turn end provides recovery.

Teammates may use terrain cover, but enemy vision and wards can reveal them. If an enemy commits into range, focus it with available control and damage. If it does not follow, return to useful objectives rather than waiting indefinitely. If support is lost or incoming burst exceeds the bait's escape budget, abort. This is a situational map profile, not an economy plan for open farming maps.

## Verification approach

Use isolated local candidates while baseline collection continues; do not change live v22 midway. Test the targeted behavior and representative unaffected maps. Before online promotion, require completed baseline evidence, confirmed candidate version and matched real-opponent follow-ups. Record lost opportunities, deaths, gems, time spent chasing/regrouping and fuel, with limitations stated. No candidate is considered successful merely because it sounds plausible.
