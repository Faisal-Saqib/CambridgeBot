# Top-20 scouting and per-map targeting plan (plan only — not started)

Goal: download real matches played by the current top-20 teams from the platform,
extract each team's strategies, rank strategy points by how many teams use them,
and produce 10 strong target points for each map. No bot changes and no unranked
match creation in this plan — it is read-only observation (zero match quota cost).

Prior work this extends: `docs/TOP_TEAM_FINDINGS.md` sampled only ranks 1–3 on
6 maps (18 observations, 15 games). This plan scales that to all top-20 teams and
all published maps, and adds a prevalence ranking.

## Phase 1 — Capture the ladder (internet)

- `cambc teams list --limit 25 --json` (or the ladder endpoint used earlier;
  captured once before at `matches/top-team-study-20261028/ladder-top25.json`).
- Freeze ranks 1–20 with team IDs, names, ratings and a UTC timestamp.
- Recheck the ladder once at analysis time and note any rank drift.

## Phase 2 — Download matches (internet, the bulk of the work)

Per team (20 teams):

- `cambc matches list --team <TEAM_ID> --kind ranked --limit 100 --json`
  → the team's recent ranked match list (opponent, map, side, result).
- For map coverage gaps, `cambc matches list --team <ID> --kind ranked
  --map <MAP_ID> --limit 5 --json` (same fallback the existing
  `scripts/fetch_top_team_study.py` uses).
- `cambc matches summary <MATCH_ID> --json -o <file>` per selected match —
  this is the detailed capture with kills, captures, purchases, tribute events,
  diagnostics. Assert `detailedCaptureComplete` before using a file.
- `cambc matches download <MATCH_ID>` only for a small set where summaries lack
  what we need (position traces for spacing analysis); replay bundles are heavy.

Rate-limit handling (proven in `fetch_top_team_study.py`): wrap every call with
retry on 429/"peer disconnected"/timeout, honour `retry after N`, 3s spacing
between calls, and log every request to `matches/top20-scout/requests/` so the
run is resumable and auditable. Downloading uses no match quota.

Sampling cap to keep it bounded: latest 3 finished ranked games per team per map
for the 10 target maps first (~600 summaries worst case), then extend to all 70
maps at 1 game per team per map (~1,400). If volume is too high, reduce to the
20 maps that appear most in top-20 recent lists first.

## Phase 3 — Strategy extraction (local analysis of downloaded data)

Extend `scripts/analyze_top_teams.py` into `scripts/strategy_census.py` that
scores each team's match for measurable strategy signatures:

- Carry concentration: top earner's share of team gold/damage (Ad Astra pattern:
  Vesper 64–74%).
- Group fighting: attackers credited per kill; fights near vs far from allies.
- Capture style: single-recipient vs multi-recipient capture events.
- Tribute timing: average gems per tribute; tribute under pressure.
- Carrier protection: escort proximity before tribute (needs replay check on a
  sample).
- Draft composition: C&I usage (5-body drafts), melee+ranged balance.
- Item families: Jungle/Home/Bruiser/etc. spend shares; Strength vs Focus focus.
- Consumables: wards, altar locks, teleport crystals per game.
- Aggression: kills/deaths, champion damage share vs camp damage.
- Camp discipline: deaths to camps, contested-capture attempts.
- Split-vs-grouped farming: simultaneous distinct objectives (replay sample).

## Phase 4 — Prevalence ranking (deliverable A)

`docs/TOP20_STRATEGY_CENSUS.md`: for every strategy point above, a table like
"single-recipient captures: used by N/20 teams (evidence: match IDs)". Points
ordered by number of teams using them — the user-facing deliverable. Distinguish
"common AND winning" from "common but mediocre" using each team's win rate with
the pattern.

## Phase 5 — Per-map target points (deliverable B)

For each published map, extend `docs/maps/<map>.md` with a "10 target points"
section built from three inputs:

- Map facts: layout, gem distribution (center vs edges), terrain barriers, altar
  positions, disconnects needing crystals, camp group sizes — from `maps/*.map26a`
  plus existing findings docs.
- Top-20 behaviour on that map specifically: which Phase-3 patterns correlate
  with wins there (e.g., The Line winners fight as 4-5; Expanse winners solo-farm
  fast).
- Our recorded weaknesses: MAP_MATRIX results, v22's 1/25 top-20 baseline maps
  (The Line, Anvil, Stampede, Starfish), guarded panel losses per map.

Each point must be actionable for our bot (a draft choice, routing rule, combat
rule, or tribute rule) — not vague. Priority: the 6 heavily-played maps first,
then the rest.

## Phase 6 — Report and handoff

- Update `docs/TOP_TEAM_FINDINGS.md` with the census summary; keep the old 3-team
  section as historical.
- Feed ranked strategy points into the version roadmap in `docs/PLAN.md` /
  `docs/HANDOFF_PLAN.md` (each future candidate cites its prevalence evidence).
- No bot code changes inside this plan.

## Constraints and caveats

- Read-only: zero match-group quota used; only API read rate limits matter.
- Historical submission IDs are unavailable — a downloaded match shows which team
  played, not which bot version; note this in every conclusion.
- Ranks/ratings are capture-time values.
- Summaries may not contain full position traces; if spacing analysis needs them,
  download replay bundles for a small subset only.
- All raw downloads, request logs, the frozen manifest and input hashes are
  preserved under `matches/top20-scout/` for audit.

## Execution checklist (when approved)

1. Verify `cambc` works and capture `ladder-top25.json` fresh.
2. Write `scripts/top20_scout.py` (resumable: manifest + requests/ + summaries/).
3. Download Phase 2 sample; verify a few summaries by hand.
4. Write `scripts/strategy_census.py`; produce the census table.
5. Produce per-map 10-point lists (6 priority maps → all 70).
6. Update findings docs; stop — promotion decisions are a separate step.
