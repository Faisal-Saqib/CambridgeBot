#!/usr/bin/env python3
"""Deep per-map analysis from downloaded top-20 ranked summaries.

For every published map, aggregates over winning top-20 team-games:
  - camp clear positions + rounds  -> which camps winners hit, and when
  - draft composition               -> winning draft per map
  - buyItem rounds                  -> early/mid/late item plan
  - consumables / wards / tribute   -> objective behaviour
  - kills/deaths timing + position  -> fight profile
  - collected/submitted/camp damage -> economy shape

Emits docs/maps/plan/<map>.md plus docs/MAP_PLANS.md index.
Points are labelled [measured] (downloaded evidence) or [derived]/[hypothesis].
"""
import json, os, statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCOUT = ROOT / "matches" / "top20-scout"
SUM = SCOUT / "summaries"
LISTS = SCOUT / "lists"
SHAPES = ROOT / "matches" / "map_shapes.json"
OUTDIR = ROOT / "docs" / "maps" / "plan"
INDEX = ROOT / "docs" / "MAP_PLANS.md"

def num(v):
    try: return float(v)
    except Exception: return 0.0

def load(p):
    for enc in ("utf-16", "utf-8-sig", "utf-8"):
        try: return json.load(open(p, encoding=enc))
        except Exception: continue
    return None

# ---------- matchId -> (map, winner_side) ----------
meta = {}
for fn in os.listdir(LISTS):
    d = load(LISTS / fn)
    if not d: continue
    for m in d.get("matches", []):
        if m.get("status") != "finished": continue
        w = next((t for t in m["teams"] if t["result"] == "win"), None)
        l = next((t for t in m["teams"] if t["result"] != "win"), None)
        meta[m["matchId"]] = dict(map=m["map"],
                                  wside=("team" + w["side"].upper()) if w else None,
                                  lside=("team" + l["side"].upper()) if l else None,
                                  winner=(w or {}).get("name"))

shapes = load(SHAPES) or {}

# ---------- per-map aggregation ----------
maps = defaultdict(lambda: dict(
    games=0, wg=0, lg=0, wdims=None,
    wdrafts=Counter(), ldrafts=Counter(), winners=Counter(),
    camps=defaultdict(lambda: [0, []]),          # (x,y) -> [count, rounds]
    ocamps=defaultdict(lambda: [0, []]),         # losing side's clears
    items_phase=defaultdict(Counter),            # phase -> item family counts (winners)
    items_raw=Counter(), oitems_raw=Counter(),
    cons=Counter(), ocons=Counter(),
    trib=[], otrib=[], kills=[], deaths=[], okills=[], odeaths=[],
    col=[], ocol=[], sub=[], osub=[], cd=[], ocd=[], gold=[], ogold=[],
    heal=[], wards=[], owards=[], firstkill=[], firstdeath=[], rounds=[],
))

PHASES = lambda r: 0 if r < 150 else (1 if r < 500 else 2)

def phase_name(i): return ("early (r<150)", "mid (150-500)", "late (r>500)")[i]

def quadrant(x, y, w, h):
    cx, cy = x / w, y / h
    ns = "N" if cy < 0.33 else ("S" if cy > 0.67 else "")
    ew = "W" if cx < 0.33 else ("E" if cx > 0.67 else "")
    return (ns + ew) or "center"

