"""Top-5 rematch for a live Chamero version: same maps, sides and opponent bots as
the v26 top-5 test. Usage: python rematch.py <live_version> <out_dir>
Rank (1-5) is rechecked before every create; a failed create stops the run and
is never retried. Then waits for all games, downloads summaries, analyzes."""
import json, subprocess, sys, time, datetime, os
from pathlib import Path
ver, out = sys.argv[1], Path(__file__).parent / sys.argv[2]
out.mkdir(exist_ok=True)
PREV = json.loads((Path(__file__).parent / "top5" / "groups.json").read_text())
MAPS = "20aedb4d-faa0-49b9-a4eb-93bea93916f5,8d9d1dc7-4386-424a-855a-b7cfc76271e3,db1fd93e-b260-45c6-b0f0-ff4252d86f10,07e14a72-a270-4f1e-ad1e-5c03b7470639,f6099a73-97ed-4b5b-8fd9-7598407f4df5"
def cli(args):
    return subprocess.run(["cambc", *args], capture_output=True, text=True)
gfile = out / "groups.json"
log = json.loads(gfile.read_text()) if gfile.exists() else []
done = {g["team_id"] for g in log}
for prev in PREV:
    if prev["team_id"] in done:
        continue
    live = cli(["submissions", "list"]).stdout.splitlines()[:2]
    if f"Live: {ver} " not in " ".join(live) + " ":
        sys.exit(f"stop: live version is not {ver}: {live}")
    lad = json.loads(cli(["ladder", "--page", "1", "--limit", "20", "--json"]).stdout)
    team = next((t for t in lad["teams"] if t["teamId"] == prev["team_id"]), None)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if team is None or team["rank"] > 5:
        print("skip (not top 5 now):", prev["team"], team and team["rank"])
        log.append(dict(team=prev["team"], team_id=prev["team_id"], skipped=True, rank=team and team["rank"], checked_at=now))
        gfile.write_text(json.dumps(log, indent=1)); continue
    src = json.loads(prev["stdout"])["groupId"]
    r = cli(["match-groups", "create", team["teamId"], "--source-group", src, "--maps", MAPS, "--sides", prev["sides"], "--json"])
    log.append(dict(team=team["name"], team_id=team["teamId"], rank=team["rank"], rating=team["rating"], checked_at=now,
                    sides=prev["sides"], source_group=src, live=live, exit=r.returncode, stdout=r.stdout.strip(), stderr=r.stderr.strip()[-500:]))
    gfile.write_text(json.dumps(log, indent=1))
    print(team["rank"], team["name"], r.returncode, r.stderr.strip()[-200:], flush=True)
    if r.returncode != 0:
        sys.exit("stop: create failed or uncertain; reconcile before retrying")
gids = [json.loads(g["stdout"])["groupId"] for g in log if not g.get("skipped")]
for _ in range(120):
    fin = 0
    for g in gids:
        r = cli(["match-groups", "show", g, "--json"])
        if r.returncode == 0:
            (out / f"show-{g}.json").write_text(r.stdout)
            fin += sum(m["status"] == "finished" for m in json.loads(r.stdout)["matches"])
        time.sleep(1)
    print("finished", fin, "/", 5 * len(gids), flush=True)
    if fin >= 5 * len(gids):
        break
    time.sleep(20)
for _ in range(6):
    missing = [m["matchId"] for g in gids for m in json.loads((out / f"show-{g}.json").read_text())["matches"]
               if not (out / f"match-{m['matchId']}.json").exists()]
    if not missing:
        break
    for m in missing:
        subprocess.run(["cambc", "matches", "summary", m, "--json"], cwd=out, capture_output=True)
        time.sleep(3)
subprocess.run([sys.executable, str(Path(__file__).parent / "top5-v27" / "analyze.py")], cwd=out, stdout=open(out / "report.txt", "w"))
print(open(out / "report.txt").read())
