#!/usr/bin/env python3
"""Resumable v22 map/opponent campaign; respects 50 match GROUPS per hour.

--prepare imports compatible frozen results without calling the platform.
--step collects results and queues at most one five-match group.
--watch continues across hourly windows; --report only renders saved results.
--queue-first submits eligible groups before collecting their results.
--self-test checks quota accounting without network access or match creation.

Writes an intent before each create request. An ambiguous create failure stops
the campaign for reconciliation instead of risking a duplicate request.
"""
import argparse
import contextlib
import hashlib
import json
import os
import re
import subprocess
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from analyze_online_batch import OUR_TEAM, aggregate, side_stats

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "matches/map-campaign-v22-20261028"
LIMIT, GROUP, WINDOW, MARGIN = 50, 5, 3600, 10


class Halt(RuntimeError):
    pass


class RejectedRateLimit(Halt):
    """The platform explicitly rejected the request before accepting a group."""
    def __init__(self, message, retry_after, capture):
        super().__init__(message)
        self.retry_after = retry_after
        self.capture = capture


def rejected_rate_limit(message):
    match = re.fullmatch(
        r"error: Platform request rejected \(HTTP 429\); retry after (\d+) seconds",
        message.strip())
    return int(match.group(1)) if match else None


def now():
    return datetime.now(timezone.utc)


