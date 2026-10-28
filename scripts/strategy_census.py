#!/usr/bin/env python3
"""Extract measurable strategy signatures from downloaded top-20 match summaries.

Reads matches/top20-scout/summaries/*.json plus the frozen manifest, and emits
per-match/per-team features and a cross-team prevalence table. Deterministic
and offline: never calls cambc.
"""
import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / "matches" / "top20-scout"
CARRY_GOLD_SHARE = 0.50
DAMAGE_SHARE = 0.60
SINGLE_CAPTURE_SHARE = 0.80
GROUP_KILL_ATTACKERS = 3.0
SMALL_TRIBUTE_GEMS = 25.0
EARLY_KILL_ROUND = 200
TIGHT_SPREAD_TILES = 8.0
ITEM_FAMILIES = ("Durability", "Jungle", "Prospector", "Capture", "Collector",
                 "Monster", "Treasure", "Home", "Bruiser")
ITEM_STATS = ("Strength", "Focus", "Health")


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def entries(data, kind):
    for event in data["events"]:
        if event["kind"] == kind:
            for entry in event["entries"]:
                yield event["owner"], entry


def item_family(name):
    for family in ITEM_FAMILIES:
        if name.startswith(family + " "):
            return family
    return "Other"


def item_stat(name):
    for stat in ITEM_STATS:
        if name.endswith(" " + stat) or (" of " + stat) in name:
            return stat
    return "Other"


def team_side(draft, champion):
    return champion["team"]


