# Handoff prompt — Cambridge Battlecode bot improvement task

Give this prompt to the AI that will code and test the next bot versions. Everything
below is the agreed context, the requested strategy ideas, suggested additions, and
the rules that must not be broken.

## 1. Codebase and environment

- Repository root: this repo (Cambridge Battlecode 2026a, CAMBC engine).
- Current live bot: **v24 "guarded support"** in `bots/apex` (Rust). It is pinned live
  on the platform (submission `758c6fd5-4884-4477-91ed-78f2b61f2e59`).
- `bots/apex22` = v22, the preserved rollback baseline. `bots/titan` = the original
  baseline (v19). `bots/guarded` = frozen v24 source. `bots/cohesion` = REJECTED
  rigid-formation experiment — do not resurrect it.
- Docs: `docs/FULL_STRATEGY.md` (whole strategy), `docs/CHANGELOG.md`,
  `docs/strategies/*.md` (one file per version), `docs/ONLINE_TESTING.md` (workflow),
  `AGENTS.md` (authoritative working notes).

Commands:

```
cambc build apex                                  # compile the Rust bot
cambc run apex <opponent-bot> --map <map>         # one local game
python -X utf8 scripts/panel.py <bot> --opps apex22 titan --jobs 4   # broad local gate
cambc submit apex                                 # upload as new platform version
cambc submissions list / activate <n>             # check / pin live version
cambc match-groups create <OPPONENT_TEAM_ID>      # queue 5 online games
cambc match-groups quota --json                   # quota + opponent ranks
cambc matches summary <MATCH_ID> --json           # download one result
```

## 2. Game facts the bot must respect

- Win: first to tribute 1,000 gems, else most gems at round 2,000 (tiebreakers: gold,
  kills, then Team B).
- Killer steals the victim's carried gems (PvP). Camp kills DESTROY carried gems.
- Recall: 5 owner turns (3 with a Home emblem), cancelled by damage/stun, keeps gems,
  heals to full on spawn.
- Tribute: ceil(gems/10) owner turns, NOT cancelled by damage; cancelled by stun,
  death, or a new altar lock on that altar.
- Teleport crystal: 3-tile blink after a 3-turn channel; ignores terrain and damage
  but NOT stuns/death; cannot be cancelled; not a return-home item.
- Prism passive: +1.5 Focus per carried gem (40 gems = +60 Focus on base 80).
- Ryth: gains Strength = 1% of bonus health; ground-targeted AoE stun (range 4).
- Cassi & Issac share death (both die, both lose gems, one kill reward).
- Vision is NOT shared; only 8 shared-memory bytes per match.
- Camps attack the nearest champion, never chase, sleep after 2 quiet rounds; capture
  by standing on a spawn tile 5 rounds uncontested; reward split among capturers.
- Respawn takes 60 rounds. Dead champions can still shop.

## 3. Strategy ideas to implement (user's requests)

1. **Anti-splitting / selective regrouping.** Champions should stay near each other
   so they don't get chased down alone. Group up only when enemies are seen or
   teammates die; escort carriers to altars. Do NOT use a rigid whole-team tether —
   that was built and rejected (19/280). v24's guarded alert/escort is the current
   implementation; improve it, don't replace it blindly.
2. **Tribute sooner.** Large hauls before banking are wasteful and risky. Current
   v22/v24 limits: 30/15/5 gems (normal / altar within 15 / within 4); 15/8/5 when
   threatened. These may be tuned per map.
3. **Protected Prism carry (big idea).** Build Prism with health so she survives
   holding many gems (her passive turns gems into Focus/damage). Other champions
   health-stack too, stay beside her, and protect her. When the frontline is about
   to fail, Prism retreats early: break contact, then Home-assisted recall
   (3 ticks, keeps gems) or a teleport crystal for a 3-tile terrain escape.
   Escorts cover until she is actually safe; only sacrifice an escort if it buys her
   escape — each death feeds the enemy 100 gold plus the escort's gems.
   Cap the gem reserve; bank when threatened, when a tribute wins, or late game.
   Tributing removes the Focus bonus — holding vs banking is the core tradeoff.
   Full spec: `docs/strategies/prism-carry-plan.md`.
4. **Focus fire.** Coordinated attacks on the same target, prioritizing enemies with
   high health/damage. Byte 6 already carries a shared focus target — improve its
   selection (e.g., prefer targets we can actually kill soon, not just the closest).
