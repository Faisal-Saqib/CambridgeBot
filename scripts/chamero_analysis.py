#!/usr/bin/env python3
"""Independent analysis of Chamero online matches (v25-v30 campaigns).

Reads every match-*.json under bots/Chamero/online (campaign dirs and root g1/g2
files), resolves map names and sides through show-*.json / g*-show.json files,
and emits docs/CHAMERO_ANALYSIS.md plus matches/chamero-analysis.json.
"""
import json, glob, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONLINE = os.path.join(ROOT, "bots", "Chamero", "online")
OUR_TEAM_ID = "b224cf2f-1e0f-44e1-9546-b574f39cd9eb"
OUR_NAME = "Quantum Wardens"

VERSIONS = {
    "top5": "v26", "top5-v27": "v27", "top5-v28": "v28",
    "top5-v29": "v29", "top5-v30": "v30", "": "v25/26",
}

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0

def load_shows(d):
    """match_id -> (map, our_side 'teamA'/'teamB', opponent name)."""
    out = {}
    for pat in ("show-*.json", "g*-show.json"):
        for f in glob.glob(os.path.join(d, pat)):
            try: g = json.load(open(f, encoding="utf-8"))
            except Exception: continue
            for m in g.get("matches", []):
                ours = None
                for t in m.get("teams", []):
                    if t.get("teamId") == OUR_TEAM_ID or t.get("name") == OUR_NAME:
                        ours = "teamA" if t["side"] == "a" else "teamB"
                        opp = [x["name"] for x in m["teams"] if x is not t]
                        out[m["matchId"]] = (m.get("map"), ours, opp[0] if opp else "?")
    return out

def champ_stats(chs, side):
    r = {"deaths":0,"kills":0,"campdmg":0.0,"champdmg":0.0,"gold":0.0,
         "collected":0,"submitted":0,"gems_held_end":0,"items":collections.Counter(),
         "cons":collections.Counter(),"per_champ":[]}
    for c in chs:
        if c["team"] != side: continue
        m = c["metrics"]
        d_ = int(num(m.get("deaths"))); k = int(num(m.get("kills")))
        r["deaths"] += d_; r["kills"] += k
        r["campdmg"] += num(m.get("monsterDamageDone"))
        r["champdmg"] += num(m.get("championDamageDone"))
        r["gold"] += num(m.get("earnedGold"))
        r["collected"] += num(m.get("collectedGems"))
        r["submitted"] += num(m.get("submittedGems"))
        r["gems_held_end"] += num(m.get("gems"))
        for ib in c.get("itemsBought", []):
            r["items"][ib["item"]] += int(num(ib.get("quantity")))
        for cb in c.get("consumablesBought", []):
            r["cons"][cb["consumable"]] += int(num(cb.get("quantity")))
        r["per_champ"].append({
            "name": c["name"], "deaths": d_, "kills": k,
            "campdmg": num(m.get("monsterDamageDone")),
            "collected": num(m.get("collectedGems")),
            "submitted": num(m.get("submittedGems")),
            "gold": num(m.get("earnedGold")),
        })
    return r

def main():
    games = []
    for f in sorted(glob.glob(os.path.join(ONLINE, "**", "match-*.json"), recursive=True)):
        d = json.load(open(f, encoding="utf-8"))
        ddir = os.path.dirname(f)
        rel = os.path.relpath(ddir, ONLINE)
        ver = VERSIONS.get(rel if rel != "." else "", "?")
        mid = os.path.basename(f)[6:-5]
        games.append((f, d, ver, mid, ddir))
    # resolve show metadata per directory
    shows = {}
    for ddir in {g[4] for g in games} | {ONLINE}:
        shows.update(load_shows(ddir))

    rows = []
    for f, d, ver, mid, ddir in games:
        mapname, ours, opp = shows.get(mid, ("?", "teamA", "?"))
        theirs = "teamB" if ours == "teamA" else "teamA"
        us = champ_stats(d["champions"], ours)
        them = champ_stats(d["champions"], theirs)
        won = d["match"]["outcome"] == ours
        faults = d.get("diagnostics", {}).get("botFaults", {})
        # gem loss = collected - submitted - held at end
        lost_us = us["collected"] - us["submitted"] - us["gems_held_end"]
        lost_them = them["collected"] - them["submitted"] - them["gems_held_end"]
        # tribute curve: first/last banked-gem jumps
        tt = {t["owner"]: t for t in d.get("teamTimelines", []) if t["metric"] == "submittedGems"}
        def first_bank_round(side):
            t = tt.get(side)
            if not t: return None
            last = 0
            for r in t.get("runs", []):
                if num(r.get("value", r.get("v", 0))) > last:
                    return r.get("round", r.get("startRound"))
            return None
        rows.append({
            "file": f, "ver": ver, "match": mid, "map": mapname, "opp": opp,
            "our_side": ours, "won": won,
            "score_us": int(num(next((t["submittedGems"] for t in d["teams"] if t["team"] == ours), 0))),
            "score_them": int(num(next((t["submittedGems"] for t in d["teams"] if t["team"] == theirs), 0))),
            "rounds": d["match"]["roundsCompleted"],
            "us": us, "them": them,
            "lost_us": lost_us, "lost_them": lost_them,
            "fault_us": faults.get(ours, 0), "fault_them": faults.get(theirs, 0),
            "draft_us": [x["champion"] for x in d["roster"]["draft"] if x["team"] == ours],
            "draft_them": [x["champion"] for x in d["roster"]["draft"] if x["team"] == theirs],
        })
    outp = os.path.join(ROOT, "matches", "chamero-analysis.json")
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    json.dump(rows, open(outp, "w", encoding="utf-8"), indent=1, default=str)
    print(f"games: {len(rows)}")
    for r in rows:
        print(r["ver"], r["map"], r["opp"][:20].ljust(20), "W" if r["won"] else "L",
              f'{r["score_us"]}-{r["score_them"]}', f'd{r["us"]["deaths"]}/k{r["us"]["kills"]}')

if __name__ == "__main__":
    main()
