# Full strategy (apex) - compact reference

Current live implementation: **v24 guarded support** (experimental, released at the user's explicit request; no online v24 results yet), source bots/apex. Sections 0-14 below describe the inherited v22 behavior (**[v20]** inherited baseline, **[v21]** rejected ward experiment, **[v22]** banking change, **[plan]** future work); v22 is the preserved rollback baseline. Section 17 lists what v24 overrides: the shared-byte-7 control layout, the alert and the escort behavior. The v23 grouping trial and the rigid cohesion experiment are archived and not active. [Results and provenance](online-cycle-20261027.md).
Base: titan (user's Rust bot, v19), extended as apex. Code: `bots/apex/src/`.

---

## 0. Game facts the strategy is built on

- **Win:** first to tribute 1,000 gems, else most gems at round 2,000 (then lifetime gold, then kills; full tie = Team B).
- **Camps:** wake when hit, attack the **nearest** champion, never chase, sleep after 2 rounds with nobody in range, keep their damage while asleep.

  | Camp | HP | Damage | Range | Gems | Gold |
  | --- | --- | --- | --- | --- | --- |
  | Wolf | 1,350 | 20 | 3 | 4 | 40 |
  | Elk | 2,400 | 60 | 4 | 15 | 90 |
  | Golem | 5,000 | 120 | 4 | 36 | 160 |
  | Monolith | 20,000 | 200 | 5 | 200 | 300 |
  | Gem cluster | 120 | 0 | – | 7 | 0 |
  | Gold cluster | 120 | 0 | – | 0 | 20 |

- **Capture:** after the whole group dies, stand on one of its tiles for 5 rounds uncontested. The reward splits between allies standing there. Occupied tiles delay the respawn.
- **Tribute:** stand next to an altar. Takes ceil(gems/10) turns. Damage does not stop it; stuns, death and altar locks do.
- **Death:** a champion kill gives the killer all carried gems plus 100 gold; a camp kill destroys them. 60-round respawn.
- **Recall:** 5 turns; any damage or stun cancels it.
- **Vision:** 8 tiles each, plus your own ward; not shared. Shared memory is only 8 bytes.
- **Fuel:** 100k per turn; running out suspends the turn mid-action.

## 1. Draft  [v20]

| Picks | Order |
| --- | --- |
| 3–4 | Vesper, Marcella, Ryth, Tavi (Willow) |
| 5 | Willow, Vesper, Ryth, Tavi, Marcella |

- Roles: Ryth and Marcella are 1,200-HP melee anchors. Vesper (+33% gold) and Tavi (shops anywhere, stun) are ranged damage. Willow heals.
- Tested and rejected: Vendetta on small maps (4–12), Cassi & Issac everywhere (52–88).

## 2. Turn order (every champion, every turn)

1. Read shared memory; note teammate deaths.
2. **Dead:** shop, drop the claim.
3. **Channelling** (tribute/recall/teleport): while tributing, cancel if nearby enemies would kill us first, unless this tribute wins the game.
4. **Sense:** visible enemies (last sighting per enemy, a 60-round sighting list), allies, occupied tiles.
5. **Shop:** on spawn, or anywhere for Tavi. Plan a shopping trip when gold ≥ max(150, 6 × distance home), with no enemies, under 25 gems carried, more than 300 rounds left, and 40+ rounds since the last trip.
6. Decide, in priority order: **Heal → Fight → Bank → Farm**.
7. Heal allies (Willow). Personal ward placement and v23 regrouping are disabled in the retained v22.
8. Stuck guard: 6 turns with no action means skip that altar for 40 rounds, or that camp for 30 if it is more than 6 tiles away.
9. Spend leftover fuel precomputing distance maps.

## 3. Farming (job choice)  [v20]

Each champion claims one camp group in shared memory and scores every group:

- **score = value / time / n**, where n = champions on the group including me.
- **value** = gems + gold × w, with w = 0.15 before round 300, 0.08 before 800, 0.03 after.
- **time** = travel + respawn wait + clear time + HP cost / n + 6.
  - Clear time = group HP / (my damage × n).
  - Respawn wait: groups returning in more than 25 rounds are skipped.
  - HP cost = expected damage taken (most dangerous camps killed first) / (60% of max HP) × (6 + distance spawn → camp). Each lost "bar" of HP is a trip home.
- **Harmless groups** (clusters) chain: up to 6 harmless neighbours within 5 tiles are added to value and time.
- **Join caps:** a harmless group takes ceil(HP/700) champions (1–5); a dangerous group takes 4. Jackpots have no cap. So dangerous camps attract helpers and harmless ones spread the team.
- **Multipliers:**
  - × 0.4 (× 0.75 after round 250) on the enemy's side of the map;
  - × 0.6 where 2+ enemies were seen in the last 40 rounds;
  - × 0.5 within 8 tiles of where we died in the last 120 rounds;
  - × 1.25 for the current job, to stop flip-flopping.
- Re-chosen every 5 rounds. When a group is respawning, step off its tiles and choose again.

## 4. Fighting camps  [v20]

- **Target:** lowest HP-per-damage first (killers first), adjusted for Varg's splash, plus distance. Melee goes adjacent; ranged keeps its full range so the melee stays nearest.
- **Spells:**
  - damage on the target;
  - stun on the most dangerous awake camp;
  - area damage on the biggest cluster;
  - shield when a camp is hitting us.

  Attack-reset spells fire straight after a basic attack.
- **Monolith-gated altars** (every altar walled by a camp, e.g. boss_battle, guardians):
  - the team hoards gems;
  - from round 200 or 60 gems, a flag in byte 7 starts the assault;
  - champions gather (min(alive, 3) within 9 tiles, or wait up to 60 rounds), kill the gate camp together, then bank.

## 5. Capturing  [v20]

- **Normal group:** only the nearest champion captures (Marcella within 8 takes priority); the rest move on.
- **Jackpot** (≥ 60 gems and ≥ 35% of the map's gems, e.g. the_line's 161/193): every champion within 12 tiles stands on it. The reward splits, the team stays together, and it banks together.
- **Contested:** go remove the enemy squatter. If it is out of sight on a long group, walk toward the tiles we can't see.
- **Timeout:** 40 rounds. Then skip the group for 100 rounds (a jackpot for only 5). Step off the tiles once captured.

## 6. Banking

- **Altar choice:** nearest by walking distance. +12 if enemies were seen near it in the last 40 rounds. Skip altars blocked by the stuck guard. If no altar is reachable, cut through the camps in the way.
- **Never bank** while capturing or while the monolith gate is shut.
- **Endgame:** always bank when banked + carried ≥ 1,000, or after round 1,900.

| Version | Bank when carrying |
| --- | --- |
| [v20] | >=60 anywhere; >=40 when altar distance <=18; >=10 when distance <=4. Marcella/careful:40/20/10. |
| [v22] normal | >=30 anywhere; >=15 when altar distance <=15; >=5 when distance <=4. |
| [v22] threatened/Marcella | >=15 anywhere; >=8 when altar distance <=15; >=5 when distance <=4. |

Altar distance is the path-distance estimate plus the existing danger penalty, not just geometric separation. Heal/fight decisions and capture/gate exclusions still precede banking.

**Threatened** = an enemy seen within 14 tiles in the last 40 rounds, a teammate died in the last 100, or below 60% HP. Marcella always counts as threatened (she earns 2 gold per gem tributed).

## 7. Fighting champions  [v20]

- **Relevant enemies:** within 10 tiles, ignoring enemies on their own spawn unless they are hitting us.
- **Kill-time model:**
  - our time to kill them = their total HP / (my damage + allies within 8);
  - their time to kill us = our total HP / their damage.
  - **Losing** = ours is more than 1.3× theirs. **Clearly losing** = more than 1.6×, or outnumbered within 6 tiles.
  - Careful mode (3+ team deaths in 150 rounds) uses 1.0 / 1.3; carrying 30+ gems makes "clearly losing" 1.0.
- **Enemy more than 7 tiles away:** leave if losing. On brawl maps, go after them if not losing.
- **Target:** the enemy in reach that dies fastest. Gem carriers are preferred; the team's focus target counts ×0.3 (shared memory byte 6).
- **Retreat** when:
  - in danger (HP < 2.5 × incoming damage + 10%), or
  - clearly losing and they are close,

  unless we can finish the target, or a teammate is within 3 tiles and it isn't clearly lost. Never run from an adjacent melee champion while we can hit back.
- **Join** a teammate's fight within 7 tiles (10 on brawl maps). Engage enemies within 5 tiles (8 on brawl maps) when not losing.
  - Ranged champions wait up to 6 turns for the enemy to walk into range.
  - On brawl maps, also chase hurt enemies (below 45% HP).
- **Spells:**
  - damage, stun or area damage on the target;
  - shield when they are within 2 tiles;
  - damaging dash (Heart of Ruin) next to the target.
- **Brawl map** (a harmless jackpot holding ≥ 50% of the map's gems, e.g. the_line, vault): the team plays aggressively all game.

## 8. Retreat and healing  [v20]

- **Retreat triggers:**
  - HP < 15%;
  - HP < 20% with no enemy in reach;
  - HP can't survive walking out of camp range;
  - HP < 30% (45% in careful mode) with no enemy near and not capturing.
- **Flee:** search up to 7 steps for the best tile outside every threat range, preferring home and allies. Recall if fleeing makes no progress for 3 turns and nothing hits us.
- **Bank on the way** if an altar is within 3 tiles.
- **Once safe:** recall when more than 6 tiles from spawn, otherwise walk home avoiding threats. Heal on spawn to 97%, hitting anything that comes in range meanwhile.

## 9. Items

- **[v20] builds** (buy at spawn; Tavi anywhere):

  | Role | Champions | Opening emblems |
  | --- | --- | --- |
  | Fighter | Vesper, Tavi, Willow, others | Monster Str, Jungle HP, Durability HP |
  | Tank | Ryth, Ren, Heart of Ruin | Jungle HP, Monster Str, Durability HP |
  | Caster | Marcella, Cassi, Stellar, Prism | Durability HP, Monster Focus |

  Then Bruiser of the main stat, with every 4th emblem HP.
- **Engine item values** (one emblem = 5 shards = 150 g):

  | Family | Stats | Passive |
  | --- | --- | --- |
  | Power | 6 main | none |
  | Bruiser | 5 main + 1 + 1 | none |
  | Monster | 5 | +15% damage to camps |
  | Jungle | 5 | −30% damage from camps |
  | Durability | 5 | −10% damage taken |
  | Treasure | 5 | +10% gold |
  | Capture | 5 | captures ~2 rounds instead of 5 |
  | Prospector | 5 | ~+1 gem on cluster captures |
  | Home | 5 | recall −50% |
  | Greed | 35 per 750 g | none |
  | Tribute / Hunter / Skirmish / Collectors | 5 | effects unknown |

- **[plan]** Opening, then Capture + Prospector (tested 75–65), then test Power against Bruiser and add Treasure. Ascendance stacks Power and owns one Capture and one Prospector each.

## 10. Personal wards (rejected v21 experiment)

This describes the tested ward behavior; it is disabled in retained v22.

When the ward is ready:
- next to an altar we are standing by (carriers get ambushed at altars);
- otherwise, if our ward is more than 8 tiles behind us, on the reachable tile within 2 tiles closest to the enemy spawn.

Ward vision feeds the sighting list, which drives job avoidance, altar choice, "threatened" and fight decisions.

## 11. Movement and fuel  [v20]

- Static distance maps (to each camp group, altar and spawn) are computed on the host and copied into wasm memory. Lookups cost a few fuel instead of hundreds.
- Dash along a map when travelling more than 6 tiles with no enemies around.
- Local one-step scoring for fights and positioning.
- Precompute distance maps only with spare fuel; job scoring stops early when fuel is low.

## 12. Shared memory map (8 bytes)

| Byte | Meaning |
| --- | --- |
| 0–5 | Camp group claimed by each champion slot (group + 1; 0 = none) |
| 6 | Team focus target (enemy index + 1) |
| 7 | Monolith-gate flags (bit 0 assault on, bit 1 gate camp dead) |

## 13. Roadmap (see `PLAN.md`)

The v23 formation experiment is documented in [apex-v23](strategies/apex-v23.md) and archived in bots/apex23 after 3/10 online wins. The following grouping goals are future work, not active behavior.

- **[plan] Pairs:** melee anchor + ranged partner (Ryth + Vesper, Marcella + Tavi; Willow follows whoever is most hurt; three picks play as one trio).
  - Camps choose the nearest champion; enemy bots choose their own targets. The melee partner cannot force opponents to attack it.
  - Shared job: the partner copies the anchor's claim.
  - Capture together, bank together; the partner stays within 3 tiles.
  - Stun chains on one target (Ryth's area stun, Marcella's enhanced stun, Tavi's stun); escort whoever is banking.
- **[plan] Altar war:**
  - buy one altar lock each;
  - place it on an altar where an enemy is tributing (cancels the tribute);
  - skip or break enemy-locked altars;
  - escape with a teleport crystal when cornered.
- **[plan]** Item build above, fuel-stall fixes, stop fighting camps while hurt and under pressure.

## 14. Testing and changelog

- Complete and analyze **at least five online matches on one fixed version before each strategy tweak**. After implementing and locally verifying a candidate, complete at least five candidate online matches before the next tweak. Queued games and local simulations do not count.
- Opponent policy: new unranked challenges must target a team currently ranked 1-20, rechecked before each request (this supersedes the earlier +/-200 rating-band rule, kept in the history). Confirm the live submission before queuing and retain match IDs, side, map, outcome and version-attribution evidence.
- Track carried-gem loss, tribute size/count, deaths, economy, wards, fuel exhaustion and bot faults alongside wins. Treat unverified mechanisms as hypotheses.
- Use focused local regressions and broader panels when a specific risk warrants them. The former 52% local screen is not proof of improvement; related variants and maps are correlated.
- Keep [CHANGELOG.md](CHANGELOG.md), the candidate document and this reference current. Exact workflow and current blocker: [ONLINE_TESTING.md](ONLINE_TESTING.md).

## 15. Map-specific strategy investigation

Current gameplay is v24 (v22 plus guarded support, see section 17). The old five-peer per-map campaign is CLOSED to dispatch (195/350 results saved). The top-20 runner now supports a 70-map campaign, but only the 25 top-20 baseline games have run so far; 70-map coverage is deferred under the user's urgent-release direction, and nothing is currently measuring all 70 maps. The protocol respects the official 50 match-group slots per hour (five games per slot) and preserves sources/results across restarts. See [MAP_CAMPAIGN.md](MAP_CAMPAIGN.md) for the design and [MAP_MATRIX.md](MAP_MATRIX.md) for coverage and per-map worksheets. Those worksheets contain evidence and candidate investigations, not automatically validated gameplay changes.

## 16. LOCAL EXPERIMENT: whole-team cohesion (REJECTED, not submitted)

Everything above describes v22 (inherited by live v24, with section 17 overrides). bots/cohesion is a separate rejected LOCAL candidate; it is not live and has not been shown to be better. See [strategies/cohesion-local.md](strategies/cohesion-local.md).

- A stable elected leader publishes a shared rally position and one shared camp objective (six-member claimant mask) in the same 8 shared bytes, alongside combat focus and gate flags.
- Followers regroup when farther than 2 tiles from the rally point. Healthy movement normally cannot increase spacing beyond 3, with a bounded margin of 4 after 3 idle turns. Emergency healing/fleeing is exempt.
- Banking and recovery trips are coordinated; empty escorts keep altar-adjacent tiles clear for the carrier.
- Followers share the leader's job. Camp scoring uses the actual nearby party's damage for every candidate camp. Travel dashes are disabled while more than one ally lives.
- Draft, items and tribute limits are unchanged.
- Weaknesses: grouped farming costs, congestion and possible extra recovery trips. Selected-map results do not establish general superiority.

## 17. v24 guarded support (live, experimental)

v24 is v22 plus guarded support (bots/apex; platform submission `758c6fd5-4884-4477-91ed-78f2b61f2e59`; Live:24 Selected:24, Mode: PINNED VERSION). Individual farm claims stay, and a short alert (seen enemies or recent allied deaths) makes distant followers close to within 3 tiles of a support leader, who is preferably a living banking carrier. There is no hard movement veto and no shared recall; banking, captures and combat retreat keep priority, empty escorts clear altar neighbors, and jobs near the leader's intent are favored. Shared byte 7 now carries gate flags (bits 0-1), the support-leader slot (bits 2-4) and the alert generation (bits 5-7), overriding the layout in section 12. Claim bytes 0-5 can temporarily publish an altar field while banking or the spawn field while recovering; shared combat focus remains in byte 6. Travel dashes are disabled while an alert is active. Draft, items and tribute limits are unchanged. It aims to protect carriers, at a possible farming cost.

Release status: v24 guarded support is live at the user's explicit request for immediate publication before their Devin weekly quota runs out. Experimental release: local 50/140 against apex22, three WASI protocol tests passed, zero faults across the full 140-game gate; no online candidate results yet. v22 is the preserved rollback baseline. Next gameplay tweak must follow at least five completed v24 online matches, all new opponents currently top20. Details: [strategies/guarded-local.md](strategies/guarded-local.md). A proposed (not implemented) Prism carry idea: [strategies/prism-carry-plan.md](strategies/prism-carry-plan.md).
