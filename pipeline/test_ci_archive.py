"""ci_archive.py (archive.yml): keep the raw repo current and heal it. No post, no content commit.
Run: python pipeline/test_ci_archive.py   (temp directories, a local bare repo as the raw remote, EirGrid requests faked,
no network and no waiting)"""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ci_archive
import ci_daily
import fetch
import raw_archive as ra
import raw_gap
from test_ci_retry import FakeResp, eirgrid_body
from test_raw_gap import put_day, put_eirgrid, put_semo

TARGET = date(2026, 11, 10)


@contextlib.contextmanager
def env(seeded=None, manifest_text=""):
    """A bare raw repo holding the 15-day window up to TARGET-1 (or `seeded`: {date: kwargs for put_day} / None to
    skip a day), an empty runner data dir, SEMOpx and EirGrid fetches faked."""
    names = (("ci_daily", ci_daily, ("DATA_DIR",)), ("ra", ra, ("DATA_DIR", "MANIFEST")),
             ("ci_archive", ci_archive, ("fetch_semo",)), ("fetch", fetch, ("requests", "_sleep")))
    saved = {n: {a: getattr(m, a) for a in attrs} for n, m, attrs in names}
    saved_env = os.environ.get("RAW_ARCHIVE_REMOTE")
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        e = type("Env", (), {})()
        e.requests, e.feed, e.semo_calls, e.semo_wrong, e.semo_error = [], {}, [], False, None
        e.remote, runner, seed = tmp / "raw.git", tmp / "runner", tmp / "seed"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(e.remote)], check=True)
        os.environ["RAW_ARCHIVE_REMOTE"] = str(e.remote)
        ra.MANIFEST = tmp / "manifest.sha256"
        ra.MANIFEST.write_text(manifest_text)
        e.manifest = ra.MANIFEST
        plan = seeded if seeded is not None else {TARGET - timedelta(days=k): {} for k in range(1, 16)}
        for d, kw in plan.items():
            if kw is not None:
                put_day(seed, d, **kw)
        ra.DATA_DIR = seed / "data"
        files = sorted(p for p in (seed / "data").rglob("*") if p.is_file())
        with contextlib.redirect_stdout(io.StringIO()):
            if files:
                ra.push_files(files, str(e.remote), "seed", {})
        ra.DATA_DIR = ci_daily.DATA_DIR = runner / "data"
        runner.mkdir()

        def get(url, params=None, timeout=None):
            day = datetime.strptime(params["dateFrom"], "%d-%b-%Y").date().isoformat()
            area = "wind" if params["chartType"] == "wind" else "demand"
            e.requests.append((day, area))
            return FakeResp(eirgrid_body(day, area, 100.0, e.feed.get((day, area), 96)))

        def semo(delivery_date=None, out_dir=None):
            e.semo_calls.append(delivery_date)
            if e.semo_error:
                raise RuntimeError(e.semo_error)
            made = put_semo(runner, delivery_date + timedelta(days=1) if e.semo_wrong else delivery_date)
            if e.semo_wrong:                                  # D+1's content under D's file name
                stamp = f"{delivery_date - timedelta(days=1):%Y%m%d}"
                made.rename(made.with_name(f"MarketResult_SEM-DA_PWR-MRC-D+1_{stamp}110000_{stamp}115501.csv"))
            return None

        ci_archive.fetch_semo = semo
        fetch.requests = type("R", (), {"get": staticmethod(get), "RequestException": Exception, "HTTPError": Exception})
        fetch._sleep = lambda s: None
        git = lambda *a: subprocess.run(["git", "--git-dir", str(e.remote), *a], capture_output=True, text=True, check=True).stdout
        e.head = lambda: git("rev-parse", "main").strip()
        e.commits = lambda: int(git("rev-list", "--count", "main").strip())
        e.archived = lambda rel: git("show", f"main:{rel}")
        e.listing = lambda: set(git("ls-tree", "-r", "--name-only", "main").split())

        def run(target=TARGET):
            out, code = io.StringIO(), 0
            with contextlib.redirect_stdout(out):
                code = ci_archive.run(target, str(e.remote))
            e.last_requests, e.last_semo = list(e.requests), list(e.semo_calls)
            e.wipe()
            return code, out.getvalue()

        def wipe():                                      # the runner is ephemeral: the next run starts empty
            import shutil
            shutil.rmtree(runner / "data", ignore_errors=True)
            e.requests.clear(); e.semo_calls.clear()
        e.run, e.wipe = run, wipe
        try:
            yield e
        finally:
            for n, m, attrs in names:
                for a in attrs:
                    setattr(m, a, saved[n][a])
            if saved_env is None:
                os.environ.pop("RAW_ARCHIVE_REMOTE", None)
            else:
                os.environ["RAW_ARCHIVE_REMOTE"] = saved_env


def rel(d, name):
    return f"data/eirgrid_raw/{d}/{name}.json"


def test_a_complete_window_is_a_noop_with_no_request_and_no_push():
    with env() as e:
        head = e.head()
        reqs = []
        orig = fetch.requests.get
        fetch.requests.get = staticmethod(lambda *a, **k: reqs.append(1) or orig(*a, **k))
        code, out = e.run(TARGET - timedelta(days=1))
        assert code == 0 and "is complete; nothing to do" in out and e.head() == head and not reqs and not e.semo_calls, out


