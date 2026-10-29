#!/usr/bin/env python3
"""Extract each top-3 team's per-map strategy from downloaded ranked games.

For each of rank-01/02/03 (Mite, Intercontinental Fish, newer team), aggregates
their own team-games per map: draft, opening camps (positions + clear timing),
item timeline, consumables, tributes, kills/deaths, spread.

Emits docs/TOP3_STRATEGIES.md (per-team per-map) and data for the combined doc.
"""
import json, os, statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCOUT = ROOT / "matches" / "top20-scout"
SUM = SCOUT / "summaries"; LISTS = SCOUT / "lists"
OUT = ROOT / "docs" / "TOP3_STRATEGIES.md"

def num(v):
    try: return float(v)
    except Exception: return 0.0

def load(p):
    for enc in ("utf-16", "utf-8-sig", "utf-8"):
        try: return json.load(open(p, encoding=enc))
        except Exception: continue
    return None

TEAMS = {}   # list file -> team name; matches -> team side
team_meta = {}
for fn in sorted(os.listdir(LISTS)):
    if not fn.startswith(("rank-01", "rank-02", "rank-03")): continue
    d = load(LISTS / fn)
    ms = d["matches"]
    names = Counter(t["name"] for m in ms for t in m["teams"])
    owner = names.most_common(1)[0][0]
    rank = fn.split("-")[1]
    team_meta[owner] = []
    for m in ms:
        if m.get("status") != "finished": continue
        t = next(t for t in m["teams"] if t["name"] == owner)
        team_meta[owner].append(dict(mid=m["matchId"], map=m["map"],
                                     side="team" + t["side"].upper(),
                                     win=t["result"] == "win"))
print({k: len(v) for k, v in team_meta.items()})

PH = lambda r: 0 if r < 150 else (1 if r < 500 else 2)

def agg_game(d, side):
    ch = [c for c in d["champions"] if c["team"] == side]
    agg = lambda k: sum(num(c["metrics"].get(k)) for c in ch)
    items = Counter(); cons = Counter(); buy_phase = defaultdict(Counter)
    for c in ch:
        for e in c.get("itemsBought", []):
            try: q = int(e.get("quantity", "1"))
            except Exception: q = 1
            items[e["item"]] += q
        for e in c.get("consumablesBought", []):
            try: q = int(e.get("quantity", "1"))
            except Exception: q = 1
            cons[e["consumable"]] += q
    camps = {}; trib = []; wards = 0; kr = []; dr = []
    for e in d["events"]:
        k = e["kind"]; ot = (e.get("owner") or {}).get("team")
        for en in e.get("entries", []):
            r = en["timestamp"]["round"]
            if k == "campClear" and ot == side and en.get("x") is not None:
                x, y = en["x"], en["y"]
                hit = None
                for (cx, cy) in camps:
                    if abs(cx - x) <= 4 and abs(cy - y) <= 4: hit = (cx, cy); break
                camps.setdefault(hit or (x, y), []).append(r)
            elif k == "buyItem" and ot == side:
                nm = (en.get("target") or {}).get("name", "?")
                fam = nm.split(" ")[0]; st = "Str" if "Strength" in nm else ("Foc" if "Focus" in nm else ("HP" if "Health" in nm else "?"))
                buy_phase[PH(r)][f"{fam}/{st}"] += 1
            elif k == "gemSubmission" and ot == side: trib.append((r, num(en.get("value"))))
            elif k == "wardPlacement" and ot == side: wards += 1
            elif k == "kill": (kr if ot == side else dr).append(r)
    sa, sb = num(d["teams"][0]["submittedGems"]), num(d["teams"][1]["submittedGems"])
    return dict(
        draft=tuple(sorted(c["name"] for c in ch)),
        score=sa if side == "teamA" else sb,
        kills=agg("kills"), deaths=agg("deaths"), col=agg("collectedGems"),
        sub=agg("submittedGems"), cd=agg("monsterDamageDone"), gold=agg("earnedGold"),
        heal=agg("healingDone"), items=items, cons=cons, camps=camps, trib=trib,
        wards=wards, kfirst=min(kr) if kr else None, dfirst=min(dr) if dr else None,
        buy_phase=buy_phase, rounds=d["match"]["roundsCompleted"],
        w=d["match"]["width"], h=d["match"]["height"])