def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transient_read_error(message):
    return any(s in message.lower() for s in
               ("429", "10051", "timed out", "connection", "retry shortly", "peer disconnected"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == value:
        return
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(value, encoding="utf-8")
    os.replace(tmp, path)


@contextlib.contextmanager
def exclusive(path):
    """OS-owned lock is released even if the process crashes or is killed."""
    with path.open("a+b") as file:
        if file.tell() == 0:
            file.write(b"0")
            file.flush()
        file.seek(0)
        if os.name == "nt":
            import msvcrt
            lock = lambda: msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
            unlock = lambda: msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            lock = lambda: fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            unlock = lambda: fcntl.flock(file, fcntl.LOCK_UN)
        try:
            lock()
        except OSError as error:
            raise Halt("Another campaign runner holds the lock; reuse it.") from error
        try:
            yield
        finally:
            file.seek(0)
            unlock()


def group_budget(quota, jobs, at):
    """One five-map create request consumes ONE platform quota unit.

    The authoritative counter includes the team's other outgoing requests.
    Count our recent accepted group IDs as a lower bound if an API response
    lags. Incoming challenges do not spend this team's outgoing quota.
    """
    capacity = min(LIMIT, int(quota["limit"]))
    assert capacity > 0 and int(quota["used"]) >= 0
    cutoff = at - timedelta(seconds=WINDOW + MARGIN)
    accepted = {}
    for job in jobs:
        queued, group = job.get("queued_at"), job.get("group_id")
        if queued and group and stamp(queued) > cutoff:
            accepted[group] = max(accepted.get(group, stamp(queued)), stamp(queued))
    used = max(int(quota["used"]), len(accepted))
    available = max(0, capacity - used)
    next_at = at
    if available == 0:
        waits = [at]
        if int(quota["used"]) >= capacity:
            reset = quota.get("resetsAt")
            waits.append(stamp(reset) + timedelta(seconds=MARGIN + 1)
                         if reset else at + timedelta(seconds=60))
        if len(accepted) >= capacity:
            waits.append(sorted(accepted.values())[len(accepted) - capacity]
                         + timedelta(seconds=WINDOW + MARGIN + 1))
        next_at = max(waits)
    return used, available, next_at


class Campaign:
    def __init__(self, folder, queue_first=False):
        self.folder = folder.resolve()
        self.config_path = self.folder / "campaign.json"
        self.config = load(self.config_path)
        c = self.config
        assert c["team_id"] == OUR_TEAM
        assert c["max_groups_per_hour"] == LIMIT and c["group_size"] == GROUP
        assert c["rating_gap"] <= 200 and len(c["opponents"]) == 5
        assert len({o["teamId"] for o in c["opponents"]}) == 5
        assert len({m["id"] for m in c["maps"]}) == len(c["maps"])
        assert len(c["maps"]) % GROUP == 0
        assert all(re.fullmatch(r"[A-Za-z0-9_-]+", m["name"]) for m in c["maps"])
        self.state_path = self.folder / "state.json"
        self.state = load(self.state_path) if self.state_path.exists() else self.initialize()
        if self.state["config_sha256"] != digest(self.config_path):
            raise Halt("Campaign configuration changed; review before resuming.")
        self.serial = 0
        self.queue_first = queue_first

    def initialize(self):
        c = self.config
        seed = load(ROOT / c["seed_analysis"])
        chosen = c["seed_opponent_id"]
        imported = [m for m in seed["matches"] if m["opponent_team_id"] == chosen]
        assert len(imported) == GROUP
        state = {"config_sha256": digest(self.config_path), "phase": "prepared",
                 "sources": {}, "jobs": [], "last_update": now().isoformat()}
        for start in range(0, len(c["maps"]), GROUP):
            maps = c["maps"][start:start + GROUP]
            for oi, opponent in enumerate(c["opponents"]):
                job = {
                    "id": f"b{start // GROUP:02}-p{oi}", "opponent_id": opponent["teamId"],
                    "opponent_name": opponent["name"], "maps": maps,
                    "sides": ["a" if (start + mi + oi) % 2 == 0 else "b" for mi in range(GROUP)],
                    "status": "pending",
                }
                if start == 0 and opponent["teamId"] == chosen:
                    assert {m["map_id"] for m in imported} == {m["id"] for m in maps}
                    for mi, mp in enumerate(maps):
                        row = next(m for m in imported if m["map_id"] == mp["id"])
                        assert row["side"] == job["sides"][mi]
                    groups = {m["group_id"] for m in imported}
                    assert len(groups) == 1
                    group = groups.pop()
                    job.update(status="complete", group_id=group, reused=True,
                               queued_at=min(m["created_at"] for m in imported))
                    state["sources"][chosen] = group
                    write(self.folder / "results" / (job["id"] + ".json"), {
                        "matches": imported, "imported_from": c["seed_analysis"],
                        "source_sha256": digest(ROOT / c["seed_analysis"]),
                    })
                state["jobs"].append(job)
        return state

    def save(self, phase=None, **details):
        if phase:
            self.state["phase"] = phase
        self.state.update(details)
        self.state["last_update"] = now().isoformat()
        self.state["runner_pid"] = os.getpid()
        write(self.state_path, self.state)

    def cli(self, args, label, mutation=False):
        """Only read-only requests get automatic retries."""
        for attempt in range(1 if mutation else 5):
            self.serial += 1
            filename = f"{now().strftime('%Y%m%dT%H%M%S%f')}-{self.serial}-{label}"
            try:
                result = subprocess.run(["cambc", *args], cwd=ROOT, capture_output=True,
                                        text=True, encoding="utf-8", timeout=120)
            except (OSError, subprocess.TimeoutExpired) as error:
                if mutation:
                    raise Halt(f"Create outcome uncertain: {error}") from error
                if attempt == 4:
                    raise Halt(f"CLI unavailable: {error}") from error
                print(f"Retrying {label} read in {5 * (attempt + 1)} seconds "
                      f"(attempt {attempt + 1}/5).", flush=True)
                time.sleep(5 * (attempt + 1))
                continue
            text(self.folder / "raw" / (filename + ".stdout"), result.stdout)
            text(self.folder / "raw" / (filename + ".stderr"), result.stderr)
            if result.returncode == 0:
                time.sleep(2)
                return result.stdout
            message = result.stderr or result.stdout
            if mutation:
                delay = rejected_rate_limit(message)
                if delay is not None and not result.stdout.strip():
                    raise RejectedRateLimit(message, delay, filename)
                raise Halt(f"Create returned an error; reconcile before retrying: {message}")
            if not transient_read_error(message) or attempt == 4:
                raise Halt(message)
            retry = re.search(r"retry after (\d+) seconds", message)
            delay = max(int(retry.group(1)) if retry else 0, 5 * (attempt + 1))
            print(f"Retrying {label} read in {delay} seconds "
                  f"(attempt {attempt + 1}/5).", flush=True)
            time.sleep(delay)
        raise Halt("Read retries exhausted")

    def verify_source(self):
        base = ROOT / self.config["source_bot"]
        for name, expected in self.config["source_hashes"].items():
            path = base / name
            if not path.exists() or digest(path) != expected:
                raise Halt(f"Frozen source changed: {path}")

    def verify_live(self):
        raw = self.cli(["submissions", "list"], "live")
        version, submission = self.config["submission_version"], self.config["submission_id"]
        live = re.search(r"Live:\s*(\d+)\s+Selected:\s*(\d+)", raw)
        line = next((s for s in raw.splitlines() if s.startswith(f"v{version} ")), "")
        fields = line.split()
        if (not live or tuple(map(int, live.groups())) != (version, version)
                or submission not in line or len(fields) < 2 or fields[1] != "active"
                or "Mode: pinned version" not in raw):
            for job in self.state["jobs"]:
                if job["status"] == "queued":
                    job["version_interruption"] = True
            raise Halt("Live/selected submission changed; campaign stopped without activating anything.")
        return raw

    def ratings(self, quota):
        ranks = [quota["requesterRank"]]
        for opponent in self.config["opponents"]:
            rank = quota["opponentRanks"].get(opponent["teamId"])
            if rank is not None:
                ranks.append(rank)
        teams = {}
        for page in sorted({(r - 1) // 100 + 1 for r in ranks}):
            data = json.loads(self.cli(["ladder", "--page", str(page), "--limit", "100", "--json"], "ladder"))
            teams.update({t["teamId"]: t for t in data["teams"]})
        if OUR_TEAM not in teams:
            raise Halt("Own rating unavailable; no opponent selected by rank alone.")
        return teams

    def check_journal(self):
        for job in self.state["jobs"]:
            if job["status"] in ("submitting", "uncertain") or job.get("version_interruption"):
                raise Halt(f"{job['id']} requires reconciliation; refusing duplicate/unattributed games.")

    def collect(self):
        self.check_journal()
        changed = False
        if any(j["status"] == "queued" for j in self.state["jobs"]):
            self.save("collecting_results")
            self.render()
        for job in self.state["jobs"]:
            if job["status"] != "queued":
                continue
            data = json.loads(self.cli(["match-groups", "show", job["group_id"], "--json"], "group"))
            write(self.folder / "groups" / (job["id"] + ".json"), data)
            assert data["nextCursor"] is None and len(data["matches"]) == GROUP
            if any(m["status"] in ("failed", "cancelled", "error") for m in data["matches"]):
                raise Halt(f"Platform failed a match in {job['id']}; retain it for review.")
            if not all(m["status"] == "finished" for m in data["matches"]):
                continue
            self.verify_live()
            results = []
            hashes = {}
            for match in sorted(data["matches"], key=lambda m: m["position"]):
                mi = match["position"] - 1
                assert match["groupId"] == job["group_id"]
                assert match["mapId"] == job["maps"][mi]["id"]
                ours = next(t for t in match["teams"] if t["teamId"] == OUR_TEAM)
                other = next(t for t in match["teams"] if t["teamId"] == job["opponent_id"])
                assert ours["side"] == job["sides"][mi]
                us, them = "team" + ours["side"].upper(), "team" + other["side"].upper()
                assert {us, them} == {"teamA", "teamB"}
                path = ROOT / "matches/online" / (match["matchId"] + ".json")
                if not path.exists():
                    self.cli(["matches", "summary", match["matchId"], "--json", "-o", str(path)], "summary")
                summary = load(path)
                hashes[match["matchId"]] = digest(path)
                assert summary["diagnostics"]["detailedCaptureComplete"]
                assert summary["match"]["outcome"] in ("teamA", "teamB")
                result = "win" if summary["match"]["outcome"] == us else "loss"
                assert result == ours["result"]
                roster = {c["id"]: c for c in summary["roster"]["champions"]}
                assert len(roster) == len(summary["roster"]["champions"])
                results.append({
                    "match_id": match["matchId"], "group_id": job["group_id"],
                    "map": match["map"], "map_id": match["mapId"], "side": ours["side"],
                    "opponent_name": other["name"], "opponent_team_id": other["teamId"],
                    "result": result, "created_at": match["createdAt"],
                    "rounds": summary["match"]["roundsCompleted"],
                    "seed": summary["match"]["seed"], "map_hash": summary["match"]["mapHash"],
                    "engine_version": summary["match"]["engineVersion"],
                    "engine_build_hash": summary["match"]["engineBuildHash"],
                    "per_match_submission_id": ours.get("submissionId"),
                    "us": side_stats(summary, us, roster),
                    "opponent": side_stats(summary, them, roster),
                })
            assert len({r["match_id"] for r in results}) == GROUP
            write(self.folder / "results" / (job["id"] + ".json"), {
                "matches": results, "summary_hashes": hashes,
                "version_evidence": "Expected live/selected submission checked before creation and after completion; per-match ID not exposed.",
            })
            job["status"] = "complete"
            self.save()
            self.render()
            progress = load(self.folder / "progress.json")
            print(f"Collected {job['id']}: {progress['results']}/{progress['target']} results; "
                  f"{progress['complete_maps']}/{progress['total_maps']} complete maps.", flush=True)
            changed = True
        return changed

    def step(self):
        if self.state.get("dispatch_disabled_reason"):
            raise Halt(self.state["dispatch_disabled_reason"])
        self.verify_source()
        self.check_journal()
        defer_collection = self.queue_first and any(
            j["status"] == "pending" for j in self.state["jobs"])
        if not defer_collection:
            self.collect()
        if all(j["status"] == "complete" for j in self.state["jobs"]):
            self.save("complete")
            return 0
        if not any(j["status"] == "pending" for j in self.state["jobs"]):
            self.save("waiting_for_results")
            return 30
        quota = json.loads(self.cli(["match-groups", "quota", "--json"], "quota"))
        if quota["team"]["id"] != OUR_TEAM or not quota["ready"]:
            raise Halt("Team identity/readiness changed.")
        used, available, next_at = group_budget(quota["quota"], self.state["jobs"], now())
        self.save(quota_groups_used=used, quota_groups_available=available,
                  server_quota=quota["quota"], earliest_group_time=next_at.isoformat())
        if available == 0:
            if defer_collection:
                self.collect()
            self.save("waiting_for_hourly_quota")
            return min(300, max(10, (next_at - now()).total_seconds()))
        teams = self.ratings(quota)
        for job in self.state["jobs"]:
            if job["status"] != "pending":
                continue
            opponent = teams.get(job["opponent_id"])
            if not opponent or abs(opponent["rating"] - teams[OUR_TEAM]["rating"]) > self.config["rating_gap"]:
                continue
            source = self.state["sources"].get(job["opponent_id"])
            if source and any(j.get("group_id") == source and j["status"] != "complete" for j in self.state["jobs"]):
                continue  # First opponent snapshot must be ready before reusing it.
            # Recheck the official group quota immediately before spending.
            self.verify_live()
            fresh = json.loads(self.cli(["match-groups", "quota", "--json"], "quota-before-create"))
            if fresh["team"]["id"] != OUR_TEAM or not fresh["ready"]:
                raise Halt("Team identity/readiness changed before creation.")
            used, available, next_at = group_budget(fresh["quota"], self.state["jobs"], now())
            if available == 0:
                if defer_collection:
                    self.collect()
                self.save("waiting_for_hourly_quota", quota_groups_used=used,
                          quota_groups_available=available, earliest_group_time=next_at.isoformat())
                return min(300, max(10, (next_at - now()).total_seconds()))
            assert used + 1 <= min(LIMIT, fresh["quota"]["limit"])
            args = ["match-groups", "create", job["opponent_id"],
                    "--maps", ",".join(m["id"] for m in job["maps"]),
                    "--sides", ",".join(job["sides"]), "--json"]
            if source:
                args += ["--source-group", source]
            job.update(status="submitting", queued_at=now().isoformat(), source_group=source,
                       our_rating=teams[OUR_TEAM]["rating"], opponent_rating=opponent["rating"],
                       command=["cambc", *args])
            self.save("submitting")  # Durable intent BEFORE the mutating request.
            try:
                response = json.loads(self.cli(args, job["id"] + "-create", mutation=True))
                if not response.get("groupId"):
                    raise Halt("Create response has no group ID")
            except RejectedRateLimit as error:
                job.setdefault("rejected_attempts", []).append({
                    "queued_at": job["queued_at"], "command": job["command"],
                    "source_group": source, "reason": str(error),
                    "response_capture": error.capture, "retry_after": error.retry_after,
                    "resolution": "Explicit HTTP 429 rejection with empty stdout; no group accepted.",
                })
                job["status"] = "pending"
                job.pop("queued_at")
                delay = max(15, error.retry_after)
                self.save("waiting_for_api_rate_limit")
                print(f"{job['id']} was rejected by the API rate limit; "
                      f"retained receipt and will recheck all guards after {delay}s.", flush=True)
                return delay
            except Exception:
                job["status"] = "uncertain"
                self.save("needs_reconciliation")
                raise
            job.update(status="queued", group_id=response["groupId"], create_response=response)
            self.state["sources"].setdefault(job["opponent_id"], response["groupId"])
            self.save("queueing" if self.queue_first else "running", quota_groups_used=used + 1,
                      quota_groups_available=available - 1, server_quota=fresh["quota"])
            print(f"Queued {job['id']}: {job['opponent_name']} "
                  f"({used + 1}/{LIMIT} quota groups; five games in this group)", flush=True)
            return 1 if self.queue_first else 5
        if defer_collection:
            self.collect()
        self.save("waiting_for_results_or_rating_band")
        return 60

    def render(self):
        """Presentation reads frozen per-group analyses, not raw engine data."""
        matches = []
        for job in self.state["jobs"]:
            if job["status"] == "complete":
                matches += load(self.folder / "results" / (job["id"] + ".json"))["matches"]
        keys = [(m["map_id"], m["opponent_team_id"]) for m in matches]
        assert len(keys) == len(set(keys))
        assert len({m["match_id"] for m in matches}) == len(matches)
        shapes = load(ROOT / self.config["map_shapes"])
        esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
        table = []
        complete = 0
        for mp in self.config["maps"]:
            rows = [m for m in matches if m["map_id"] == mp["id"]]
            assert len(rows) <= 5
            wins = sum(m["result"] == "win" for m in rows)
            complete += len(rows) == 5
            shape = shapes.get(mp["name"].replace("_", "-"), {})
            facts = []
            if shape:
                facts.append(f"{shape['w']}x{shape['h']}; {shape['altars']} altars; {shape['total']} static gems")
                if shape["total"] and shape["unreach"]:
                    facts.append(f"{shape['unreach']}/{shape['total']} static gems were recorded outside the spawn walkable component")
                facts.append(f"Largest group: {shape['top']} gems, summed base strength {shape['top_str']:g}")
            body = [f"# {mp['name']} - map strategy worksheet", "",
                    "<!-- Generated from frozen campaign results by scripts/map_campaign.py. -->", "",
                    f"Fixed baseline: v22. Coverage: **{len(rows)}/5 opponents**. Record: **{wins}-{len(rows)-wins}**.",
                    "", "## Map evidence", "",
                    *["- " + f for f in facts],
                    "", "Shape facts are from the earlier frozen map scan. Match IDs below resolve to tested map hashes in the stored summaries.",
                    "", "## Results", "",
                    "| Opponent | Side | Result | Gems us/them | Deaths us/them | Our gems lost | Match ID |",
                    "| --- | --- | --- | --- | --- | --- | --- |"]
            for m in rows:
                u, o = m["us"], m["opponent"]
                body.append(f"| {esc(m['opponent_name'])} | {m['side']} | {m['result']} | {u['submitted']}/{o['submitted']} | "
                            f"{u['metrics']['deaths']:g}/{o['metrics']['deaths']:g} | {u['gem_loss']} | {m['match_id']} |")
            body += ["", "## Interpretation and next experiment", ""]
            if len(rows) < 5:
                body += ["Incomplete opponent coverage. No map-specific strategy decision yet."]
            else:
                sums = aggregate(rows)
                u, o = sums["us"], sums["opponent"]
                body += [
                    f"- Collected {u['collected']:g}; submitted {u['submitted']}; lost {u['gem_loss']} carried gems.",
                    f"- Deaths {u['deaths']:g} versus {o['deaths']:g}; fuel exhaustion {u['fuel_exhaustions']}; bot faults {u['bot_faults']}.",
                    "- Preserve v22 as this map's reference." if wins >= 4 else "- Investigate a dedicated map profile before changing global behavior.",
                ]
                if shape and shape["total"] and shape["top"] * 2 >= shape["total"]:
                    body += ["- Test control and delivery around the dominant gem group; determine whether it needs a raid or capture defense."]
                if shape and shape["total"] and shape["unreach"] * 4 >= shape["total"]:
                    body += ["- Test terrain traversal and access to disconnected gem sources."]
                if shape.get("altars") == 1:
                    body += ["- Inspect the single altar's approach, locks and carrier survival."]
                if shape.get("w", 0) * shape.get("h", 0) >= 4900:
                    body += ["- Compare travel time and solo farming against grouping on this large map."]
                if u["gem_loss"]:
                    body += ["- Inspect actual loss events and routes; low submission alone does not prove a banking-threshold problem."]
            body += ["", "These are hypotheses for controlled follow-up, not a validated optimal strategy. The completed design uses five real opponent snapshots with a 3/2 side balance. No map-specific bot change is enabled by this report.", ""]
            text(ROOT / self.config["report_dir"] / (mp["name"] + ".md"), "\n".join(body))
            table.append(f"| [{mp['name']}](maps/{mp['name']}.md) | {len(rows)}/5 | {wins}-{len(rows)-wins} |")
        title = [
            "# Per-map online baseline matrix", "",
            f"**{len(matches)}/{len(self.config['maps']) * 5} results; {complete}/{len(self.config['maps'])} maps have all five opponents.**",
            f"State: `{self.state['phase']}`. Updated: {self.state['last_update']}.",
            f"Groups awaiting collection: {sum(j['status'] == 'queued' for j in self.state['jobs'])}; "
            f"groups not yet requested: {sum(j['status'] == 'pending' for j in self.state['jobs'])}.",
            f"Hourly quota usage last checked: {self.state.get('quota_groups_used', 'not checked')}/50 groups. "
            f"Available group slots: {self.state.get('quota_groups_available', 'not checked')}. One group contains five games.",
            f"Next budget time: {self.state.get('earliest_group_time', 'not checked')}.",
            "", "Bot: pinned v22. Opponents: " + "; ".join(esc(o["name"]) for o in self.config["opponents"]) + ".",
            "", "Five compatible historical Ascendance results are reused. The other 345 cells require new matches. Opponent submissions are pinned after their first group; current ratings are checked before each new group.",
            "", "| Map | Opponents complete | Wins-losses |", "| --- | --- | --- |", *table,
            "", "Results are not adjusted for opponent or side strength and are not proof of an optimal map strategy. Full inputs, commands, raw responses and frozen analyses are under `matches/map-campaign-v22-20261028/`.", "",
        ]
        if self.state.get("error"):
            title += ["Runner stopped: " + esc(self.state["error"]), ""]
        text(ROOT / self.config["matrix_path"], "\n".join(title))
        write(self.folder / "progress.json", {
            "results": len(matches), "target": len(self.config["maps"]) * 5,
            "complete_maps": complete, "total_maps": len(self.config["maps"]),
            "phase": self.state["phase"], "updated": self.state["last_update"],
            "runner_pid": self.state.get("runner_pid"), "error": self.state.get("error"),
            "queued_groups": sum(j["status"] == "queued" for j in self.state["jobs"]),
            "pending_groups": sum(j["status"] == "pending" for j in self.state["jobs"]),
            "quota_groups_available": self.state.get("quota_groups_available"),
            "queue_first": self.queue_first,
        })


def self_test():
    at = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    assert transient_read_error("error: Peer disconnected")
    assert transient_read_error("HTTP 429; retry after 5 seconds")
    assert not transient_read_error("HTTP 409: no eligible bot")
    assert not transient_read_error("Authentication required")
    assert rejected_rate_limit("error: Platform request rejected (HTTP 429); retry after 5 seconds\n") == 5
    assert rejected_rate_limit("Peer disconnected after HTTP 429") is None
    assert rejected_rate_limit("error: Platform request rejected (HTTP 500); retry after 5 seconds") is None
    def quota(used):
        return {"limit": 50, "used": used, "resetsAt": (at+timedelta(seconds=100)).isoformat()}
    def jobs(n, age=10):
        return [{"group_id": str(i), "queued_at": (at-timedelta(seconds=age)).isoformat()} for i in range(n)]
    assert group_budget(quota(10), jobs(9), at)[1] == 40
    assert group_budget(quota(49), [], at)[1] == 1
    assert group_budget(quota(50), [], at)[1] == 0
    assert group_budget(quota(0), jobs(50, 3620), at)[0] == 0
    assert group_budget(quota(0), jobs(50, 3605), at)[0] == 50
    assert group_budget(quota(0), jobs(1), at)[0] == 1
    assert group_budget(quota(1), jobs(1), at)[0] == 1
    assert group_budget(quota(0), jobs(2), at)[0] == 2
    assert group_budget(quota(0), jobs(1) + jobs(1), at)[0] == 1
    assert group_budget(quota(0), [{"queued_at": at.isoformat()}], at)[0] == 0
    used, available, eligible = group_budget(quota(50), jobs(50), at)
    assert used == 50 and available == 0 and eligible > at
    assert group_budget(quota(0), jobs(50), eligible)[1] == 50
    for status in ("submitting", "uncertain"):
        dummy = object.__new__(Campaign)
        dummy.state = {"jobs": [{"id": "test", "status": status}]}
        try:
            dummy.collect()
            raise AssertionError("Uncertain create was not blocked")
        except Halt:
            pass
    dummy = object.__new__(Campaign)
    dummy.config = {"submission_version": 22, "submission_id": "expected-id"}
    dummy.state = {"jobs": [{"id": "test", "status": "queued"}]}
    dummy.cli = lambda args, label: "Mode: pinned version\nLive: 22  Selected: 23\nv22 active rust expected-id\n"
    try:
        dummy.verify_live()
        raise AssertionError("Version change was not blocked")
    except Halt:
        pass
    assert dummy.state["jobs"][0]["version_interruption"]
    dummy.cli = lambda args, label: "Mode: pinned version\nLive: 22  Selected: 22\nv22 active rust expected-id\n"
    assert "expected-id" in dummy.verify_live()

    def dispatch_stub(statuses, used=0, fresh_used=None):
        runner = object.__new__(Campaign)
        runner.queue_first = True
        runner.config = {"rating_gap": 200}
        runner.state = {"sources": {"peer": "frozen-source"}, "jobs": [
            {"id": f"test-{i}", "status": status, "opponent_id": "peer",
             "opponent_name": "Peer", "maps": [{"id": f"map-{n}"} for n in range(5)],
             "sides": ["a"] * 5, "group_id": f"old-{i}" if status == "queued" else None}
            for i, status in enumerate(statuses)]}
        events = []
        runner.verify_source = lambda: None
        runner.verify_live = lambda: events.append("live")
        runner.collect = lambda: events.append("collect")
        runner.ratings = lambda data: {OUR_TEAM: {"rating": 1500}, "peer": {"rating": 1501}}
        def save(phase=None, **details):
            if phase:
                runner.state["phase"] = phase
            runner.state.update(details)
        runner.save = save
        def cli(args, label, mutation=False):
            events.append(label)
            if mutation:
                assert runner.state["jobs"][-1]["status"] == "submitting"
                assert "live" in events and "quota-before-create" in events
                return '{"groupId":"new-group"}'
            count = fresh_used if label == "quota-before-create" and fresh_used is not None else used
            return json.dumps({"quota": quota(count), "team": {"id": OUR_TEAM}, "ready": True})
        runner.cli = cli
        return runner, events

    runner, events = dispatch_stub(["queued", "pending"])
    assert runner.step() == 1
    assert "collect" not in events and runner.state["jobs"][-1]["group_id"] == "new-group"
    for used, fresh_used in ((50, None), (49, 50)):
        runner, events = dispatch_stub(["queued", "pending"], used, fresh_used)
        assert runner.step() >= 10 and "collect" in events
        assert runner.state["jobs"][-1]["status"] == "pending"
        assert not any(e.endswith("-create") and e != "quota-before-create" for e in events)
    runner, events = dispatch_stub(["queued"])
    assert runner.step() == 30 and events == ["collect"]
    runner, events = dispatch_stub(["queued", "pending"])
    runner.state["sources"]["peer"] = "old-0"
    assert runner.step() == 60 and "collect" in events
    assert runner.state["jobs"][-1]["status"] == "pending"
    for status in ("submitting", "uncertain"):
        runner, events = dispatch_stub([status, "pending"])
        try:
            runner.step()
            raise AssertionError("Queue-first bypassed reconciliation")
        except Halt:
            pass
        assert events == []
    runner, events = dispatch_stub(["pending"])
    original_cli = runner.cli
    def rejected_cli(args, label, mutation=False):
        if mutation:
            raise RejectedRateLimit("explicit rejection", 5, "test-receipt")
        return original_cli(args, label, mutation)
    runner.cli = rejected_cli
    assert runner.step() == 15
    rejected_job = runner.state["jobs"][0]
    assert rejected_job["status"] == "pending" and "queued_at" not in rejected_job
    assert len(rejected_job["rejected_attempts"]) == 1
    assert rejected_job["rejected_attempts"][0]["response_capture"] == "test-receipt"
    runner, events = dispatch_stub(["pending"])
    runner.state["dispatch_disabled_reason"] = "User closed this opponent panel."
    try:
        runner.step()
        raise AssertionError("Closed campaign attempted dispatch")
    except Halt:
        pass
    assert events == []
    print("Self-test passed: group quota units, server counter, local lag protection, "
          "deduplication, expiry, ambiguous creates, version guards, queue-first ordering "
          "and collection while dispatch is blocked.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, default=DEFAULT)
    parser.add_argument("--queue-first", action="store_true",
                        help="Queue eligible groups first; collect after dispatch or while blocked.")
    mode = parser.add_mutually_exclusive_group(required=True)
    for name in ("prepare", "step", "watch", "report", "collect", "self-test"):
        mode.add_argument("--" + name, action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    with exclusive(args.campaign / "runner.lock"):
        campaign = Campaign(args.campaign, queue_first=args.queue_first)
        try:
            if not args.prepare and not args.report:
                campaign.state.pop("error", None)
            campaign.save()
            campaign.render()
            if args.prepare or args.report:
                return
            if args.collect:
                campaign.verify_source()
                campaign.collect()
                campaign.save("stopped_by_user_top20_only" if campaign.state.get("dispatch_disabled_reason")
                              else "collection_finished")
                campaign.render()
                print(json.dumps(load(campaign.folder / "progress.json")), flush=True)
                return
            while True:
                delay = campaign.step()
                campaign.render()
                print(json.dumps(load(campaign.folder / "progress.json")), flush=True)
                if not args.watch or not delay:
                    return
                time.sleep(delay)
        except BaseException as error:
            campaign.save("stopped", error=str(error))
            campaign.render()
            raise


if __name__ == "__main__":
    main()