def test_a_new_day_is_fetched_verified_and_pushed_in_one_commit_and_the_retry_is_a_noop():
    with env() as e:
        commits = e.commits()
        code, out = e.run()
        assert code == 0, out
        assert e.commits() == commits + 1 and "pushed 3 raw files" in out, out
        assert sorted(set(e.last_requests)) == [(TARGET.isoformat(), "demand"), (TARGET.isoformat(), "wind")], e.last_requests
        assert e.last_semo == [TARGET]                                          # one SEMOpx fetch, for the target only
        have = e.listing()
        assert raw_gap.missing(have, TARGET, TARGET) == [], have
        head = e.head()
        code, out = e.run()                                                    # the 10:15 attempt
        assert code == 0 and e.head() == head and not e.requests and not e.semo_calls and "nothing to do" in out, out


def test_a_partial_target_fails_loudly_then_the_retry_completes_it():
    with env() as e:
        e.feed = {(TARGET.isoformat(), "demand"): 60}                           # 30/48 half-hours: the feed saved early
        code, out = e.run()
        assert code == 1 and f"::error::{TARGET} is still short in the archive: demand 30/48" in out, out
        assert rel(TARGET, "demand") in e.listing()                             # the partial is recorded
        e.feed = {}
        code, out = e.run()                                                    # the 10:15 retry
        assert code == 0 and "replacing" in out and "pushed 0 raw files to the raw repo (1 replaced)" in out, out
        assert len(e.archived(rel(TARGET, "demand"))) > 5000                    # the complete one is archived now


def test_heal_request_list_is_exactly_the_empty_area():
    hole = TARGET - timedelta(days=5)
    plan = {TARGET - timedelta(days=k): {} for k in range(0, 16)}
    plan[hole] = {"demand_quarters": 0}
    with env(plan) as e:
        seen = []
        orig = fetch.requests.get
        fetch.requests.get = staticmethod(lambda url, params=None, timeout=None: (seen.append(
            (datetime.strptime(params["dateFrom"], "%d-%b-%Y").date().isoformat(), params["chartType"])), orig(url, params, timeout))[1])
        code, out = e.run()
        assert code == 0 and seen == [(hole.isoformat(), "generation")], (seen, out)   # EirGrid calls demand "generation"
        assert len(e.archived(rel(hole, "demand"))) > 5000 and "1 replaced" in out, out


def test_heal_leaves_a_manifest_pinned_incomplete_file_alone():
    hole = TARGET - timedelta(days=4)
    plan = {TARGET - timedelta(days=k): {} for k in range(0, 16)}
    plan[hole] = {"demand_quarters": 60}
    with env(plan) as e:
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "demand.json"
            f.write_text(eirgrid_body(hole.isoformat(), "demand", 100.0, 60))
            ra.MANIFEST.write_text(f"{ra.sha256(f)}  {rel(hole, 'demand')}\n")
        seen = []
        orig = fetch.requests.get
        fetch.requests.get = staticmethod(lambda url, params=None, timeout=None: (seen.append(params["dateFrom"]), orig(url, params, timeout))[1])
        head = e.head()
        code, out = e.run()
        assert code == 0 and not seen and e.head() == head, (seen, out)
        assert f"::warning::{hole} is still short in the archive: demand 30/48" in out, out


def test_missing_days_in_the_window_are_filled():
    gap = TARGET - timedelta(days=3)
    plan = {TARGET - timedelta(days=k): ({} if TARGET - timedelta(days=k) != gap else None) for k in range(0, 16)}
    with env(plan) as e:
        code, out = e.run()
        assert code == 0, out
        assert raw_gap.missing(e.listing(), gap, gap) == [], e.listing()


def test_a_semo_file_for_the_wrong_date_is_refused_and_nothing_is_pushed():
    with env() as e:
        e.semo_wrong = True
        head = e.head()
        code, out = e.run()
        assert code == 1 and "refused: is for 2026-11-11, not 2026-11-10" in out and e.head() == head, out


def test_a_semo_fetch_failure_fails_the_run_and_names_it():
    with env() as e:
        e.semo_error = "No SEM-DA market result CSV found (2026-11-10)"
        code, out = e.run()
        assert code == 1 and "is still short in the archive: semo" in out and "No SEM-DA market result CSV" in out, out
        assert rel(TARGET, "wind") in e.listing()          # the half that did arrive is archived, not lost


def test_the_workflow_owns_the_raw_schedule_and_commits_nothing_to_this_repo():
    text = (Path(__file__).parent.parent / ".github" / "workflows" / "archive.yml").read_text()
    assert '- cron: "15 7 * * *"' in text and '- cron: "15 10 * * *"' in text and "workflow_dispatch" in text
    assert "contents: read" in text and "contents: write" not in text
    assert "python pipeline/ci_archive.py" in text and "ci_publish" not in text and "git push" not in text
    assert text.count("DATA_REPO_TOKEN: ${{ secrets.DATA_REPO_TOKEN }}") == 2         # the guard step and the run step only


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
