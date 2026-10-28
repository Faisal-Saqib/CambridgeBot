#!/usr/bin/env python3
"""Freeze an event-checked analysis of the explicit top-team study manifest."""
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from analyze_online_batch import aggregate, side_stats

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / "matches/top-team-study-20261028"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def at_round(timeline, rnd):
    offset = 0
    for run in timeline["runs"]:
        end = offset + run["duration"]
        if offset <= rnd < end:
            return float(run["value"])
        offset = end
    return None  # Never extend a finished game to a later comparison round.


def event_key(entry):
    ts = entry["timestamp"]
    return (ts["round"], ts["phase"], ts["substep"], ts["input"], entry["target"]["id"])


def analyze_side(data, side):
    roster = {c["id"]: c for c in data["roster"]["champions"]}
    stats = side_stats(data, side, roster)
    by_owner = defaultdict(lambda: defaultdict(list))
    assist_owners, kill_keys = defaultdict(set), set()
    for series in data["events"]:
        owner, kind = series["owner"], series["kind"]
        if owner.get("kind") != "champion":
            continue
        for entry in series["entries"]:
            if kind == "kill":
                kill_keys.add(event_key(entry))
            elif kind == "assist":
                assist_owners[event_key(entry)].add(owner["id"])
            by_owner[owner["id"]][kind].append(entry)
    assert not (set(assist_owners) - kill_keys), "Assist cannot be linked to a kill"
    timelines = {(t["owner"]["id"], t["metric"]): t for t in data["championTimelines"]}
    champions, credited, captures = [], Counter(), defaultdict(list)
    for champion in data["champions"]:
        cid = champion["id"]
        if roster[cid]["team"] != side:
            continue
        events, metrics = by_owner[cid], champion["metrics"]
        paid = sum(e["amount"] for kind in ("buyItem", "buyConsumable") for e in events[kind])
        assert math.isclose(paid, float(metrics["spentGold"]), abs_tol=1e-5)
        for metric in ("earnedGold", "spentGold", "championDamageDone", "monsterDamageDone"):
            timeline = timelines[cid, metric]
            assert sum(r["duration"] for r in timeline["runs"]) == data["match"]["roundsStarted"] + 1
            assert math.isclose(float(timeline["runs"][-1]["value"]), float(metrics[metric]),
                                rel_tol=1e-6, abs_tol=1e-4)
        by_stat, by_family = Counter(), Counter()
        purchases = []
        for entry in events["buyItem"]:
            name = entry["target"]["name"]
            match = re.fullmatch(r"(.+) (Shard|Emblem) of (Strength|Health|Focus)", name)
            assert match, name
            family, _, stat = match.groups()
            by_stat[stat] += entry["amount"]
            by_family[family] += entry["amount"]
            purchases.append({"round": entry["timestamp"]["round"], "item": name,
                              "quantity": int(entry["value"]), "gold_spent": entry["amount"]})
        combinations = [{"round": e["timestamp"]["round"], "item": e["target"]["name"],
                         "quantity": int(e["value"])} for e in events["itemCombination"]]
        kills = []
        for entry in events["kill"]:
            assistants = assist_owners[event_key(entry)]
            assert cid not in assistants
            assert all(roster[a]["team"] == side for a in assistants)
            participants = 1 + len(assistants)
            credited[participants] += 1
            kills.append({"round": entry["timestamp"]["round"], "victim": entry["target"]["name"],
                          "credited_attackers": participants, "x": entry["x"], "y": entry["y"]})
        assert len(kills) == int(metrics["kills"])
        for entry in events["gemCollection"]:
            if entry.get("target", {}).get("kind") == "campGroup":
                captures[event_key(entry)].append({
                    "champion_id": cid, "champion": roster[cid]["name"],
                    "gems": int(entry["value"]), "x": entry["x"], "y": entry["y"],
                })
        champions.append({
            "id": cid, "name": roster[cid]["name"], "draft_pick": roster[cid]["draftPick"],
            "metrics": {key: float(value) for key, value in metrics.items()},
            "item_gold_by_stat": dict(by_stat), "item_gold_by_family": dict(by_family),
            "purchases": purchases, "emblem_combinations": combinations, "kill_events": kills,
            "early": {str(rnd): {metric: at_round(timelines[cid, metric], rnd)
                                for metric in ("earnedGold", "spentGold", "championDamageDone",
                                               "monsterDamageDone", "submittedGems", "deaths")}
                      for rnd in (100, 300, 500)},
        })
    assert sum(credited.values()) == stats["metrics"]["kills"]
    gold_total = stats["metrics"]["earnedGold"]
    damage_total = stats["metrics"]["championDamageDone"]
    for champion in champions:
        champion["gold_share"] = champion["metrics"]["earnedGold"] / gold_total if gold_total else None
        champion["pvp_damage_share"] = champion["metrics"]["championDamageDone"] / damage_total if damage_total else None
    capture_records = [
        {"round": key[0], "group_id": key[4], "recipients": recipients,
         "gems": sum(r["gems"] for r in recipients)}
        for key, recipients in sorted(captures.items())
    ]
    item_stats, item_families = Counter(), Counter()
    for champion in champions:
        item_stats.update(champion["item_gold_by_stat"])
        item_families.update(champion["item_gold_by_family"])
    return {
        "stats": stats, "champions": champions,
        "item_gold_by_stat": dict(item_stats), "item_gold_by_family": dict(item_families),
        "credited_attackers_per_kill": dict(credited),
        "captures": capture_records,
        "capture_recipient_counts": dict(Counter(len(c["recipients"]) for c in capture_records)),
        "largest_earner_id": max(champions, key=lambda c: c["metrics"]["earnedGold"])["id"],
        "largest_pvp_damage_id": max(champions, key=lambda c: c["metrics"]["championDamageDone"])["id"],
    }