def analyze_match(data, observed_names):
    """Per-team feature rows for the top-20 teams observed in this match."""
    champions = data["champions"]
    teams = sorted({c["team"] for c in champions})
    rows = {}
    kills_of = {t: [] for t in teams}      # (round, victim_id, killer_id)
    deaths_of = {t: Counter() for t in teams}
    gem_loss = {t: 0.0 for t in teams}
    captures = {t: defaultdict(set) for t in teams}   # (round, group) -> owners
    clear_pts = {t: defaultdict(list) for t in teams} # round -> [(x,y)]
    tributes = {t: [] for t in teams}
    wards = {t: 0 for t in teams}
    buys = {t: Counter() for t in teams}     # family -> count
    buy_stats = {t: Counter() for t in teams}
    consumables = {t: Counter() for t in teams}
    assists = {t: defaultdict(set) for t in teams}  # (round, victim) -> assister ids

    for owner, e in entries(data, "kill"):
        kills_of[owner["team"]].append(
            (e["timestamp"]["round"], e["target"].get("id"), owner["id"]))
    for owner, e in entries(data, "death"):
        deaths_of[owner["team"]][e.get("context", "?")] += 1
    for owner, e in entries(data, "assist"):
        assists[owner["team"]][(e["timestamp"]["round"], e["target"].get("id"))].add(
            owner["id"])
    for owner, e in entries(data, "gemLoss"):
        gem_loss[owner["team"]] += num(e.get("amount") or e.get("value"))
    for owner, e in entries(data, "gemCollection"):
        if e.get("context") == "campGroup":
            key = (e["timestamp"]["round"], e["target"].get("id"))
            captures[owner["team"]][key].add(owner["id"])
    for owner, e in entries(data, "campClear"):
        clear_pts[owner["team"]][e["timestamp"]["round"]].append((e.get("x"), e.get("y")))
    for owner, e in entries(data, "gemSubmission"):
        amount = num(e.get("amount"))
        if amount <= 0:
            amount = num(e.get("value"))
        tributes[owner["team"]].append(amount)
    for owner, e in entries(data, "wardPlacement"):
        wards[owner["team"]] += 1
    for owner, e in entries(data, "buyItem"):
        buys[owner["team"]][item_family(e["target"]["name"])] += 1
        buy_stats[owner["team"]][item_stat(e["target"]["name"])] += 1
    for owner, e in entries(data, "itemCombination"):
        buys[owner["team"]][item_family(e["target"]["name"])] += 1
        buy_stats[owner["team"]][item_stat(e["target"]["name"])] += 1
    for owner, e in entries(data, "buyConsumable"):
        consumables[owner["team"]][e["target"].get("name", "?")] += 1

    # attacker counts per kill: killer + credited assists at same round/victim
    attackers = {t: [] for t in teams}
    for t in teams:
        for rnd, victim, killer in kills_of[t]:
            attackers[t].append(1 + len(assists[t].get((rnd, victim), ())))

    rounds = max(1, data["match"]["roundsCompleted"])
    outcome = data["match"]["outcome"]
    draft = data.get("roster", {}).get("draft", [])
    draft_by_team = {t: [d["champion"] for d in draft if d["team"] == t] for t in teams}
    bodies = Counter(c["team"] for c in data.get("roster", {}).get("champions", []))

    for t in teams:
        ours = [c for c in champions if c["team"] == t]
        earned = [num(c["metrics"]["earnedGold"]) for c in ours]
        damage = [num(c["metrics"]["championDamageDone"]) for c in ours]
        caps = list(captures[t].values())
        kill_rounds = [r for r, _, _ in kills_of[t]]
        spread_samples = []
        for rnd, pts in clear_pts[t].items():
            pts = [(x, y) for x, y in pts if x is not None]
            if len(pts) >= 2:
                dists = [math.dist(a, b) for i, a in enumerate(pts) for b in pts[i + 1:]]
                spread_samples.append(sum(dists) / len(dists))
        tribs = [v for v in tributes[t] if v > 0]
        submitted = sum(tribs) if tribs else num(
            next((x["submittedGems"] for x in data["teams"] if x["team"] == t), 0))
        row = {
            "won": outcome == t,
            "bodies": bodies.get(t, 0),
            "draft_size": len(draft_by_team.get(t, [])),
            "draft": draft_by_team.get(t, []),
            "kills": len(kills_of[t]),
            "deaths": sum(deaths_of[t].values()),
            "deaths_to_camps": deaths_of[t].get("camp", 0),
            "early_kills": sum(1 for r in kill_rounds if r <= EARLY_KILL_ROUND),
            "attackers_per_kill": (sum(attackers[t]) / len(attackers[t])
                                   if attackers[t] else None),
            "submitted": submitted,
            "tributes": len(tribs),
            "tribute_mean": submitted / len(tribs) if tribs else None,
            "gem_loss": gem_loss[t],
            "top_gold_share": (max(earned) / sum(earned)) if sum(earned) else 0.0,
            "top_damage_share": (max(damage) / sum(damage)) if sum(damage) else 0.0,
            "captures": len(caps),
            "single_captures": sum(1 for s in caps if len(s) == 1),
            "farm_spread": (sum(spread_samples) / len(spread_samples)
                            if spread_samples else None),
            "wards": wards[t],
            "item_families": dict(buys[t]),
            "item_stats": dict(buy_stats[t]),
            "consumables": dict(consumables[t]),
            "healing_done": sum(num(c["metrics"]["healingDone"]) for c in ours),
            "rounds": rounds,
        }
        rows[t] = row
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=FOLDER / "census.json")
    args = parser.parse_args()

    manifest = load(FOLDER / "manifest.json")
    observed = {mid: e["observed_teams"] for mid, e in manifest["selection"].items()}
    ladder = load(FOLDER / "ladder.json")
    top20 = {t["name"]: t for t in ladder["teams"] if t["rank"] <= 20}
    name_by_id = {t["teamId"]: t["name"] for t in top20.values()}

    matches = sorted((FOLDER / "summaries").glob("*.json"))
    games = []
    skipped = 0
    for path in matches:
        mid = path.stem
        data = load(path)
        if not data.get("diagnostics", {}).get("detailedCaptureComplete"):
            skipped += 1
            continue
        meta = manifest["selection"].get(mid, {}).get("match", {})
        map_name = meta.get("map") or meta.get("mapName")
        id_to_name = {t["teamId"]: name_by_id.get(t["teamId"]) for t in meta.get("teams", [])}
        rows = analyze_match(data, observed.get(mid, []))
        for side, row in rows.items():
            # attribute the side to a top-20 team via match teams
            team_id = next((t["teamId"] for t in meta.get("teams", [])
                            if t["side"].lower() == side[-1].lower()), None)
            team_name = id_to_name.get(team_id)
            if team_name not in top20:
                continue
            games.append({"match": mid, "map": map_name, "team": team_name,
                          "rank": top20[team_name]["rank"], "side": side, **row})
    print(f"Analyzed {len(games)} team-games from {len(matches)} summaries "
          f"({skipped} skipped)", flush=True)

    def feature_flags(g):
        flags = set()
        if g["top_gold_share"] >= CARRY_GOLD_SHARE:
            flags.add("carry_gold_concentration")
        if g["top_damage_share"] >= DAMAGE_SHARE:
            flags.add("carry_damage_concentration")
        if g["captures"] and g["single_captures"] / g["captures"] >= SINGLE_CAPTURE_SHARE:
            flags.add("single_recipient_captures")
        if g["attackers_per_kill"] and g["attackers_per_kill"] >= GROUP_KILL_ATTACKERS:
            flags.add("group_kills_3plus")
        if g["tribute_mean"] and g["tribute_mean"] < SMALL_TRIBUTE_GEMS:
            flags.add("small_tributes")
        if g["early_kills"] >= 3:
            flags.add("early_aggression")
        if g["wards"] >= 5:
            flags.add("warding")
        if g["bodies"] > g["draft_size"]:
            flags.add("linked_pair_draft")
        if g["farm_spread"] is not None and g["farm_spread"] <= TIGHT_SPREAD_TILES:
            flags.add("tight_farm_grouping")
        if g["gem_loss"] <= g["submitted"] * 0.15:
            flags.add("protected_carriers_low_loss")
        for item in g["consumables"]:
            flags.add("consumable:" + item.lower().replace(" ", "_"))
        total_items = sum(g["item_families"].values())
        for family, count in g["item_families"].items():
            if total_items and count / total_items >= 0.3:
                flags.add("item_family:" + family.lower())
        stats_total = sum(g["item_stats"].values())
        for stat, count in g["item_stats"].items():
            if stats_total and count / stats_total >= 0.5:
                flags.add("stat_majority:" + stat.lower())
        return flags

    census = defaultdict(lambda: {"teams": set(), "games": 0, "wins": 0})
    per_team_games = Counter()
    per_team_flag = defaultdict(Counter)
    for g in games:
        per_team_games[g["team"]] += 1
        flags = feature_flags(g)
        for k in flags | {"any_game"}:
            c = census[k]
            c["teams"].add(g["team"])
            c["games"] += 1
            c["wins"] += g["won"]
        for k in flags:
            per_team_flag[k][g["team"]] += 1

    table = []
    for k, v in census.items():
        if k == "any_game":
            continue
        habitual = {t for t, n in per_team_flag[k].items()
                    if n >= 0.5 * per_team_games[t]}
        table.append({"feature": k,
                      "teams": sorted(v["teams"]), "team_count": len(v["teams"]),
                      "habitual_teams": sorted(habitual),
                      "habitual_count": len(habitual),
                      "games": v["games"], "wins": v["wins"],
                      "win_rate": v["wins"] / v["games"] if v["games"] else None})
    table.sort(key=lambda r: (-r["habitual_count"], -r["team_count"], -r["games"]))
    args.out.write_text(json.dumps({
        "team_games": len(games), "matches_analyzed": len(matches),
        "skipped_incomplete": skipped, "features": table, "games_detail": games,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    for row in table:
        print(f"{row['habitual_count']:>2}/{row['team_count']:>2} teams  "
              f"{row['games']:>4} games  {row['wins']:>4} wins  {row['feature']}",
              flush=True)


if __name__ == "__main__":
    main()
