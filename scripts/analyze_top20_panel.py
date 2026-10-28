#!/usr/bin/env python3
"""Compare two completed, frozen top-20 panels without fetching or changing games."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from analyze_online_batch import aggregate


def load_panel(folder):
    config = json.loads((folder / "panel.json").read_text(encoding="utf-8"))
    state = json.loads((folder / "state.json").read_text(encoding="utf-8"))
    assert config["opponent_rule"] == "current_top20"
    assert len(state["jobs"]) == len(config["opponents"]), "This comparison requires one group per opponent."
    assert all(j["status"] == "complete" for j in state["jobs"])
    expected = {(t["teamId"], m["id"]) for t in config["opponents"] for m in config["maps"]}
    rows, fingerprints = [], {}
    for path in [folder / "panel.json", *sorted((folder / "results").glob("*.json"))]:
        raw = path.read_bytes()
        fingerprints[str(path.resolve())] = hashlib.sha256(raw).hexdigest()
        if path.parent.name == "results":
            rows.extend(json.loads(raw)["matches"])
    assert len({m["match_id"] for m in rows}) == len(rows) == len(expected)
    indexed = {(m["opponent_team_id"], m["map_id"]): m for m in rows}
    assert set(indexed) == expected
    intents = {j["opponent_id"]: {
        "group_id": j["group_id"], "source_group": j.get("source_group"),
        "command": j["command"], "opponent_rank": j["opponent_rank"],
        "rank_checked_at": j["rank_checked_at"],
    } for j in state["jobs"]}
    assert len(intents) == len(config["opponents"]), "This comparison requires one group per opponent."
    assert all(type(j["opponent_rank"]) is int and 1 <= j["opponent_rank"] <= 20 for j in intents.values())
    fingerprints[str(folder.resolve()) + "::intents"] = hashlib.sha256(
        json.dumps(intents, sort_keys=True).encode()).hexdigest()
    return config, intents, rows, indexed, fingerprints


def report(data):
    a, b = data["baseline"], data["candidate"]
    lines = [
        "# Matched top-20 formation comparison", "",
        f"Baseline v{data['baseline_version']}: {a['wins']}/{a['games']} wins. "
        f"Candidate v{data['candidate_version']}: {b['wins']}/{b['games']} wins.", "",
        f"{data['paired_games']} games match on opponent, map, side, seed, map hash and engine build. "
        "Saved opponent submissions were requested through --source-group. "
        "Per-match submission IDs are not exposed; live/selected-version checks and source hashes "
        "remain the attribution evidence.", "",
        "| Metric | Baseline | Candidate |",
        "| --- | ---: | ---: |",
    ]
    for label, key in (
        ("Gems submitted", "submitted"), ("Gems collected", "collected"),
        ("Deaths", "deaths"), ("Kills", "kills"), ("Gold earned", "gold"),
        ("Carried gems lost", "gem_loss"), ("Tributes", "tributes"),
        ("Fuel exhaustion events", "fuel_exhaustions"), ("Bot faults", "bot_faults"),
    ):
        lines.append(f"| {label} | {a['us'][key]:g} | {b['us'][key]:g} |")
    lines += ["", "| Map | Baseline wins | Candidate wins | Baseline gems | Candidate gems | Baseline deaths | Candidate deaths |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for name, row in data["by_map"].items():
        x, y = row["baseline"], row["candidate"]
        lines.append(f"| {name} | {x['wins']}/{x['games']} | {y['wins']}/{y['games']} "
                     f"| {x['us']['submitted']} | {y['us']['submitted']} "
                     f"| {x['us']['deaths']:g} | {y['us']['deaths']:g} |")
    lines += ["", "All completed games, including faults, are included. "
              "This is a small fixed-opponent panel; a change in its win count is not proof of general improvement."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    bc, bj, br, bi, bh = load_panel(args.baseline)
    cc, cj, cr, ci, ch = load_panel(args.candidate)
    assert set(bi) == set(ci)
    assert not ({m["match_id"] for m in br} & {m["match_id"] for m in cr})
    for opponent, job in cj.items():
        source = bj[opponent]["group_id"]
        assert job["source_group"] == source
        at = job["command"].index("--source-group")
        assert job["command"][at + 1] == source
    matched_fields = ("side", "seed", "map_hash", "engine_version", "engine_build_hash")
    for key in bi:
        for field in matched_fields:
            assert bi[key][field] == ci[key][field], (key, field, bi[key][field], ci[key][field])
    fingerprints = bh | ch
    output = args.candidate / "comparison.json"
    if output.exists():
        data = json.loads(output.read_text(encoding="utf-8"))
        assert data["input_sha256"] == fingerprints, "Frozen comparison inputs changed."
    else:
        data = {
            "baseline_version": bc["submission_version"], "candidate_version": cc["submission_version"],
            "input_sha256": fingerprints, "baseline": aggregate(br), "candidate": aggregate(cr),
            "paired_games": len(bi),
            "outcome_transitions": dict(Counter(bi[k]["result"] + " -> " + ci[k]["result"] for k in bi)),
            "by_map": {name: {
                "baseline": aggregate([m for m in br if m["map"] == name]),
                "candidate": aggregate([m for m in cr if m["map"] == name]),
            } for name in sorted({m["map"] for m in br})},
            "baseline_matches": br, "candidate_matches": cr,
        }
        output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    assert args.report.parent.is_dir()
    args.report.write_text(report(data), encoding="utf-8")
    print(json.dumps({k: data[k] for k in ("baseline", "candidate", "paired_games", "outcome_transitions")}))


if __name__ == "__main__":
    main()
