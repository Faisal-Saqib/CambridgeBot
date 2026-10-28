#!/usr/bin/env python3
"""Download and summarise our online matches.

    python scripts/online_report.py --limit 30            # our latest matches
    python scripts/online_report.py --since 2026-10-27T17:00
    python scripts/online_report.py --detail <matchId-prefix>   # per-champion table

Summaries are cached under matches/online/<matchId>.json.
"""
import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "matches" / "online"
TEAM = "Quantum Wardens"


def cambc_json(*args):
    out = subprocess.run(["cambc", *args, "--json"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return json.loads(out.stdout)


def summary(match_id):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{match_id}.json"
    if not path.exists():
        subprocess.run(["cambc", "matches", "summary", match_id, "--json"], cwd=ROOT, capture_output=True)
        src = ROOT / f"match-{match_id}.json"
        if not src.exists():
            return None
        src.replace(path)
    return json.loads(path.read_text(encoding="utf-8"))


def side_stats(d, team):
    agg = defaultdict(float)
    names = []
    for c in d["champions"]:
        r = next(x for x in d["roster"]["champions"] if x["id"] == c["id"])
        if r["team"] != team:
            continue
        names.append(r["name"][:8])
        m = c["metrics"]
        for k in ("collectedGems", "submittedGems", "deaths", "kills", "earnedGold", "monsterDamageDone",
                  "championDamageDone", "championDamageTaken", "monsterDamageTaken"):
            agg[k] += float(m.get(k, 0) or 0)
    return agg, names


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--since", default="")
    ap.add_argument("--detail", default="")
    args = ap.parse_args()

    lst = cambc_json("matches", "list", "--team", "me", "--limit", str(args.limit))["matches"]
    rows = []
    for m in lst:
        if m["status"] != "finished" or m["createdAt"] < args.since:
            continue
        us = next((t for t in m["teams"] if t["name"] == TEAM), None)
        them = next((t for t in m["teams"] if t["name"] != TEAM), None)
        if not us or not them:
            continue
        if args.detail and not m["matchId"].startswith(args.detail):
            continue
        d = summary(m["matchId"])
        if not d:
            continue
        ours, theirs = "team" + us["side"].upper(), "team" + them["side"].upper()
        a, an = side_stats(d, ours)
        b, bn = side_stats(d, theirs)
        sub = {t["team"]: int(t["submittedGems"]) for t in d["teams"]}
        rows.append((m, us.get("result"), them["name"], d, ours, theirs, a, an, b, bn, sub))

    wins = sum(r[1] == "win" for r in rows)
    print(f"{wins}W-{len(rows) - wins}L over {len(rows)} matches\n")
    for m, res, opp, d, ours, theirs, a, an, b, bn, sub in rows:
        opp_s = opp.encode("ascii", "replace").decode()[:16]
        print(f"{(res or '?'):4} {m['map'][:18]:18} {opp_s:16} r{d['match']['roundsCompleted']:<5}"
              f" sub {sub[ours]:>4}-{sub[theirs]:<4} coll {a['collectedGems']:>4.0f}-{b['collectedGems']:<4.0f}"
              f" d {a['deaths']:>2.0f}-{b['deaths']:<2.0f} k {a['kills']:>2.0f}-{b['kills']:<2.0f}"
              f" gold {a['earnedGold']:>5.0f}-{b['earnedGold']:<5.0f} mDmg {a['monsterDamageDone'] / 1000:>4.0f}k-{b['monsterDamageDone'] / 1000:<4.0f}k"
              f" | {'/'.join(an)} vs {'/'.join(bn)}")
        if args.detail:
            for c in d["champions"]:
                r = next(x for x in d["roster"]["champions"] if x["id"] == c["id"])
                mm = c["metrics"]
                tag = "US " if r["team"] == ours else "opp"
                print(f"   {tag} {r['name'][:12]:12} coll {mm.get('collectedGems')!s:>4} sub {mm.get('submittedGems')!s:>4}"
                      f" d {mm.get('deaths')!s:>2} k {mm.get('kills')!s:>2} cDmg {int(float(mm.get('championDamageDone', 0))):>6}"
                      f" cTk {int(float(mm.get('championDamageTaken', 0))):>6} mDmg {int(float(mm.get('monsterDamageDone', 0))):>6}"
                      f" mTk {int(float(mm.get('monsterDamageTaken', 0))):>6} gold {int(float(mm.get('earnedGold', 0))):>5}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
