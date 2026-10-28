#!/usr/bin/env python3
"""Play one bot against a panel of opponents on a set of maps, both sides,
in one parallel batch, and report wins and gem margins per opponent.

    python scripts/panel.py apex --opps titan titanj1 hunter --maps 00the-line
"""
import argparse
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bot")
    ap.add_argument("--opps", nargs="+", required=True)
    ap.add_argument("--maps", nargs="*", help="map names (default: all)")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--quiet", action="store_true", help="only print the summary")
    args = ap.parse_args()

    maps = args.maps or sorted(p.stem for p in (ROOT / "maps").glob("*.map26a"))
    out = ROOT / "matches" / f"panel-{args.bot}-{time.strftime('%Y%m%d-%H%M%S')}"
    out.mkdir(parents=True)
    games, rows = [], []
    for opp in args.opps:
        for m in maps:
            mp = ROOT / "maps" / f"{m}.map26a"
            for side in ("A", "B"):
                a, b = (args.bot, opp) if side == "A" else (opp, args.bot)
                stem = out / f"{opp}-{m}-{side}"
                games.append((opp, m, side, stem.with_suffix(".json")))
                rows.append(f"{ROOT / 'bots' / a} {ROOT / 'bots' / b} {mp} {stem}.repl26a --statistics {stem}.json")
    (out / "manifest.txt").write_text("\n".join(rows) + "\n")
    with open(out / "run-batch.log", "w") as log:
        subprocess.run(["cambc", "run-batch", "--release", "--json", "--jobs", str(args.jobs), str(out / "manifest.txt")],
                       cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)

    per = defaultdict(lambda: [0, 0, 0, 0])  # wins, games, our gems, their gems
    for opp, m, side, stats in games:
        if not stats.exists():
            print(f"ERROR {opp} {m} {side}")
            continue
        d = json.loads(stats.read_text())
        gems = {t["team"]: int(t["submittedGems"]) for t in d["teams"]}
        us, them = ("teamA", "teamB") if side == "A" else ("teamB", "teamA")
        won = d["match"]["outcome"] == us
        p = per[opp]
        p[0] += won
        p[1] += 1
        p[2] += gems.get(us, 0)
        p[3] += gems.get(them, 0)
        if not args.quiet:
            print(f"{opp:<10} {m:<22} {side} {'win ' if won else 'loss'} {gems.get(us, 0):>5} {gems.get(them, 0):>5} "
                  f"r{d['match']['roundsCompleted']}")
    tw = tg = 0
    for opp, (w, g, ug, tg_) in per.items():
        print(f"{args.bot} vs {opp:<10} {w:>3}/{g:<3} avg gems {ug // max(g, 1):>4} - {tg_ // max(g, 1):<4}")
        tw += w
        tg += g
    print(f"TOTAL {args.bot}: {tw}/{tg} wins  ({out})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