for fn in os.listdir(SUM):
    mid = fn[:-5]
    m = meta.get(mid)
    if not m or not m["wside"]: continue
    d = load(SUM / fn)
    if not d: continue
    mp = m["map"]; wside = m["wside"]; lside = m["lside"]
    R = maps[mp]; R["games"] += 1; R["wg"] += 1
    R["wdims"] = (d["match"]["width"], d["match"]["height"])
    R["rounds"].append(d["match"]["roundsCompleted"])
    if m["winner"]: R["winners"][m["winner"]] += 1
    wchamps = [c for c in d["champions"] if c["team"] == wside]
    lchamps = [c for c in d["champions"] if c["team"] != wside]
    R["wdrafts"][tuple(sorted(c["name"] for c in wchamps))] += 1
    R["ldrafts"][tuple(sorted(c["name"] for c in lchamps))] += 1
    agg = lambda ch, k: sum(num(c["metrics"].get(k)) for c in ch)
    R["kills"].append(agg(wchamps, "kills")); R["deaths"].append(agg(wchamps, "deaths"))
    R["okills"].append(agg(lchamps, "kills")); R["odeaths"].append(agg(lchamps, "deaths"))
    R["col"].append(agg(wchamps, "collectedGems")); R["ocol"].append(agg(lchamps, "collectedGems"))
    R["cd"].append(agg(wchamps, "monsterDamageDone")); R["ocd"].append(agg(lchamps, "monsterDamageDone"))
    R["gold"].append(agg(wchamps, "earnedGold")); R["ogold"].append(agg(lchamps, "earnedGold"))
    R["heal"].append(agg(wchamps, "healingDone"))
    sa, sb = num(d["teams"][0]["submittedGems"]), num(d["teams"][1]["submittedGems"])
    R["sub"].append(sa if wside == "teamA" else sb); R["osub"].append(sb if wside == "teamA" else sa)
    w_items = Counter(); l_items = Counter()
    for c in wchamps:
        for e in c.get("itemsBought", []):
            try: q = int(e.get("quantity", "1"))
            except Exception: q = 1
            w_items[e["item"]] += q
        for e in c.get("consumablesBought", []):
            try: q = int(e.get("quantity", "1"))
            except Exception: q = 1
            R["cons"][e["consumable"]] += q
    for c in lchamps:
        for e in c.get("itemsBought", []):
            try: q = int(e.get("quantity", "1"))
            except Exception: q = 1
            l_items[e["item"]] += q
        for e in c.get("consumablesBought", []):
            try: q = int(e.get("quantity", "1"))
            except Exception: q = 1
            R["ocons"][e["consumable"]] += q
    R["items_raw"].update(w_items); R["oitems_raw"].update(l_items)
    kr = []; dr = []; wr = 0; owr = 0
    for e in d["events"]:
        k = e["kind"]; ot = (e.get("owner") or {}).get("team")
        for en in e.get("entries", []):
            r = en["timestamp"]["round"]
            if k == "campClear":
                x, y = en.get("x"), en.get("y")
                if x is None: continue
                tgt = R["camps"] if ot == wside else R["ocamps"]
                # dedupe into existing camp cluster within 4 tiles
                hit = None
                for (cx, cy) in tgt:
                    if abs(cx - x) <= 4 and abs(cy - y) <= 4: hit = (cx, cy); break
                if hit is None: hit = (x, y)
                tgt[hit][0] += 1; tgt[hit][1].append(r)
            elif k == "buyItem" and ot == wside:
                nm = (en.get("target") or {}).get("name", "?")
                fam = nm.split(" ")[0] if nm != "?" else "?"
                stat = "Strength" if "Strength" in nm else ("Focus" if "Focus" in nm else ("Health" if "Health" in nm else "?"))
                R["items_phase"][PHASES(r)][f"{fam}/{stat}"] += 1
            elif k == "gemSubmission" and ot == wside:
                R["trib"].append((r, num(en.get("value"))))
            elif k == "gemSubmission" and ot == lside:
                R["otrib"].append((r, num(en.get("value"))))
            elif k == "wardPlacement":
                if ot == wside: wr += 1
                elif ot == lside: owr += 1
            elif k == "kill":
                (kr if ot == wside else dr).append(r)
    R["wards"].append(wr); R["owards"].append(owr)
    if kr: R["firstkill"].append(min(kr))
    if dr: R["firstdeath"].append(min(dr))

OUTDIR.mkdir(parents=True, exist_ok=True)
index = ["# Map plans — deep per-map strategy", "",
         "Generated by `scripts/map_deep.py` from matches/top20-scout (downloaded ranked",
         "summaries of the current top-20 teams). Each plan aggregates *winning* team-games",
         "on that map: camps hit and when, drafts, item timeline, tributes, wards, fights.",
         "Labels: [measured] downloaded evidence · [derived] computed from evidence ·",
         "[hypothesis] proposal not yet validated.", "", "| Map | Games | Win drafts | Early camps | Tribute |", "|---|---|---|---|---|"]

