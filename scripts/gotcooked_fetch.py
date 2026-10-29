#!/usr/bin/env python3
"""Download all match summaries for team 'Got Cooked' (rank 392).

Reads matches/gotcooked-ranked.json + gotcooked-unranked.json (CLI list output),
deduplicates finished matches, downloads `cambc matches summary` for each into
matches/gotcooked/summaries/, resumable.
"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "matches")
OUT = os.path.join(M, "gotcooked", "summaries")
os.makedirs(OUT, exist_ok=True)

def load(p):
    for enc in ("utf-16", "utf-8-sig", "utf-8"):
        try:
            return json.load(open(p, encoding=enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise RuntimeError(p)

ids, meta = [], {}
for fn in ("gotcooked-ranked.json", "gotcooked-unranked.json"):
    p = os.path.join(M, fn)
    if not os.path.exists(p):
        continue
    d = load(p)
    for m in d.get("matches", []):
        if m.get("status") != "finished":
            continue
        mid = m["matchId"]
        if mid not in meta:
            ids.append(mid)
        meta[mid] = m

pending = [i for i in ids if not os.path.exists(os.path.join(OUT, f"{i}.json"))]
print(f"{len(ids)} unique finished matches, {len(pending)} summaries to fetch", flush=True)

ok = fail = 0
for n, mid in enumerate(pending, 1):
    tmp = os.path.join(OUT, mid + ".tmp")
    dst = os.path.join(OUT, mid + ".json")
    r = subprocess.run(["cambc", "matches", "summary", mid, "--json", "-o", tmp],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 100:
        os.replace(tmp, dst)
        ok += 1
    else:
        if os.path.exists(tmp):
            os.remove(tmp)
        fail += 1
        print(f"  FAIL {mid}: {(r.stderr or r.stdout)[:140]}", flush=True)
        time.sleep(2)
    if n % 20 == 0:
        print(f"  {n}/{len(pending)} ({fail} failures)", flush=True)

json.dump({i: meta[i] for i in ids},
          open(os.path.join(ROOT, "matches", "gotcooked", "meta.json"), "w", encoding="utf-8"),
          indent=1)
print(f"done: {ok} ok, {fail} failed, {len(ids)-len(pending)+ok} total present", flush=True)
