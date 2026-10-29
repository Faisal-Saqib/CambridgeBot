"""Create panel 2: one group vs each team currently ranked 6-10 on five new maps
(anvil, stampede, starfish, fields, galaxy). These groups become the opponent-bot
source for every later version (rematch.py panel2). Stops on any failed create."""
import json, subprocess, sys, datetime
from pathlib import Path
OUT = Path(__file__).parent
MAPS = "001efcd1-42cd-4fe6-b8d1-b906b4713009,aa9038e8-9700-41a9-b6c5-8b17694b913b,541f522e-19b8-45e8-adaa-db87213672a0,c7026f58-b3cb-4a90-a552-25cb47a2fb01,d7814873-ceeb-4f96-930e-831c389d7f4d"
ver = sys.argv[1]
def cli(a): return subprocess.run(["cambc", *a], capture_output=True, text=True)
gfile = OUT / "groups.json"
log = json.loads(gfile.read_text()) if gfile.exists() else []
done = {g["rank_slot"] for g in log}
for slot in range(6, 11):
    if slot in done: continue
    live = cli(["submissions", "list"]).stdout.splitlines()[:2]
    if f"Live: {ver} " not in " ".join(live) + " ": sys.exit(f"stop: live is not {ver}: {live}")
    lad = json.loads(cli(["ladder", "--page", "1", "--limit", "20", "--json"]).stdout)
    team = next(t for t in lad["teams"] if t["rank"] == slot)
    sides = "a,b,a,b,a" if slot % 2 == 0 else "b,a,b,a,b"
    r = cli(["match-groups", "create", team["teamId"], "--maps", MAPS, "--sides", sides, "--json"])
    log.append(dict(rank_slot=slot, team=team["name"], team_id=team["teamId"], rank=team["rank"], rating=team["rating"],
                    checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), sides=sides, live=live,
                    exit=r.returncode, stdout=r.stdout.strip(), stderr=r.stderr.strip()[-500:]))
    gfile.write_text(json.dumps(log, indent=1))
    print(slot, team["name"], r.returncode, r.stderr.strip()[-200:], flush=True)
    if r.returncode != 0: sys.exit("stop: create failed or uncertain")
