#!/usr/bin/env python3
"""Run a fixed map panel in five-map groups against current top-20 opponents."""
import argparse
import json
import time
from collections import Counter
from pathlib import Path

from map_campaign import (
    Campaign, Halt, RejectedRateLimit, ROOT, OUR_TEAM, digest, exclusive,
    group_budget, load, now, stamp, text, write,
)


def eligible(team):
    return team is not None and type(team.get("rank")) is int and 1 <= team["rank"] <= 20


def make_jobs(config):
    maps = config["maps"]
    jobs = []
    for start in range(0, len(maps), 5):
        for i, team in enumerate(config["opponents"]):
            assert len(config["sides"][team["teamId"]]) == len(maps)
            jobs.append({
                "id": f"p{i}" if len(maps) == 5 else f"b{start // 5:02}-p{i}",
                "opponent_id": team["teamId"], "opponent_name": team["name"],
                "maps": maps[start:start + 5],
                "sides": config["sides"][team["teamId"]][start:start + 5],
                "source_group": config.get("source_groups", {}).get(team["teamId"]),
                "status": "pending",
            })
    return jobs


class Top20Panel(Campaign):
    def __init__(self, folder):
        self.folder = folder.resolve()
        self.config_path = self.folder / "panel.json"
        self.config = load(self.config_path)
        assert self.config["team_id"] == OUR_TEAM
        assert self.config["opponent_rule"] == "current_top20"
        assert len(self.config["maps"]) >= 5 and len(self.config["maps"]) % 5 == 0
        assert len({m["id"] for m in self.config["maps"]}) == len(self.config["maps"])
        assert len(self.config["opponents"]) == 5
        assert len({t["teamId"] for t in self.config["opponents"]}) == 5
        self.state_path = self.folder / "state.json"
        self.serial, self.queue_first = 0, True
        if self.state_path.exists():
            self.state = load(self.state_path)
        else:
            self.state = {
                "phase": "prepared", "config_sha256": digest(self.config_path),
                "jobs": make_jobs(self.config),
            }
        if self.state["config_sha256"] != digest(self.config_path):
            raise Halt("Panel configuration changed; review before resuming.")

    def render(self):
        matches = []
        for job in self.state["jobs"]:
            if job["status"] == "complete":
                matches.extend(load(self.folder / "results" / f"{job['id']}.json")["matches"])
        assert len({m["match_id"] for m in matches}) == len(matches)
        total_maps = len(self.config["maps"])
        target = total_maps * len(self.config["opponents"])
        counts = Counter(j["status"] for j in self.state["jobs"])
        progress = {
            "results": len(matches), "target": target, "phase": self.state["phase"],
            "complete_maps": sum(sum(m["map_id"] == mp["id"] for m in matches) == 5
                                 for mp in self.config["maps"]), "total_maps": total_maps,
            "groups": dict(counts), "updated": self.state.get("last_update"),
            "runner_pid": self.state.get("runner_pid"), "error": self.state.get("error"),
        }
        write(self.folder / "progress.json", progress)
        lines = [
            f"# {self.config['label']}", "",
            f"Fixed v{self.config['submission_version']}; {len(matches)}/{target} results. "
            f"State: {self.state['phase']}. Updated: {self.state.get('last_update')}.", "",
            "Every new request requires a fresh current rank of 1-20. "
            "Already accepted games retain their creation-time rank evidence.", "",
            "| Map | Opponent | Rank at request | Side | Result | Gems for-against | Deaths | Gems lost | Match |",
            "| --- | --- | ---: | --- | --- | --- | ---: | ---: | --- |",
        ]
        ranks = {j["group_id"]: j.get("opponent_rank", "?") for j in self.state["jobs"] if j.get("group_id")}
        for m in matches:
            lines.append(
                f"| {m['map']} | {m['opponent_name'].replace('|', '/')} | {ranks[m['group_id']]} "
                f"| {m['side']} | {m['result']} | {m['us']['submitted']}-{m['opponent']['submitted']} "
                f"| {m['us']['metrics']['deaths']:.0f} | {m['us']['gem_loss']} | `{m['match_id']}` |")
        if self.state.get("error"):
            lines += ["", "Stopped: " + self.state["error"]]
        text(ROOT / self.config["report_path"], "\n".join(lines) + "\n")

    def step(self):
        if self.state.get("dispatch_disabled_reason"):
            raise Halt(self.state["dispatch_disabled_reason"])
        self.verify_source()
        self.check_journal()
        pending = [j for j in self.state["jobs"] if j["status"] == "pending"]
        if not pending:
            self.collect()
            done = all(j["status"] == "complete" for j in self.state["jobs"])
            self.save("complete" if done else "waiting_for_results")
            return 0 if done else 30

        self.verify_live()
        ladder = json.loads(self.cli(["ladder", "--page", "1", "--limit", "20", "--json"], "top20-before-create"))
        captured_at = now().isoformat()
        teams = {t["teamId"]: t for t in ladder["teams"]}
        job = next((j for j in pending if eligible(teams.get(j["opponent_id"]))), None)
        if job is None:
            self.collect()
            self.save("waiting_for_top20_eligibility")
            return 60
        opponent = teams[job["opponent_id"]]
        assert eligible(opponent) and opponent["teamId"] != OUR_TEAM
        quota = json.loads(self.cli(["match-groups", "quota", "--json"], "quota-before-create"))
        if quota["team"]["id"] != OUR_TEAM or not quota["ready"]:
            raise Halt("Team identity/readiness changed.")
        ledger = list(self.state["jobs"])
        for path in self.config.get("additional_ledgers", []):
            ledger.extend(load(ROOT / path)["jobs"])
        used, available, next_at = group_budget(quota["quota"], ledger, now())
        self.save(server_quota=quota["quota"], quota_groups_available=available)
        if not available:
            self.collect()
            self.save("waiting_for_hourly_quota")
            return min(300, max(15, (next_at - now()).total_seconds()))
        if (now() - stamp(captured_at)).total_seconds() > 10:
            self.save("refreshing_top20_after_slow_quota_read")
            return 5
        args = ["match-groups", "create", job["opponent_id"],
                "--maps", ",".join(m["id"] for m in job["maps"]),
                "--sides", ",".join(job["sides"]), "--json"]
        if job.get("source_group"):
            args += ["--source-group", job["source_group"]]
        job.update(status="submitting", queued_at=now().isoformat(),
                   opponent_rank=opponent["rank"], opponent_rating=opponent["rating"],
                   rank_checked_at=captured_at, command=["cambc", *args])
        self.save("submitting")
        try:
            response = json.loads(self.cli(args, job["id"] + "-create", mutation=True))
            if not response.get("groupId"):
                raise Halt("Create response has no group ID")
        except RejectedRateLimit as error:
            job.setdefault("rejected_attempts", []).append({
                "queued_at": job["queued_at"], "command": job["command"],
                "reason": str(error), "response_capture": error.capture,
                "opponent_rank": job["opponent_rank"], "rank_checked_at": captured_at,
            })
            job["status"] = "pending"
            job.pop("queued_at")
            self.save("waiting_for_api_rate_limit")
            print(f"Explicit API rejection for {job['id']}; recheck rank/version/quota after backoff.", flush=True)
            return max(15, error.retry_after)
        except BaseException:
            job["status"] = "uncertain"
            self.save("needs_reconciliation")
            raise
        job.update(status="queued", group_id=response["groupId"], create_response=response)
        self.save("queueing", quota_groups_available=available - 1)
        print(f"Queued {job['opponent_name']} at rank {job['opponent_rank']}: "
              f"{response['groupId']} ({used + 1}/50 groups).", flush=True)
        return 5


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, nargs="?")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        for rank in (1, 20):
            assert eligible({"rank": rank})
        for team in (None, {}, {"rank": 0}, {"rank": 21}, {"rank": 500},
                     {"rank": "1"}, {"rank": True}, {"rating": 2400}):
            assert not eligible(team)
        for size in (5, 70):
            config = {
                "maps": [{"id": str(i)} for i in range(size)],
                "opponents": [{"teamId": f"t{i}", "name": f"Team {i}"} for i in range(5)],
                "sides": {f"t{i}": ["a" if (i + j) % 2 == 0 else "b" for j in range(size)] for i in range(5)},
                "source_groups": {f"t{i}": f"source{i}" for i in range(5)},
            }
            jobs = make_jobs(config)
            assert len(jobs) == size and len({j["id"] for j in jobs}) == size
            pairs = [(j["opponent_id"], m["id"]) for j in jobs for m in j["maps"]]
            assert len(pairs) == len(set(pairs)) == size * 5
            for job in jobs:
                assert len(job["maps"]) == len(job["sides"]) == 5
                assert job["source_group"] == config["source_groups"][job["opponent_id"]]
                for mp, side in zip(job["maps"], job["sides"]):
                    assert side == config["sides"][job["opponent_id"]][int(mp["id"])]
            if size == 5:
                assert [j["id"] for j in jobs] == [f"p{i}" for i in range(5)]
        print("Top-20 eligibility and 5/70-map scheduling checks passed; rating never substitutes for rank.")
        return
    if args.folder is None:
        parser.error("folder is required")
    with exclusive(args.folder / "runner.lock"):
        panel = Top20Panel(args.folder)
        try:
            panel.state.pop("error", None)
            panel.save()
            panel.render()
            if args.report:
                return
            while True:
                delay = panel.step()
                panel.render()
                print(json.dumps(load(panel.folder / "progress.json")), flush=True)
                if not args.watch or not delay:
                    return
                time.sleep(delay)
        except BaseException as error:
            panel.save("stopped", error=str(error))
            panel.render()
            raise


if __name__ == "__main__":
    main()
