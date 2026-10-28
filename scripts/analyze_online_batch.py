#!/usr/bin/env python3
"""Analyze explicit, completed online groups from saved CLI metadata and summaries.

No network calls. Match identity and our side come from the saved group metadata,
never the draft. Output is an immutable analysis snapshot; use a new path for a
different analysis. Submission labels are operator-supplied context, not proof
of a per-match submission ID.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

OUR_TEAM = "b224cf2f-1e0f-44e1-9546-b574f39cd9eb"
METRICS = (
    "collectedGems", "submittedGems", "deaths", "kills", "earnedGold",
    "monsterDamageDone", "monsterDamageTaken",
    "championDamageDone", "championDamageTaken",
)


def load(path):
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8-sig")), hashlib.sha256(raw).hexdigest()


def side_stats(data, side, roster):
    champions = []
    sums = Counter()
    items = Counter()
    consumables = Counter()
    for champion in data["champions"]:
        identity = roster[champion["id"]]
        if identity["team"] != side:
            continue
        values = {key: float(champion["metrics"][key]) for key in METRICS}
        sums.update(values)
        champions.append({
            "id": champion["id"], "name": identity["name"], "metrics": values,
            "items_bought": champion.get("itemsBought", []),
            "consumables_bought": champion.get("consumablesBought", []),
        })
        for item in champion.get("itemsBought", []):
            items[item["item"]] += int(item["quantity"])
        for item in champion.get("consumablesBought", []):
            consumables[item["consumable"]] += int(item["quantity"])

    event_counts = Counter()
    loss_by_killer = Counter()
    losses = []
    submissions = []
    deaths = []
    for series in data["events"]:
        owner = series["owner"]
        if owner.get("kind") != "champion":
            continue
        identity = roster[owner["id"]]
        assert identity["team"] == owner["team"]
        if identity["team"] != side:
            continue
        kind = series["kind"]
        for entry in series["entries"]:
            event_counts[kind] += 1
            if kind in ("death", "wardPlacement", "fuelExhausted", "kill"):
                assert int(entry["value"]) == 1, (kind, entry)
            if kind == "gemSubmission":
                submissions.append(int(entry["value"]))
            elif kind == "gemLoss":
                target = entry.get("target")
                target = target if isinstance(target, dict) else {}
                killer_kind = target.get("kind", "unknown")
                loss_by_killer[killer_kind] += int(entry["value"])
                losses.append({
                    "round": entry["timestamp"]["round"],
                    "champion": identity["name"], "gems": int(entry["value"]),
                    "killer_kind": killer_kind, "killer": target.get("name"),
                    "x": entry["x"], "y": entry["y"],
                })
            elif kind == "death":
                target = entry.get("target")
                target = target if isinstance(target, dict) else {}
                deaths.append({
                    "round": entry["timestamp"]["round"],
                    "champion": identity["name"],
                    "killer_kind": target.get("kind", "unknown"),
                    "killer": target.get("name"),
                })

    submitted = next(int(t["submittedGems"]) for t in data["teams"] if t["team"] == side)
    assert sum(submissions) == submitted == sums["submittedGems"]
    assert len(deaths) == sums["deaths"]
    assert event_counts["kill"] == sums["kills"]
    return {
        "submitted": submitted,
        "metrics": dict(sums),
        "event_counts": dict(event_counts),
        "gem_loss": sum(loss_by_killer.values()),
        "gem_loss_by_killer_kind": dict(loss_by_killer),
        "tribute_count": len(submissions),
        "tribute_mean": submitted / len(submissions) if submissions else None,
        "tribute_max": max(submissions, default=0),
        "loss_events": sorted(losses, key=lambda e: e["round"]),
        "death_events": sorted(deaths, key=lambda e: e["round"]),
        "items_bought": dict(items),
        "consumables_bought": dict(consumables),
        "champions": champions,
        "bot_faults": data["diagnostics"]["botFaults"][side],
    }


def aggregate(matches):
    output = {"games": len(matches), "wins": sum(m["result"] == "win" for m in matches)}
    output["losses"] = output["games"] - output["wins"]
    for side in ("us", "opponent"):
        values = Counter()
        for match in matches:
            stats = match[side]
            values["submitted"] += stats["submitted"]
            values["collected"] += stats["metrics"]["collectedGems"]
            values["deaths"] += stats["metrics"]["deaths"]
            values["kills"] += stats["metrics"]["kills"]
            values["gold"] += stats["metrics"]["earnedGold"]
            values["gem_loss"] += stats["gem_loss"]
            values["gem_loss_to_champions"] += stats["gem_loss_by_killer_kind"].get("champion", 0)
            values["gem_loss_to_camps"] += stats["gem_loss_by_killer_kind"].get("camp", 0)
            values["tributes"] += stats["tribute_count"]
            values["wards"] += stats["event_counts"].get("wardPlacement", 0)
            values["fuel_exhaustions"] += stats["event_counts"].get("fuelExhausted", 0)
            values["bot_faults"] += stats["bot_faults"]
        output[side] = dict(values)
        output[side]["tribute_mean"] = values["submitted"] / values["tributes"] if values["tributes"] else None
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", nargs="+", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError(f"Snapshot already exists; read it instead of recomputing: {args.out}")
    if not args.out.parent.is_dir():
        raise ValueError(f"Output parent does not exist: {args.out.parent}")

    games = []
    seen_ids = set()
    source_hashes = {}
    for path in args.metadata:
        group, digest = load(path)
        source_hashes[str(path)] = digest
        assert group.get("nextCursor") is None, "Group metadata is incomplete"
        assert len(group["matches"]) == 5, "Expected the full five-match group"
        for match in sorted(group["matches"], key=lambda m: m["position"]):
            assert match["status"] == "finished", (match["matchId"], match["status"])
            assert match["groupId"] == group["groupId"]
            assert match["matchId"] not in seen_ids
            seen_ids.add(match["matchId"])
            ours = next(t for t in match["teams"] if t["teamId"] == OUR_TEAM)
            theirs = next(t for t in match["teams"] if t["teamId"] != OUR_TEAM)
            us, them = "team" + ours["side"].upper(), "team" + theirs["side"].upper()
            assert {us, them} == {"teamA", "teamB"}
            summary_path = args.cache / (match["matchId"] + ".json")
            data, digest = load(summary_path)
            source_hashes[str(summary_path)] = digest
            assert data["diagnostics"]["detailedCaptureComplete"]
            assert data["match"]["outcome"] in ("teamA", "teamB")
            result = "win" if data["match"]["outcome"] == us else "loss"
            assert result == ours["result"], match["matchId"]
            roster = {c["id"]: c for c in data["roster"]["champions"]}
            assert len(roster) == len(data["roster"]["champions"])
            games.append({
                "match_id": match["matchId"], "group_id": group["groupId"],
                "map": match["map"], "map_id": match["mapId"],
                "side": ours["side"], "result": result,
                "opponent_team_id": theirs["teamId"], "opponent_name": theirs["name"],
                "created_at": match["createdAt"], "finished_at": match["finishedAt"],
                "rounds": data["match"]["roundsCompleted"],
                "seed": data["match"]["seed"], "map_hash": data["match"]["mapHash"],
                "engine_version": data["match"]["engineVersion"],
                "engine_build_hash": data["match"]["engineBuildHash"],
                "per_match_submission_id": ours.get("submissionId"),
                "us": side_stats(data, us, roster),
                "opponent": side_stats(data, them, roster),
            })

    snapshot = {
        "label": args.label,
        "version_attribution": "Label supplied by operator. Consult live-state snapshots; match metadata may not expose submission IDs.",
        "source_hashes": source_hashes,
        "definitions": {
            "gems_lost": "Sum of gemLoss event values, separately by target kind.",
            "tributes": "Count of completed gemSubmission events; their summed value is checked against team and champion totals.",
            "deaths": "Champion metric totals checked against death events.",
            "fuel_exhaustions": "Count of per-champion fuelExhausted entries, including initialization.",
            "items": "Purchases, not evidence that consumables were used.",
        },
        "total": aggregate(games),
        "by_opponent": {
            name: aggregate([m for m in games if m["opponent_name"] == name])
            for name in sorted({m["opponent_name"] for m in games})
        },
        "matches": games,
    }
    args.out.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(args.label)
    for game in games:
        us, them = game["us"], game["opponent"]
        print(f"{game['opponent_name']:12} {game['map']:18} {game['side']} {game['result']:4} "
              f"score {us['submitted']:4}-{them['submitted']:<4} "
              f"lost {us['gem_loss']:4}-{them['gem_loss']:<4} "
              f"deaths {us['metrics']['deaths']:3.0f}-{them['metrics']['deaths']:<3.0f} "
              f"tributes {us['tribute_count']:2}-{them['tribute_count']:<2} "
              f"wards {us['event_counts'].get('wardPlacement', 0):3} "
              f"fuel {us['event_counts'].get('fuelExhausted', 0):3} "
              f"faults {us['bot_faults']}")
    print(json.dumps({"total": snapshot["total"], "by_opponent": snapshot["by_opponent"]}, indent=2))
    print(f"Snapshot: {args.out}")


if __name__ == "__main__":
    main()
