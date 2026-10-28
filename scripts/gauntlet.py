#!/usr/bin/env python3
"""Play one bot against another on every map, from both sides, and print a results table."""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bot", nargs="?", default="main", help="bot under bots/ (default: main)")
    parser.add_argument("opponent", nargs="?", default="starter-cpp", help="opponent under bots/ (default: starter-cpp)")
    parser.add_argument("--maps", nargs="*", help="map names in maps/ (default: all)")
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--rounds", type=int, help="stop each match after this many rounds")
    args = parser.parse_args()

    maps = args.maps or sorted(p.stem for p in (ROOT / "maps").glob("*.map26a"))
    if not maps:
        sys.exit("no maps in maps/; run `cambc maps pull`")

    out = ROOT / "matches" / f"gauntlet-{time.strftime('%Y%m%d-%H%M%S')}"
    out.mkdir(parents=True)
    bot, opp = ROOT / "bots" / args.bot, ROOT / "bots" / args.opponent

    games = []  # (map, our side, stats path)
    rows = []
    for name in maps:
        map_path = ROOT / "maps" / f"{name}.map26a"
        for side, (a, b) in (("A", (bot, opp)), ("B", (opp, bot))):
            stem = out / f"{name}-{side}"
            games.append((name, side, stem.with_suffix(".json")))
            rows.append(f"{a} {b} {map_path} {stem}.repl26a --statistics {stem}.json")
    manifest = out / "manifest.txt"
    manifest.write_text("\n".join(rows) + "\n")

    cmd = ["cambc", "run-batch", "--release", "--json", "--jobs", str(args.jobs), str(manifest)]
    if args.rounds:
        cmd += ["--rounds", str(args.rounds)]
    with open(out / "run-batch.log", "w") as log:
        subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)

    wins = losses = errors = 0
    print(f"{'map':<24} {'side':<4} {'result':<6} {'gems us':>8} {'gems them':>10} {'rounds':>7}")
    for name, side, stats in games:
        if not stats.exists():
            errors += 1
            print(f"{name:<24} {side:<4} {'ERROR':<6}")
            continue
        data = json.loads(stats.read_text())
        gems = {t["team"]: int(t["submittedGems"]) for t in data["teams"]}
        us, them = ("teamA", "teamB") if side == "A" else ("teamB", "teamA")
        won = data["match"]["outcome"] == us
        wins += won
        losses += not won
        print(f"{name:<24} {side:<4} {'win' if won else 'loss':<6} {gems.get(us, 0):>8} {gems.get(them, 0):>10} "
              f"{data['match']['roundsCompleted']:>7}")

    print(f"\n{args.bot} vs {args.opponent}: {wins} wins, {losses} losses, {errors} errors")
    if errors:
        print(f"see {out / 'run-batch.log'} for errors")
    print(f"replays and logs: {out}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
