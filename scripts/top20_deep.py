#!/usr/bin/env python3
"""Deep analysis of top-20 team behavior across all downloaded summaries.

Reads matches/top20-scout/summaries/*.json + manifest + lists (for map names),
aggregates per (team, champion) and per team, and writes
matches/top20-scout/deep.json plus docs/TOP20_DEEP_ANALYSIS.md.
Offline only — never calls cambc.
"""
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / "matches" / "top20-scout"
OUT_JSON = FOLDER / "deep.json"
OUT_MD = ROOT / "docs" / "TOP20_DEEP_ANALYSIS.md"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def item_kind(name):
    parts = name.split()
    return ("shard" if "Shard" in name else "emblem" if "Emblem" in name else "other")


def item_family(name):
    return name.split()[0]


def item_stat(name):
    return name.split()[-1]


def entries(data, kind):
    for event in data["events"]:
        if event["kind"] == kind:
            for e in event["entries"]:
                yield event["owner"], e


def main():
    manifest = load(FOLDER / "manifest.json")
    meta = {mid: e["match"] for mid, e in manifest["selection"].items()}
    # matches outside the 2/map selection still need map names -> merge lists
    for p in (FOLDER / "lists").glob("*.json"):
        for m in load(p)["matches"]:
            meta.setdefault(m["matchId"], m)
    ladder = load(FOLDER / "ladder.json")
    top20 = {t["teamId"]: t for t in ladder["teams"] if t["rank"] <= 20}
    id2name = {tid: t["name"] for tid, t in top20.items()}

    teams = defaultdict(lambda: {
        "games": 0, "wins": 0, "maps": Counter(),
        "drafts": Counter(),            # tuple of picks
        "champ": defaultdict(lambda: {
            "games": 0, "wins": 0, "kills": 0, "deaths": 0, "assists": 0,
            "earnedGold": 0.0, "spentGold": 0.0, "damage": 0.0,
            "collected": 0.0, "submitted": 0.0,
            "captures": 0, "solo_captures": 0,
            "wards": 0, "clears": 0,
            "shards": Counter(), "emblems": Counter(),
            "consumables": Counter(),
            "xs": [], "ys": [], "first_clear_rounds": [],
        }),
        "tribute_sizes": [], "tribute_rounds": [],
        "kills": 0, "deaths": 0, "camp_deaths": 0,
        "submitted": 0.0, "gem_loss": 0.0,
        "wards": 0, "ward_rounds": [], "ward_cdist": [],
        "lock_rounds": [], "crystal_uses": 0,
        "attackers_per_kill": [], "solo_capture_share": [],
        "carry_share": [], "spread": [],
        "altar_tiles": Counter(),
        "win_rounds": [], "loss_rounds": [],
    })
    match_count = 0
    champ_tot = defaultdict(lambda: Counter())   # global per champion name
    team_names = set()

    for path in sorted((FOLDER / "summaries").glob("*.json")):
        data = load(path)
        if not data.get("diagnostics", {}).get("detailedCaptureComplete"):
            continue
        mid = path.stem
        m = meta.get(mid, {})
        map_name = m.get("map") or m.get("mapName")
        width, height = num(data["match"].get("width")), num(data["match"].get("height"))
        cx, cy = width / 2, height / 2
        outcome = data["match"]["outcome"]
        draft = data.get("roster", {}).get("draft", [])
        match_count += 1

        # events indexed by owner id
        caps = defaultdict(lambda: defaultdict(set))   # team -> (round,grp) -> owners
        for owner, e in entries(data, "gemCollection"):
            if e.get("context") == "campGroup":
                caps[owner["team"]][(e["timestamp"]["round"], e["target"].get("id"))].add(owner["id"])
        clears = defaultdict(list)  # champ id -> [(round,x,y)]
        for owner, e in entries(data, "campClear"):
            clears[owner["id"]].append((e["timestamp"]["round"], e.get("x"), e.get("y")))
        assists = defaultdict(set)
        for owner, e in entries(data, "assist"):
            assists[(e["timestamp"]["round"], e["target"].get("id"))].add(owner["id"])
        kills = defaultdict(list)
        for owner, e in entries(data, "kill"):
            kills[owner["team"]].append((e["timestamp"]["round"], e["target"].get("id")))
        deaths_by_ctx = defaultdict(Counter)
        for owner, e in entries(data, "death"):
            deaths_by_ctx[owner["team"]][e.get("context", "?")] += 1
        ward_pts = defaultdict(list)
        for owner, e in entries(data, "wardPlacement"):
            ward_pts[owner["id"]].append((e["timestamp"]["round"], e.get("x"), e.get("y")))
        subs = defaultdict(list)
        for owner, e in entries(data, "gemSubmission"):
            amt = num(e.get("amount") or e.get("value"))
            subs[owner["team"]].append((e["timestamp"]["round"], amt, e.get("x"), e.get("y")))
        losses = defaultdict(float)
        for owner, e in entries(data, "gemLoss"):
            losses[owner["team"]] += num(e.get("amount") or e.get("value"))
        locks = defaultdict(list)
        crystals = defaultdict(int)
        for owner, e in entries(data, "buyConsumable"):
            name = e["target"].get("name", "").lower()
            if "lock" in name:
                locks[owner["team"]].append(e["timestamp"]["round"])
            if "crystal" in name:
                crystals[owner["team"]] += 1

        champ_by_id = {c["id"]: c for c in data["champions"]}
        side_teams = sorted({c["team"] for c in data["champions"]})
        for side in side_teams:
            # identify the top-20 team on this side via match teams list
            tid = next((t["teamId"] for t in m.get("teams", [])
                        if t["side"].lower() == side[-1].lower()), None)
            tname = id2name.get(tid)
            if not tname:
                continue
            T = teams[tname]
            team_names.add(tname)
            ours = [c for c in data["champions"] if c["team"] == side]
            won = outcome == side
            T["games"] += 1
            T["wins"] += won
            T["maps"][map_name] += 1
            T["win_rounds" if won else "loss_rounds"].append(data["match"]["roundsCompleted"])
            picks = tuple(d["champion"] for d in draft if d["team"] == side)
            T["drafts"][picks] += 1

            earned = {c["id"]: num(c["metrics"]["earnedGold"]) for c in ours}
            tot_earned = sum(earned.values()) or 1
            T["carry_share"].append(max(earned.values()) / tot_earned)
            T["kills"] += len(kills[side])
            T["deaths"] += sum(deaths_by_ctx[side].values())
            T["camp_deaths"] += deaths_by_ctx[side].get("camp", 0)
            T["submitted"] += sum(a for _, a, _, _ in subs[side])
            T["gem_loss"] += losses[side]
            T["lock_rounds"].extend(locks[side])
            T["crystal_uses"] += crystals[side]
            for r, amt, x, y in subs[side]:
                if amt > 0:
                    T["tribute_sizes"].append(amt)
                    T["tribute_rounds"].append(r)
                    T["altar_tiles"][(x, y)] += 1
            for r, victim in kills[side]:
                T["attackers_per_kill"].append(1 + len(assists.get((r, victim), ())))
            caps_side = caps[side]
            if caps_side:
                T["solo_capture_share"].append(
                    sum(1 for s in caps_side.values() if len(s) == 1) / len(caps_side))
            # spread of simultaneous clears
            by_round = defaultdict(list)
            for c in ours:
                for r, x, y in clears.get(c["id"], []):
                    if x is not None:
                        by_round[r].append((x, y))
            spread_vals = []
            for pts in by_round.values():
                if len(pts) >= 2:
                    d = [math.dist(a, b) for i, a in enumerate(pts) for b in pts[i + 1:]]
                    spread_vals.append(sum(d) / len(d))
            if spread_vals:
                T["spread"].append(sum(spread_vals) / len(spread_vals))

            for c in ours:
                C = T["champ"][c["name"]]
                champ_tot[c["name"]]["games"] += 1
                C["games"] += 1
                C["wins"] += won
                met = c["metrics"]
                C["kills"] += int(num(met["kills"]))
                C["deaths"] += int(num(met["deaths"]))
                C["assists"] += int(num(met["assists"]))
                C["earnedGold"] += earned[c["id"]]
                C["spentGold"] += num(met["spentGold"])
                C["damage"] += num(met["championDamageDone"])
                C["collected"] += num(met["collectedGems"])
                C["submitted"] += num(met["submittedGems"])
                C["captures"] += sum(1 for k, s in caps_side.items() if c["id"] in s)
                C["solo_captures"] += sum(1 for k, s in caps_side.items()
                                         if s == {c["id"]})
                for w_r, w_x, w_y in ward_pts.get(c["id"], []):
                    C["wards"] += 1
                    T["wards"] += 1
                    T["ward_rounds"].append(w_r)
                    if w_x is not None and width:
                        T["ward_cdist"].append(math.dist((w_x, w_y), (cx, cy))
                                               / max(1, math.dist((0, 0), (cx, cy))))
                for ib in c["itemsBought"]:
                    fam, stat, q = item_family(ib["item"]), item_stat(ib["item"]), int(num(ib["quantity"]))
                    C["shards" if item_kind(ib["item"]) == "shard" else "emblems"][(fam, stat)] += q
                for cb in c["consumablesBought"]:
                    C["consumables"][cb.get("consumable") or cb.get("item")] += int(num(cb["quantity"]))
                pts = sorted(clears.get(c["id"], []))
                if pts:
                    C["first_clear_rounds"].append(pts[0][0])
                    xs = [p[1] for p in pts if p[1] is not None]
                    ys = [p[2] for p in pts if p[2] is not None]
                    C["xs"].extend(xs)
                    C["ys"].extend(ys)

    # ---------- aggregates ----------
    summary = {}
    for name, T in teams.items():
        n = max(1, T["games"])
        champs = {}
        for cname, C in T["champ"].items():
            g = max(1, C["games"])
            champs[cname] = {
                "games": C["games"], "win_rate": C["wins"] / g,
                "pick_share": C["games"] / n,
                "kills_pg": C["kills"] / g, "deaths_pg": C["deaths"] / g,
                "assists_pg": C["assists"] / g,
                "gold_share": C["earnedGold"] / max(1, sum(x["earnedGold"] for x in T["champ"].values())),
                "damage_share": C["damage"] / max(1, sum(x["damage"] for x in T["champ"].values())),
                "spend_share": C["spentGold"] / max(1, sum(x["spentGold"] for x in T["champ"].values())),
                "submitted_pg": C["submitted"] / g,
                "captures_pg": C["captures"] / g, "solo_cap_pg": C["solo_captures"] / g,
                "wards_pg": C["wards"] / g,
                "first_clear_round": statistics.mean(C["first_clear_rounds"]) if C["first_clear_rounds"] else None,
                "shards": {f"{f}|{s}": q for (f, s), q in C["shards"].most_common()},
                "emblems": {f"{f}|{s}": q for (f, s), q in C["emblems"].most_common()},
                "consumables": dict(C["consumables"]),
                "path_radius": (statistics.mean(math.dist((x, y), (statistics.mean(C["xs"]), statistics.mean(C["ys"])))
                                              for x, y in zip(C["xs"], C["ys"]))
                                if C["xs"] else None),
            }
        summary[name] = {
            "games": T["games"], "win_rate": T["wins"] / n,
            "drafts": [{"picks": list(k), "count": v} for k, v in T["drafts"].most_common(5)],
            "kills_pg": T["kills"] / n, "deaths_pg": T["deaths"] / n,
            "camp_deaths_pg": T["camp_deaths"] / n,
            "submitted_pg": T["submitted"] / n,
            "gem_loss_share": T["gem_loss"] / max(1, T["submitted"] + T["gem_loss"]),
            "tribute_mean": statistics.mean(T["tribute_sizes"]) if T["tribute_sizes"] else None,
            "tribute_round_mean": statistics.mean(T["tribute_rounds"]) if T["tribute_rounds"] else None,
            "attackers_per_kill": statistics.mean(T["attackers_per_kill"]) if T["attackers_per_kill"] else None,
            "solo_capture_share": statistics.mean(T["solo_capture_share"]) if T["solo_capture_share"] else None,
            "carry_share": statistics.mean(T["carry_share"]),
            "farm_spread": statistics.mean(T["spread"]) if T["spread"] else None,
            "wards_pg": T["wards"] / n,
            "ward_round_mean": statistics.mean(T["ward_rounds"]) if T["ward_rounds"] else None,
            "ward_center_dist": statistics.mean(T["ward_cdist"]) if T["ward_cdist"] else None,
            "locks_pg": len(T["lock_rounds"]) / n,
            "crystals_pg": T["crystal_uses"] / n,
            "altars_used": len(T["altar_tiles"]),
            "win_round_mean": statistics.mean(T["win_rounds"]) if T["win_rounds"] else None,
            "loss_round_mean": statistics.mean(T["loss_rounds"]) if T["loss_rounds"] else None,
            "champions": champs,
        }

    OUT_JSON.write_text(json.dumps({
        "matches": match_count, "teams": summary,
        "champion_global": {k: dict(v) for k, v in champ_tot.items()},
    }, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Wrote {OUT_JSON}: {len(summary)} teams, {match_count} matches", flush=True)

    # ---------- markdown ----------
    L = ["# Deep analysis of top-20 teams", "",
         f"Source: {match_count} downloaded ranked summaries (recent-100 per team, "
         "deduplicated) under matches/top20-scout. All figures are per game "
         "unless noted. Ranks are capture-time.", ""]
    L += ["## Team overview", "",
          "| Team | Games | Win% | Kills | Deaths | Camp deaths | Submitted | Gem loss% | Tribute size | Attackers/kill | Solo capture% | Carry share | Farm spread | Wards | Locks | Crystals | Win round |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for name in sorted(summary, key=lambda t: -summary[t]["win_rate"]):
        S = summary[name]
        L.append(f"| {name} | {S['games']} | {S['win_rate']*100:.0f}% | "
                 f"{S['kills_pg']:.1f} | {S['deaths_pg']:.1f} | {S['camp_deaths_pg']:.1f} | "
                 f"{S['submitted_pg']:.0f} | {S['gem_loss_share']*100:.0f}% | "
                 f"{fmt(S['tribute_mean'])} | {fmt(S['attackers_per_kill'])} | "
                 f"{fmt((S['solo_capture_share'] or 0)*100,0)}% | {S['carry_share']:.2f} | "
                 f"{fmt(S['farm_spread'])} | {S['wards_pg']:.0f} | {S['locks_pg']:.1f} | "
                 f"{S['crystals_pg']:.1f} | {fmt(S['win_round_mean'],0)} |")
    L.append("")
    L += ["## Most common drafts (per team)", ""]
    for name in sorted(summary):
        S = summary[name]
        top = S["drafts"][0] if S["drafts"] else None
        if top:
            L.append(f"- **{name}**: {' + '.join(top['picks'])} "
                     f"({top['count']}/{S['games']} games)")
    L.append("")
    L += ["## Champion roles (aggregated over teams)", "",
          "Per champion name across all sampled top-20 games: usage, typical gold "
          "share, damage share, captures, wards and favorite item builds.", ""]
    # global per champion across teams
    agg = defaultdict(lambda: {"games": 0, "gold": [], "dmg": [], "cap": [],
                               "wards": 0, "shards": Counter(), "emblems": Counter(),
                               "teams": set()})
    for name, S in summary.items():
        for cname, C in S["champions"].items():
            A = agg[cname]
            A["games"] += C["games"]
            A["gold"].append(C["gold_share"])
            A["dmg"].append(C["damage_share"])
            A["cap"].append(C["captures_pg"])
            A["wards"] += C["wards_pg"] * C["games"]
            A["teams"].add(name)
            for k, v in C["shards"].items():
                A["shards"][k] += v
            for k, v in C["emblems"].items():
                A["emblems"][k] += v
    L += ["| Champion | Teams | Games | Gold share | Damage share | Captures/game | Wards/game | Top emblems |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for cname in sorted(agg, key=lambda c: -agg[c]["games"]):
        A = agg[cname]
        emb = ", ".join(f"{k.replace('|',' ')}×{v}" for k, v in A["emblems"].most_common(3))
        L.append(f"| {cname} | {len(A['teams'])} | {A['games']} | "
                 f"{statistics.mean(A['gold']):.2f} | {statistics.mean(A['dmg']):.2f} | "
                 f"{statistics.mean(A['cap']):.1f} | {A['wards']/max(1,A['games']):.1f} | {emb} |")
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD}", flush=True)


def fmt(v, d=1):
    return f"{v:.{d}f}" if v is not None else "n/a"


if __name__ == "__main__":
    main()
