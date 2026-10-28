"""Rematch the v26 top-5 test on v27: same maps, sides and opponent bots
(--source-group), only teams currently ranked 1-5. Stops on any failed create."""
import json, subprocess, sys, datetime
from pathlib import Path
OUT = Path(__file__).parent
PREV = json.loads((OUT.parent / "top5" / "groups.json").read_text())
MAPS = "20aedb4d-faa0-49b9-a4eb-93bea93916f5,8d9d1dc7-4386-424a-855a-b7cfc76271e3,db1fd93e-b260-45c6-b0f0-ff4252d86f10,07e14a72-a270-4f1e-ad1e-5c03b7470639,f6099a73-97ed-4b5b-8fd9-7598407f4df5"
def cli(args):
    return subprocess.run(["cambc", *args], capture_output=True, text=True)
log = json.loads((OUT / "groups.json").read_text()) if (OUT / "groups.json").exists() else []
done = {g["team_id"] for g in log}
for prev in PREV:
    if prev["team_id"] in done:
        continue
    live = cli(["submissions", "list"]).stdout.splitlines()[:2]
    if "Live: 27" not in " ".join(live):
        sys.exit(f"stop: live version changed: {live}")
    lad = json.loads(cli(["ladder", "--page", "1", "--limit", "20", "--json"]).stdout)
    team = next((t for t in lad["teams"] if t["teamId"] == prev["team_id"]), None)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if team is None or team["rank"] > 5:
        print("skip (not top 5 now):", prev["team"], team and team["rank"])
        log.append(dict(team=prev["team"], team_id=prev["team_id"], skipped=True, rank=team and team["rank"], checked_at=now))
        (OUT / "groups.json").write_text(json.dumps(log, indent=1)); continue
    src = json.loads(prev["stdout"])["groupId"]
    r = cli(["match-groups", "create", team["teamId"], "--source-group", src, "--maps", MAPS, "--sides", prev["sides"], "--json"])
    log.append(dict(team=team["name"], team_id=team["teamId"], rank=team["rank"], rating=team["rating"], checked_at=now,
                    sides=prev["sides"], source_group=src, live=live, exit=r.returncode, stdout=r.stdout.strip(), stderr=r.stderr.strip()[-500:]))
    (OUT / "groups.json").write_text(json.dumps(log, indent=1))
    print(team["rank"], team["name"], r.returncode, r.stdout.strip()[:90], r.stderr.strip()[-200:])
    if r.returncode != 0:
        sys.exit("stop: create failed or uncertain; reconcile before retrying")