5. **Finish low-health enemies.** If a kill is confirmed (target HP <= one of our
   hits, no stun/retaliation risk), take the hit even when below retreat health.
   A prototype landed 6 finishing kills but scored 4/10 — needs tighter gating and
   measurement, not blind enabling.
6. **Map-specific strategies.** Use map-aware profiles, not one universal policy:
   symmetric maps → commit to one side; center-gem maps → contest the center instead
   of farming edges; forced-brawl maps (`00the_line`, where v22 went 1/25 vs top-20)
   need combat-first play; open farming maps (`00expanse`, where we went 5-0) should
   keep current farming. Build per-map overrides behind a map-id switch.
7. **Melee + ranged combos.** High-health melee (Ryth) tanks in front; ranged
   (Vesper, Tavi, Prism, Marcella) attack from behind. When the frontline dies,
   ranged units retreat unless a kill is confirmed.
8. **Spawn bait (situational).** On suitable maps: an injured, empty-handed champion
   lures a hunter toward healthy allies near our spawn, then escapes to heal while
   the hidden teammates counter. Do NOT rely on the bait dying — respawn is 60
   rounds. Short commitment window; abandon if the enemy doesn't chase.
9. **Concentrate rewards.** Capture rewards go to champions in the capture area —
   allies can clear a camp then step off capture tiles so the chosen carry (e.g.,
   Prism) takes the whole reward. Abandon this if it delays a contested capture.

## 4. Suggested additions (assistant's own ideas)

- Keep v24's guarded substrate and change ONE thing per version so results are
  attributable. Freeze each candidate under `bots/<name>` and save the diff.
- Shared byte 7 in v24: gate flags (bits 0-1), support-leader slot (bits 2-4),
  alert generation (bits 5-7). Bytes 0-5 are per-champion claims (bankers/recovering
  champions can temporarily publish altar/spawn fields). Byte 6 is the focus target.
  Do not clobber these fields — there was a real bug where cached byte-7 writes
  stomped each other.
- Track per-change metrics: wins, submitted gems, deaths, kills, carried-gem loss,
  fuel-exhaustion events, bot faults. Zero faults is necessary, not sufficient.
- For the finish-kill gate: require target HP <= our hit, no nearby unseen stun
  threat, and our carried gems low enough that dying for the trade is acceptable.
- Deterministic A/B: same map, same side, same opponent bot, same seed.
- Watch for the known deadlock class: an escort waiting at exactly the distance its
  leader is forbidden to exceed (already fixed once — keep the regression tests).
- Ryth is a strong frontline candidate: health stacking also raises his Strength.

## 5. Hard rules (non-negotiable)

- At least **5 completed online games on a fixed version** before any further
  gameplay tweak. Preserve every game including losses and faults.
- New unranked challenges: **only teams currently ranked top-20**, rechecked
  immediately before each create call. Quota: 50 outgoing five-map groups/hour
  (one group = one quota slot). Never blindly retry an uncertain create.
- Local gate before online: focused 12-game panel (6 maps, both sides) plus the
  broad 140-game gate vs `apex22` and `titan`. A candidate needs evidence, not just
  "no faults," before promotion. Local wins alone do not prove an online improvement
  (guarded went 50/140 locally).
- Never change the live pinned version without an explicit submit + activate, and
  record the submission ID in `docs/CHANGELOG.md` and `AGENTS.md`.
- Write/update `docs/strategies/<version>.md` for every version: changes, strengths,
  weaknesses, test results. Update `docs/FULL_STRATEGY.md` and `docs/CHANGELOG.md`.
- No claimed improvements without numbers. Per-match submission attribution is not
  available from the platform — say "attribution unverified" when relevant.

## 6. Suggested iteration order

1. First: 5+ online games of the CURRENT live v24 vs top-20 opponents; download,
   analyze, and save the baseline report (the runner exists: `scripts/top20_panel.py`,
   `scripts/analyze_top20_panel.py`).
2. If v24 looks worse than the saved v22 top-20 baseline (1/25), diagnose why before
   touching code — check whether alerts fire too often or leaders pick wrong goals.
3. Implement the Prism carry as an isolated map-gated candidate (`bots/prism`),
   with capped reserve, Home emblem, escort rotation, and early retreat.
4. Implement the finishing-kill gate separately, measuring finishing kills landed.
5. Only then attempt map-specific profiles and the spawn-bait tactic.
6. Promote or roll back with an evidence table: wins/gems/deaths/kills/faults vs the
   saved baseline on the same opponents/maps/sides.
