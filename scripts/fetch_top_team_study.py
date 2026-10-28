#!/usr/bin/env python3
"""Capture a fixed observational sample of existing ranked matches; create no matches."""
import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / "matches/top-team-study-20261028"
MAPS = ("00the_line", "00anvil", "00stampede", "01starfish", "00expanse", "01islands")


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_new(path, value):
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def call(args):
    assert args[:2] in (["matches", "list"], ["matches", "summary"])
    for attempt in range(5):
        started = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(["cambc", *args], cwd=ROOT, capture_output=True,
                                text=True, encoding="utf-8", timeout=120)
        record = {"started_at": started, "command": ["cambc", *args],
                  "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        save_new(FOLDER / "requests" / f"{name}.json", record)
        time.sleep(3)
        if result.returncode == 0:
            return result.stdout
        message = result.stderr or result.stdout
        transient = any(s in message.lower() for s in
                        ("429", "peer disconnected", "connection", "timed out", "retry shortly"))
        if not transient or attempt == 4:
            raise RuntimeError(message)
        retry = re.search(r"retry after (\d+) seconds", message)
        delay = max(int(retry.group(1)) if retry else 0, 5 * (attempt + 1))
        print(f"Study read retry in {delay}s: {args[:2]}", flush=True)
        time.sleep(delay)
    raise AssertionError("unreachable")


def main():
    assert FOLDER.is_dir()
    (FOLDER / "requests").mkdir(exist_ok=True)
    (FOLDER / "summaries").mkdir(exist_ok=True)
    manifest_path = FOLDER / "manifest.json"
    if not manifest_path.exists():
        teams = load(FOLDER / "ladder-top25.json")["teams"][:3]
        assert [t["rank"] for t in teams] == [1, 2, 3]
        assert len({t["teamId"] for t in teams}) == 3
        maps = {m["name"]: m["id"] for m in
                load(ROOT / "matches/map-campaign-v22-20261028/campaign.json")["maps"]}
        observations, inputs = [], {"ladder-top25.json", "ladder-captured-at.txt"}
        for team in teams:
            recent_name = f"rank-{team['rank']}-recent.json"
            inputs.add(recent_name)
            recent = load(FOLDER / recent_name)["matches"]
            for map_name in MAPS:
                candidates = [m for m in recent if m["status"] == "finished"
                              and m["mapId"] == maps[map_name] and m["kind"] == "ranked"]
                if not candidates:
                    filename = f"rank-{team['rank']}-{map_name}.json"
                    path = FOLDER / filename
                    if not path.exists():
                        raw = call(["matches", "list", "--team", team["teamId"],
                                    "--kind", "ranked", "--map", maps[map_name],
                                    "--limit", "5", "--json"])
                        save_new(path, json.loads(raw))
                    inputs.add(filename)
                    candidates = [m for m in load(path)["matches"] if m["status"] == "finished"
                                  and m["mapId"] == maps[map_name] and m["kind"] == "ranked"]
                match = max(candidates, key=lambda m: (m["createdAt"], m["matchId"])) if candidates else None
                if match:
                    assert match["map"] == map_name
                    assert any(t["teamId"] == team["teamId"] for t in match["teams"])
                observations.append({"team": team, "map": map_name, "match": match})
        save_new(manifest_path, {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "selection": "Current ladder ranks 1-3; six prespecified maps. Latest finished ranked game "
                         "per team/map in captured recent-100 list, or filtered latest-five fallback. "
                         "Select irrespective of win/loss; preserve both perspectives of shared matches. "
                         "Ratings/ranks are capture-time values, not match-time values.",
            "maps": MAPS, "observations": observations,
            "input_sha256": {name: hashlib.sha256((FOLDER / name).read_bytes()).hexdigest()
                             for name in sorted(inputs)},
        })
    manifest = load(manifest_path)
    matches = {o["match"]["matchId"]: o["match"] for o in manifest["observations"] if o["match"]}
    print(f"Frozen selection: {len(manifest['observations'])} team/map observations, "
          f"{len(matches)} distinct matches.", flush=True)
    for index, (match_id, match) in enumerate(matches.items(), 1):
        path = FOLDER / "summaries" / f"{match_id}.json"
        if not path.exists():
            temporary = path.with_suffix(".download.json")
            call(["matches", "summary", match_id, "--json", "-o", str(temporary)])
            data = load(temporary)
            assert data["diagnostics"]["detailedCaptureComplete"]
            assert data["match"]["outcome"] in ("teamA", "teamB")
            temporary.replace(path)
        data = load(path)
        assert data["diagnostics"]["detailedCaptureComplete"]
        assert data["match"]["outcome"] in ("teamA", "teamB")
        for team in match["teams"]:
            side = "team" + team["side"].upper()
            assert (data["match"]["outcome"] == side) == (team["result"] == "win")
        print(f"Captured {index}/{len(matches)}: {match['map']} {match_id}", flush=True)


if __name__ == "__main__":
    main()