def capture():
    manifest = load(FOLDER / "manifest.json")
    for name, expected in manifest["input_sha256"].items():
        assert sha(FOLDER / name) == expected, name
    matches = {o["match"]["matchId"]: o["match"] for o in manifest["observations"] if o["match"]}
    games, hashes = {}, {}
    for match_id, metadata in matches.items():
        path = FOLDER / "summaries" / f"{match_id}.json"
        data = load(path)
        assert data["diagnostics"]["detailedCaptureComplete"]
        assert len({c["id"] for c in data["roster"]["champions"]}) == len(data["champions"])
        sides = {}
        for team in metadata["teams"]:
            side = "team" + team["side"].upper()
            assert (data["match"]["outcome"] == side) == (team["result"] == "win")
            sides[side] = {"identity": team, **analyze_side(data, side)}
        games[match_id] = {"metadata": metadata, "engine_match": data["match"], "sides": sides}
        hashes[match_id] = sha(path)
        print(f"Checked {metadata['map']} {match_id}", flush=True)
    baseline, baseline_hashes = defaultdict(list), {}
    for path in sorted((ROOT / "matches/map-campaign-v22-20261028/results").glob("*.json")):
        selected = [m for m in load(path)["matches"] if m["map"] in manifest["maps"]]
        if selected:
            baseline_hashes[path.name] = sha(path)
            for match in selected:
                baseline[match["map"]].append(match)
    assert all(len(baseline[m]) == 5 for m in manifest["maps"])
    for rows in baseline.values():
        assert len({m["opponent_team_id"] for m in rows}) == 5
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "manifest_sha256": sha(FOLDER / "manifest.json"), "summary_sha256": hashes,
        "games": games, "observations": manifest["observations"],
        "baseline": {mp: {"aggregate": aggregate(rows), "matches": rows} for mp, rows in baseline.items()},
        "baseline_result_sha256": baseline_hashes,
        "definitions": {
            "purchases": "Gold from buyItem event amounts only; itemCombination is not another purchase.",
            "credited_attackers": "Killer plus unique credited assists linked by target, round, phase, "
                                  "substep and input. Measures kill participation, not continuous formation.",
            "captures": "Recipients of campGroup gemCollection events at each capture, including zero-gem entries.",
            "gold_share": "One body's lifetime earnedGold / summed team earnedGold; not evidence of intentional funneling.",
            "timelines": "RLE index equals round number; initial snapshot is index 0. Missing future rounds are null.",
            "scope": "18 selected team/map observations from 15 distinct ranked games, with both perspectives "
                     "retained when selected teams meet. Current ranks do not identify historical bot versions. "
                     "Different opponents/sides mean this is observational scouting, not a matched win-rate test.",
        },
    }


def render(data):
    rows = [
        "# Top-team map study: captured observations", "",
        "This table reads a frozen analysis. Interpretations and candidate decisions are in TOP_TEAM_FINDINGS.md.",
        "", data["definitions"]["scope"], "",
        "| Team | Map | Result | Gems | Deaths | Largest gold share | Largest damage share | Gold spent: Strength / Focus / Health |",
        "| --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for observation in data["observations"]:
        metadata = observation["match"]
        if metadata is None:
            continue
        game = data["games"][metadata["matchId"]]
        team = next(s for s in game["sides"].values()
                    if s["identity"]["teamId"] == observation["team"]["teamId"])
        champions = {c["id"]: c for c in team["champions"]}
        earner = champions[team["largest_earner_id"]]
        dealer = champions[team["largest_pvp_damage_id"]]
        share = lambda c, metric: f"{c['name']} {c[metric]:.0%}" if c[metric] is not None else "no total"
        stats = team["stats"]
        spend = team["item_gold_by_stat"]
        rows.append(f"| {observation['team']['name']} | {observation['map']} | {team['identity']['result']} "
                    f"| {stats['submitted']} | {stats['metrics']['deaths']:.0f} "
                    f"| {share(earner, 'gold_share')} | {share(dealer, 'pvp_damage_share')} "
                    f"| {spend.get('Strength', 0):.0f} / {spend.get('Focus', 0):.0f} / {spend.get('Health', 0):.0f} |")
    rows += ["", "Purchases are checked against spentGold and counted once. Automatic emblem combinations are excluded.",
             "High lifetime gold share can result from kills, farm distribution, survival or passives; it does not establish deliberate resource funneling.",
             "", "## Match references", ""]
    for match_id, game in data["games"].items():
        metadata = game["metadata"]
        names = " vs ".join(t["name"] for t in metadata["teams"])
        rows.append(f"- `{metadata['map']}`: {names}, `{match_id}`, {metadata['createdAt']}.")
    rows += ["", "Frozen data: `matches/top-team-study-20261028/analysis.json`. "
             "Raw inputs, selection manifest and hashes are kept beside it.", ""]
    (ROOT / "docs/TOP_TEAM_OBSERVATIONS.md").write_text("\n".join(rows), encoding="utf-8")


def main():
    path = FOLDER / "analysis.json"
    if not path.exists():
        data = capture()
        assert not path.exists()
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    data = load(path)
    assert data["manifest_sha256"] == sha(FOLDER / "manifest.json")
    render(data)
    print(f"Frozen analysis: {len(data['games'])} distinct games; rendered docs/TOP_TEAM_OBSERVATIONS.md")


if __name__ == "__main__":
    main()