for mp in sorted(maps):
    R = maps[mp]; n = R["games"]
    w, h = R["wdims"] or (0, 0)
    sh = shapes.get(mp, {})
    def avg(xs): return sum(xs) / len(xs) if xs else 0.0
    L = []
    L.append(f"# {mp} — deep plan")
    L.append("")
    L.append(f"Sample: **{n} winning top-20 team-games** · map {w}x{h} · "
             f"altars {sh.get('altars','?')} · gap-separated gems {sh.get('unreach','?')}/{sh.get('total','?')}")
    L.append("")
    # winners
    tops = ", ".join(f"{t} x{c}" for t, c in R["winners"].most_common(4))
    L.append(f"Winning teams here: {tops}")
    L.append("")
    # outcome stats
    L.append("## Winners' numbers (per game)")
    L.append("")
    L.append(f"- Score {avg(R['sub']):.0f} vs loser {avg(R['osub']):.0f} · "
             f"collected {avg(R['col']):.0f} vs {avg(R['ocol']):.0f} · "
             f"camp damage {avg(R['cd'])/1000:.0f}k vs {avg(R['ocd'])/1000:.0f}k")
    L.append(f"- Kills {avg(R['kills']):.1f} vs {avg(R['okills']):.1f} · "
             f"deaths {avg(R['deaths']):.1f} vs {avg(R['odeaths']):.1f} · "
             f"game length ~{avg(R['rounds']):.0f} rounds")
    L.append(f"- Gold {avg(R['gold']):.0f} vs {avg(R['ogold']):.0f} · "
             f"healing {avg(R['heal'])/1000:.1f}k · wards {avg(R['wards']):.0f} vs {avg(R['owards']):.0f}")
    if R["firstkill"]: L.append(f"- First kill ~round {statistics.median(R['firstkill']):.0f} · "
                               f"first death ~round {statistics.median(R['firstdeath']):.0f}" if R["firstdeath"] else "")
    L.append("")
    # draft
    L.append("## Draft")
    L.append("")
    for dr, c in R["wdrafts"].most_common(4):
        L.append(f"- **{c}x** {' + '.join(dr)}")
    if R["ldrafts"]:
        L.append("")
        L.append("Losing drafts seen here: " + "; ".join(f"{' + '.join(d)} x{c}" for d, c in R["ldrafts"].most_common(2)))
    L.append("")
    # camps by phase
    L.append("## Camps winners attack — and when")
    L.append("")
    camps_sorted = sorted(R["camps"].items(), key=lambda kv: -kv[1][0])
    early, midp, late = [], [], []
    for (x, y), (cnt, rounds) in camps_sorted:
        med = statistics.median(rounds)
        q = quadrant(x, y, w or 1, h or 1)
        rec = f"{q} ({x},{y}) cleared {cnt}x, median r{med:.0f}"
        (early if med < 150 else midp if med < 500 else late).append(rec)
    for lbl, lst in (("Early (median clear < r150)", early), ("Mid (150-500)", midp), ("Late (>500)", late)):
        if lst:
            L.append(f"**{lbl}:**")
            for r_ in lst[:8]: L.append(f"- {r_}")
            L.append("")
    # items by phase
    L.append("## Buy plan (winners' purchases by phase)")
    L.append("")
    for ph in range(3):
        if R["items_phase"][ph]:
            top = ", ".join(f"{k} x{v}" for k, v in R["items_phase"][ph].most_common(6))
            L.append(f"- **{phase_name(ph)}**: {top}")
    L.append("")
    if R["cons"]:
        L.append("Consumables bought by winners: " + ", ".join(f"{k} x{v} ({v/n:.1f}/game)" for k, v in R["cons"].most_common()))
        L.append("")
    # tribute
    if R["trib"]:
        sizes = [v for _, v in R["trib"]]
        L.append(f"## Tributes: {len(R['trib'])/n:.1f}/game, avg size {sum(sizes)/len(sizes):.0f}, "
                 f"median round {statistics.median(r for r,_ in R['trib']):.0f}")
        L.append("")
    # fight profile
    fighty = avg(R["kills"]) + avg(R["deaths"]) > 15
    L.append("## Game plan")
    L.append("")
    if fighty:
        L.append("- [derived] **Fight map**: winners here fight (~{:.0f} kills/game) — group for".format(avg(R['kills'])) +
                 " engagements, focus the carrier, tribute before fighting.")
    else:
        L.append("- [derived] **Farm map**: winners here out-farm ({:.0f} vs {:.0f} collected) —".format(avg(R['col']), avg(R['ocol'])) +
                 " spread wide, avoid fights unless free kills.")
    if early:
        L.append(f"- [measured] Open on the **{early[0].split(' ')[0]}** camps — winners clear them before r150.")
    if late:
        L.append("- [measured] Save the hardest camps for late — winners only touch them after r500.")
    if sh.get("unreach", 0) and sh["unreach"] / max(sh.get("total", 1), 1) > 0.05:
        L.append(f"- [derived] **Gap-separated**: {sh['unreach']}/{sh['total']} gems unreachable on foot — one crystal/dash hopper mandatory.")
    if avg(R["trib"] and [v for _, v in R["trib"]] or [0]) and R["trib"]:
        L.append(f"- [measured] Bank ~{sorted(v for _,v in R['trib'])[len(R['trib'])//2]:.0f} gems per tribute at the nearest altar.")
    L.append("")
    L.append("---")
    (OUTDIR / f"{mp}.md").write_text("\n".join(L), encoding="utf-8")
    wdr = R["wdrafts"].most_common(1)[0][0] if R["wdrafts"] else ()
    index.append(f"| [{mp}](maps/plan/{mp}.md) | {n} | {' + '.join(wdr)[:40]} | {len(early)} | {len(R['trib'])/n:.0f} |")

INDEX.write_text("\n".join(index), encoding="utf-8")
print(f"wrote {len(maps)} map plans + index")
