"""Queue one 5-map unranked group against each of the current top-5 teams.
Rank is rechecked right before every create; an uncertain create stops the run."""
import json, subprocess, sys, datetime
from pathlib import Path
OUT = Path(__file__).parent
MAPS = "20aedb4d-faa0-49b9-a4eb-93bea93916f5,8d9d1dc7-4386-424a-855a-b7cfc76271e3,db1fd93e-b260-45c6-b0f0-ff4252d86f10,07e14a72-a270-4f1e-ad1e-5c03b7470639,f6099a73-97ed-4b5b-8fd9-7598407f4df5"
def cli(args):
    return subprocess.run(["cambc", *args], capture_output=True, text=True)
log = json.loads((OUT / "groups.json").read_text()) if (OUT / "groups.json").exists() else []
done = {g["rank_slot"] for g in log}
for slot in range(1, 6):
    if slot in done:
        continue
    live = cli(["submissions", "list"]).stdout.splitlines()[:2]
    if "Live: 26" not in " ".join(live):
        sys.exit(f"stop: live version changed: {live}")
    lad = json.loads(cli(["ladder", "--page", "1", "--limit", "20", "--json"]).stdout)
    team = next(t for t in lad["teams"] if t["rank"] == slot)
    sides = "a,b,a,b,a" if slot % 2 else "b,a,b,a,b"
    now = datetime.datetime.utcnow().isoformat() + "Z"
    r = cli(["match-groups", "create", team["teamId"], "--maps", MAPS, "--sides", sides, "--json"])
    rec = dict(rank_slot=slot, team=team["name"], team_id=team["teamId"], rank=team["rank"], rating=team["rating"],
               checked_at=now, sides=sides, live=live, exit=r.returncode, stdout=r.stdout.strip(), stderr=r.stderr.strip()[-500:])
    log.append(rec)
    (OUT / "groups.json").write_text(json.dumps(log, indent=1))
    print(slot, team["name"], r.returncode, r.stdout.strip()[:120], r.stderr.strip()[-200:])
    if r.returncode != 0:
        sys.exit("stop: create failed or uncertain; reconcile before retrying")
