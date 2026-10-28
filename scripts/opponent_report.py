#!/usr/bin/env python3
"""Deep-dive our matches against one opponent (cached summaries from
online_report.py): economy timelines, how every death happened, builds,
consumables and drafts.

    python scripts/opponent_report.py Ascendance
"""
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEAM = "Quantum Wardens"


def value_at(runs, rnd):
    t = 0
    v = 0.0
    for r in runs:
        if t > rnd:
            break
        v = float(r["value"])
        t += r["duration"]
    return v


def main() -> int:
    opp = sys.argv[1]
    out = subprocess.run(["cambc", "matches", "list", "--team", "me", "--limit", "100", "--json"],
                         cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    ms = [m for m in json.loads(out)["matches"]
          if m["status"] == "finished" and any(t["name"] == opp for t in m["teams"])]
    totals = Counter()
    killer_types = Counter()
    gang = Counter()
    lost_gems = 0
    our_items = Counter()
    their_items = Counter()
    their_cons = Counter()
    our_cons = Counter()
    gap_rows = []
    for m in ms:
        path = ROOT / "matches" / "online" / f"{m['matchId']}.json"
        if not path.exists():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        ust = next(t for t in m["teams"] if t["name"] == TEAM)
        us = "team" + ust["side"].upper()
        them = "teamB" if us == "teamA" else "teamA"
        roster = {c["id"]: c for c in d["roster"]["champions"]}
        rounds = d["match"]["roundsCompleted"]

        # Economy timelines: gold earned and gems banked per team.
        gold = {us: defaultdict(float), them: defaultdict(float)}
        for tl in d["championTimelines"]:
            if tl["metric"] != "earnedGold":
                continue
            team = roster[tl["owner"]["id"]]["team"]
            for r in (100, 200, 300, 500, 800):
                gold[team][r] += value_at(tl["runs"], r)
        bank = {}
        for tl in d["teamTimelines"]:
            if tl["metric"] == "submittedGems":
                bank[tl["owner"]] = {r: value_at(tl["runs"], r) for r in (200, 400, 600, 800)}

        # Deaths: who killed us, how many attackers, when, what we carried.
        assists = defaultdict(set)
        for e in d["events"]:
            if e.get("kind") == "assist":
                for x in e.get("entries", []):
                    key = (x["timestamp"]["round"], x.get("target", {}).get("id"))
                    assists[key].add(e["owner"]["id"])
        deaths = []
        for e in d["events"]:
            k = e.get("kind")
            owner = e.get("owner", {})
            team = roster.get(owner.get("id"), {}).get("team")
            for x in e.get("entries", []):
                if k == "death" and team == us:
                    tgt = x.get("target", {})
                    rnd = x["timestamp"]["round"]
                    n = 1 + len(assists.get((rnd, owner["id"]), ()))
                    deaths.append((rnd, owner["name"], tgt.get("name", tgt.get("kind")), n, x["x"], x["y"]))
                    killer_types[tgt.get("name", tgt.get("kind"))] += 1
                    if tgt.get("kind") == "champion":
                        gang[n] += 1
                if k == "gemLoss" and team == us:
                    lost_gems += int(x.get("value", 0))
        deaths.sort()
        first = deaths[0][0] if deaths else None

        for c in d["champions"]:
            team = roster[c["id"]]["team"]
            items = our_items if team == us else their_items
            cons = our_cons if team == us else their_cons
            for it in c.get("itemsBought", []):
                items[it["item"].split(" Shard")[0].split(" Emblem")[0]] += int(it["quantity"])
            for cb in c.get("consumablesBought", []):
                cons[cb["consumable"]] += int(cb["quantity"])

        agg = {us: Counter(), them: Counter()}
        for c in d["champions"]:
            mm = c["metrics"]
            a = agg[roster[c["id"]]["team"]]
            for key in ("deaths", "kills", "collectedGems", "monsterDamageDone", "championDamageDone"):
                a[key] += float(mm.get(key, 0) or 0)
        for key in ("deaths", "kills"):
            totals["our_" + key] += agg[us][key]
            totals["their_" + key] += agg[them][key]
        totals["games"] += 1
        totals["wins"] += ust.get("result") == "win"

        ours = "/".join(c["name"][:7] for c in d["roster"]["champions"] if c["team"] == us)
        theirs = "/".join(c["name"][:7] for c in d["roster"]["champions"] if c["team"] == them)
        print(f"== {m['map']} {ust.get('result')} r{rounds}  {ours}  vs  {theirs}")
        print("   gold  r100 {:>5.0f}-{:<5.0f} r200 {:>5.0f}-{:<5.0f} r300 {:>5.0f}-{:<5.0f} r500 {:>5.0f}-{:<5.0f} r800 {:>5.0f}-{:<5.0f}".format(
            *[v for r in (100, 200, 300, 500, 800) for v in (gold[us][r], gold[them][r])]))
        if us in bank and them in bank:
            print("   bank  r200 {:>4.0f}-{:<4.0f} r400 {:>4.0f}-{:<4.0f} r600 {:>4.0f}-{:<4.0f} r800 {:>4.0f}-{:<4.0f}".format(
                *[v for r in (200, 400, 600, 800) for v in (bank[us][r], bank[them][r])]))
        print(f"   deaths {agg[us]['deaths']:.0f}-{agg[them]['deaths']:.0f}  kills {agg[us]['kills']:.0f}-{agg[them]['kills']:.0f}"
              f"  monsterDmg {agg[us]['monsterDamageDone'] / 1000:.0f}k-{agg[them]['monsterDamageDone'] / 1000:.0f}k"
              f"  champDmg {agg[us]['championDamageDone'] / 1000:.0f}k-{agg[them]['championDamageDone'] / 1000:.0f}k  first death r{first}")
        print("   our deaths (round victim<-killer xAttackers @pos):",
              " ".join(f"r{r} {v[:5]}<-{k[:5]}x{n}" for r, v, k, n, _, _ in deaths[:12]))
        gap_rows.append((m["map"], gold[us][300], gold[them][300]))

    print(f"\nRECORD {totals['wins']:.0f}-{totals['games'] - totals['wins']:.0f}  deaths {totals['our_deaths']:.0f} vs {totals['their_deaths']:.0f}"
          f"  kills {totals['our_kills']:.0f} vs {totals['their_kills']:.0f}  carried gems lost on death: {lost_gems}")
    print("killed by:", dict(killer_types.most_common()))
    print("attackers per champion kill on us:", dict(sorted(gang.items())))
    print("our items bought:  ", dict(our_items.most_common()))
    print("their items bought:", dict(their_items.most_common()))
    print("our consumables:   ", dict(our_cons))
    print("their consumables: ", dict(their_cons))
    return 0


if __name__ == "__main__":
    sys.exit(main())
