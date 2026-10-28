#!/usr/bin/env python3
"""Download ranked matches played by the current top-20 ladder teams.

Read-only scouting: creates no matches, spends no match quota. Fetches each
team's recent ranked match list, selects up to PER_MAP newest finished games
per team per published map (deduplicated), and downloads full summaries.

Resumable: existing list/summary files are reused; every API call is logged
under requests/.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / "matches" / "top20-scout"
MAPS_FILE = ROOT / "matches" / "map-campaign-v22-20261028" / "campaign.json"
PER_MAP = 2


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_new(path, value):
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def call(args, log_dir):
    """Run a read-only cambc command with bounded retries; log every attempt."""
    assert args[0] in ("ladder", "matches"), args
    for attempt in range(6):
        started = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(["cambc", *args], cwd=ROOT, capture_output=True,
                                text=True, encoding="utf-8", timeout=180)
        record = {"started_at": started, "command": ["cambc", *args],
                  "returncode": result.returncode,
                  "stdout": result.stdout[-4000:], "stderr": result.stderr[-4000:]}
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        (log_dir / f"{name}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        time.sleep(0.5)
        if result.returncode == 0:
            return result.stdout
        message = (result.stderr or "") + (result.stdout or "")
        transient = any(s in message.lower() for s in
                        ("429", "peer disconnected", "connection", "timed out",
                         "retry shortly", "retry after"))
        if not transient or attempt == 5:
            raise RuntimeError(f"{args}: {message[:500]}")
        retry = re.search(r"retry after (\d+) seconds", message)
        delay = max(int(retry.group(1)) if retry else 0, 5 * (attempt + 1))
        print(f"  retry in {delay}s: {' '.join(args[:2])}", flush=True)
        time.sleep(delay)
    raise AssertionError("unreachable")


def finished(m):
    return m.get("status") == "finished" and m.get("kind") == "ranked"


def select_matches(teams, lists_dir, published_names):
    """Pick up to PER_MAP newest finished ranked games per team per map."""
    selection = {}  # matchId -> {"match": ..., "teams": [names]}
    coverage = {}
    for team in teams:
        path = lists_dir / f"rank-{team['rank']:02d}-{team['teamId']}.json"
        matches = [m for m in load(path)["matches"] if finished(m)]
        per_map = {}
        for m in matches:
            name = m.get("map") or m.get("mapName")
            if name not in published_names:
                continue
            per_map.setdefault(name, []).append(m)
        covered = []
        for name, ms in per_map.items():
            ms.sort(key=lambda m: (m.get("createdAt") or "", m["matchId"]), reverse=True)
            covered.append(name)
            for m in ms[:PER_MAP]:
                assert name == (m.get("map") or m.get("mapName"))
                entry = selection.setdefault(m["matchId"], {"match": m, "teams": []})
                entry["teams"].append(team["name"])
        coverage[team["name"]] = len(covered)
    return selection, coverage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lists-only", action="store_true",
                        help="Fetch team match lists and the selection manifest, no summaries.")
    parser.add_argument("--all-lists", action="store_true",
                        help="Also download summaries for every finished ranked match in the team lists.")
    parser.add_argument("--limit", type=int, default=0,
                        help="Download at most N more summaries this run (0 = all pending).")
    args = parser.parse_args()

    lists_dir = FOLDER / "lists"
    summaries_dir = FOLDER / "summaries"
    requests_dir = FOLDER / "requests"
    for d in (lists_dir, summaries_dir, requests_dir):
        d.mkdir(parents=True, exist_ok=True)

    ladder = load(FOLDER / "ladder.json")
    teams = [t for t in ladder["teams"] if t["rank"] <= 20]
    assert len(teams) == 20, len(teams)
    maps = {m["name"]: m["id"] for m in load(MAPS_FILE)["maps"]}
    print(f"Published maps: {len(maps)}", flush=True)

    # Phase 1: recent ranked lists for each team.
    for team in teams:
        path = lists_dir / f"rank-{team['rank']:02d}-{team['teamId']}.json"
        if path.exists():
            continue
        raw = call(["matches", "list", "--team", team["teamId"], "--kind", "ranked",
                    "--limit", "100", "--json"], requests_dir)
        data = json.loads(raw)
        assert data["matches"], team["name"]
        save_new(path, data)
        print(f"List {team['rank']:>2} {team['name']}: {len(data['matches'])} matches",
              flush=True)

    # Phase 2: select and freeze the manifest once.
    manifest_path = FOLDER / "manifest.json"
    if manifest_path.exists():
        manifest = load(manifest_path)
        selection = {mid: e["match"] for mid, e in manifest["selection"].items()}
    else:
        selection, coverage = select_matches(teams, lists_dir, set(maps))
        manifest = {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "selection_rule": f"Newest {PER_MAP} finished ranked games per team per "
                              "published map from the team's recent-100 ranked list; "
                              "shared matches deduplicated and attributed to every "
                              "observed top-20 participant.",
            "per_team_map_coverage": coverage,
            "selection": {mid: {"match": e["match"], "observed_teams": e["teams"]}
                          for mid, e in sorted(selection.items())},
            "list_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(lists_dir.glob("*.json"))},
        }
        save_new(manifest_path, manifest)
    print(f"Selected {len(manifest['selection'])} distinct matches", flush=True)
    if args.lists_only:
        for name, count in sorted(manifest["per_team_map_coverage"].items()):
            print(f"  {name}: {count} maps", flush=True)
        return

    # Phase 3: summaries.
    for stale in summaries_dir.glob("*.download.json"):
        stale.unlink()
    pending = [mid for mid in manifest["selection"]
               if not (summaries_dir / f"{mid}.json").exists()]
    if args.all_lists:
        listed = set()
        for p in lists_dir.glob("*.json"):
            listed.update(m["matchId"] for m in load(p)["matches"] if finished(m))
        pending.extend(mid for mid in sorted(listed - set(manifest["selection"]))
                       if not (summaries_dir / f"{mid}.json").exists())
    print(f"Pending summaries: {len(pending)}", flush=True)
    done = failed = 0
    for mid in pending:
        if args.limit and done >= args.limit:
            break
        path = summaries_dir / f"{mid}.json"
        temporary = path.with_suffix(".download.json")
        try:
            call(["matches", "summary", mid, "--json", "-o", str(temporary)], requests_dir)
            data = load(temporary)
            assert data["diagnostics"]["detailedCaptureComplete"], mid
            assert data["match"]["outcome"] in ("teamA", "teamB"), mid
            temporary.replace(path)
        except Exception as exc:
            print(f"FAILED {mid}: {exc}", file=sys.stderr, flush=True)
            failed += 1
            if temporary.exists():
                temporary.unlink()
            continue
        done += 1
        if done % 10 == 0 or done == len(pending):
            print(f"Summaries {done}/{len(pending)} (failures {failed})", flush=True)
    print(f"Downloaded {done}, failed {failed}, "
          f"total present {len(list(summaries_dir.glob('*.json')))}", flush=True)


if __name__ == "__main__":
    main()
