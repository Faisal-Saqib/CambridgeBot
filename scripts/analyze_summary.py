#!/usr/bin/env python3
"""Deep-analyze CAMSTAT-converted match summaries: per-champ economy/combat totals."""
import json, sys
from pathlib import Path

def final(runs):
    return int(runs[-1]["value"]) if runs else 0

def series(runs, n):
    """Expand run-length timeline to per-round values."""
    out = []
    for r in runs:
        out += [int(r["value"])] * r["duration"]
    return (out + [0] * n)[:n]

def main(d):
    p = Path(d)
    files = [p] if p.is_file() else sorted(p.glob("*.json"))
    for f in files:
        j = json.loads(f.read_text())
        m = j["match"]
        teams = {t["team"]: t for t in j["teams"]}
        print(f"\n=== {f.name[:8]} {m['width']}x{m['height']} r{m['roundsCompleted']} "
              f"winner={m['outcome']} | A={teams['teamA']['submittedGems']}g B={teams['teamB']['submittedGems']}g ===")
        # per-champ final metrics
        byo = {}
        for ct in j["championTimelines"]:
            o = ct["owner"]
            if o["kind"] != "champion":
                continue
            key = (o["team"], o["name"])
            byo.setdefault(key, {})[ct["metric"]] = final(ct["runs"])
        for team in ("teamA", "teamB"):
            print(f"  {team}:")
            for (t, name), mm in sorted(byo.items()):
                if t != team:
                    continue
                print(f"    {name:<14} gold={mm.get('earnedGold',0):>5} spent={mm.get('spentGold',0):>5} "
                      f"coll={mm.get('collectedGems',0):>4} sub={mm.get('submittedGems',0):>4} "
                      f"K={mm.get('kills',0)} D={mm.get('deaths',0)} "
                      f"mdmg={mm.get('monsterDamageDone',0):>5} mtaken={mm.get('monsterDamageTaken',0):>5} "
                      f"cdmg={mm.get('championDamageDone',0):>5} ctaken={mm.get('championDamageTaken',0):>5} "
                      f"heal={mm.get('healingDone',0):>4}")
        # gem-submission curve per team
        n = m["roundsCompleted"]
        for tt in j["teamTimelines"]:
            if tt["metric"] == "submittedGems":
                s = series(tt["runs"], n)
                marks = {q: s[min(n - 1, int(n * q))] for q in (0.25, 0.5, 0.75, 1.0)}
                owner = tt["owner"]["team"] if isinstance(tt["owner"], dict) else tt["owner"]
                print(f"  {owner} submittedGems curve: "
                      f"25%={marks[0.25]} 50%={marks[0.5]} 75%={marks[0.75]} end={marks[1.0]}")
        # event kinds
        kinds = {}
        for e in j.get("events", []):
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + len(e.get("entries", []))
        if kinds:
            print("  events:", kinds)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