def qd(x, y, w, h):
    ns = "N" if y / h < 0.33 else ("S" if y / h > 0.67 else "")
    ew = "W" if x / w < 0.33 else ("E" if x / w > 0.67 else "")
    return (ns + ew) or "C"

# ---------- aggregate ----------
per = defaultdict(lambda: defaultdict(list))   # team -> map -> [game]
for team, games in team_meta.items():
    for g in games:
        p = SUM / f"{g['mid']}.json"
        if not p.exists(): continue
        d = load(p)
        if not d: continue
        r = agg_game(d, g["side"]); r["win"] = g["win"]
        per[team][g["map"]].append(r)

L = ["# Top-3 teams — per-map strategy copies", "",
     "Mite (rank ~1), Intercontinental Fish (rank ~2), newer team (rank ~3) at",
     "scout-capture time. Each section: their games on that map, what they draft,",
     "which camps they hit first, what they buy and when, tribute/fight profile.",
     "All numbers measured from their ranked summaries.", ""]

for team in ("Mite", "Intercontinental Fish", "newer team"):
    tm = per[team]
    n = sum(len(v) for v in tm.values())
    w = sum(1 for v in tm.values() for g in v if g["win"])
    L.append(f"# {team} — {w}/{n} wins")
    L.append("")
    # signature draft overall
    all_drafts = Counter(g["draft"] for v in tm.values() for g in v)
    L.append("**Signature drafts:** " + "; ".join(f"{' + '.join(d)} x{c}" for d, c in all_drafts.most_common(3)))
    L.append("")
    for mp in sorted(tm, key=lambda k: -len(tm[k])):
        gs = tm[mp]; wg = [g for g in gs if g["win"]]
        use = wg if wg else gs   # learn from wins if any
        nw = len(use)
        av = lambda f: sum(f(g) for g in use) / nw
        L.append(f"## {mp} — {len(wg)}/{len(gs)} wins")
        # draft
        dr = Counter(g["draft"] for g in use).most_common(1)[0]
        L.append(f"- Draft: {' + '.join(dr[0])} (x{dr[1]})")
        # opening camps: camps with median first-clear < r200
        allc = defaultdict(list)
        for g in use:
            for (x, y), rs in g["camps"].items():
                allc[(x, y)].extend(rs)
        early = sorted(((statistics.median(rs), qd(x, y, gs[0]["w"], gs[0]["h"]), len(rs)) for (x, y), rs in allc.items()))
        if early:
            op = [f"{q}({c}x~r{m:.0f})" for m, q, c in early if m < 200][:6]
            if op: L.append(f"- Opens on: {', '.join(op)}")
        # stats line
        L.append(f"- Score {av(lambda g: g['score']):.0f} · kills {av(lambda g: g['kills']):.1f}/deaths {av(lambda g: g['deaths']):.1f} · "
                 f"col {av(lambda g: g['col']):.0f} · camp {av(lambda g: g['cd'])/1000:.0f}k · gold {av(lambda g: g['gold']):.0f} · wards {av(lambda g: g['wards']):.0f}")
        # buy phases
        bp = defaultdict(Counter)
        for g in use:
            for i, cnt in g["buy_phase"].items(): bp[i].update(cnt)
        seg = []
        for i in range(3):
            if bp[i]: seg.append(f"r{'<150' if i==0 else '150-500' if i==1 else '>500'}: " + ", ".join(f"{k}~{v/nw:.0f}" for k, v in bp[i].most_common(3)))
        if seg: L.append("- Buys: " + " | ".join(seg))
        # consumables + tribute
        ctot = Counter()
        for g in use: ctot.update(g["cons"])
        if ctot: L.append("- Consumables: " + ", ".join(f"{k} {v/nw:.1f}/g" for k, v in ctot.most_common()))
        tr = [t for g in use for t in g["trib"]]
        if tr: L.append(f"- Tributes: {len(tr)/nw:.1f}/g avg {sum(v for _,v in tr)/len(tr):.0f} first ~r{min(r for r,_ in tr)}")
        fk = [g["kfirst"] for g in use if g["kfirst"]]; fd = [g["dfirst"] for g in use if g["dfirst"]]
        if fk: L.append(f"- First kill ~r{statistics.median(fk):.0f}" + (f", first death ~r{statistics.median(fd):.0f}" if fd else ""))
        L.append("")

OUT.write_text("\n".join(L), encoding="utf-8")
print("wrote", OUT)
