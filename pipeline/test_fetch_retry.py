"""EirGrid fetch retry (fetch.fetch_areas): bounded, logged, most-complete-wins, and the strict wind check unchanged.
Run: python pipeline/test_fetch_retry.py   (temp directories only; requests.get is scripted and sleep is mocked: no network, no waiting)

Real: ci_daily.main, run_daily.main, fetch.fetch_wind_and_demand / fetch_areas, raw_archive restore/push (git).
Stubbed (as in test_ci_retry): the SEMOpx download, the DAM CSV parse, and the post scaffold, which here omits the
"Wind % of Demand" section when wind % is unavailable, as the real one does, so the strict wind check can be seen to bite.

1. A flaky feed (demand empty x4, then complete) is retried and the day publishes; both areas share the rounds and the waits.
2. An always-empty feed is refused after the last attempt, in bounded time (sleep mocked), with nothing published.
3. A complete first fetch makes no retry and no wait.
4. A timeout is retried; the read timeout is 30 s (env-configurable); the attempts are logged and tabled in $GITHUB_STEP_SUMMARY.
5. The most complete response is the one archived, whatever order they arrive in.
6. Defaults: one attempt outside CI, ten in CI, EIRGRID_ATTEMPTS overrides; backfill/heal callers (no CI) never retry."""

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fetch
import process
import raw_archive
import run_daily
from test_ci_retry import DAY, ISO, FakeResp, ci_env, eirgrid_body, run_ci
from update_manifest import update_manifest

PREV = (DAY - timedelta(days=1)).isoformat()
EMPTY = '{"Rows":[]}'
ENV_KEYS = ("EIRGRID_ATTEMPTS", "EIRGRID_RETRY_MIN_S", "EIRGRID_RETRY_MAX_S", "EIRGRID_READ_TIMEOUT_S", "CI", "GITHUB_STEP_SUMMARY")


@contextlib.contextmanager
def env_vars(**kw):
    saved = {k: os.environ.get(k) for k in ENV_KEYS}
    for k in ENV_KEYS:
        os.environ.pop(k, None)
    os.environ.update({k: str(v) for k, v in kw.items()})
    try:
        yield
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v


@contextlib.contextmanager
def scripted_feed(script=None, **env):
    """ci_env with requests.get wrapped so chosen (day, area) requests get a scripted answer first, in order:
    "empty", "timeout", or "qN" (a partial day of N 15-minute rows); anything else falls through to the harness."""
    with env_vars(**env), ci_env() as e:
        e.script = {k: list(v) for k, v in (script or {}).items()}
        e.calls, e.sleeps = [], []
        inner = fetch.requests.get

        def get(url, params=None, timeout=None):
            from datetime import datetime
            day = datetime.strptime(params["dateFrom"], "%d-%b-%Y").date().isoformat()
            area = "wind" if params["chartType"] == "wind" else "demand"
            e.calls.append((day, area, timeout))
            queue = e.script.get((day, area))
            if queue:
                act = queue.pop(0)
                if act == "empty":
                    return FakeResp(EMPTY)
                if act == "timeout":
                    raise TimeoutError("Read timed out. (read timeout=30)")
                if act.startswith("q"):
                    return FakeResp(eirgrid_body(day, area, 100.0, int(act[1:])))
            return inner(url, params=params, timeout=timeout)

        def scaffold(delivery_date, explicit_file=None, title="", eirgrid_df=None, **k):
            post = e.content / "daily" / ISO / "index.md"
            post.parent.mkdir(parents=True, exist_ok=True)
            # The real rule (process.MIN_WIND_FRACTION): a wind % section needs 75% of the day's periods. The previous
            # day's demand supplies the first two half-hours even when the target day's demand feed is empty.
            has_wind_pct = (eirgrid_df is not None
                            and eirgrid_df["WindGeneration_pct"].notna().sum() >= process.MIN_WIND_FRACTION * len(eirgrid_df))
            post.write_text(f"---\ntitle: {title}\n---\n{'Wind % of Demand' if has_wind_pct else ''}\n{eirgrid_df.to_csv(index=False)}")

        fetch.requests = type("R", (), {"get": staticmethod(get), "RequestException": Exception, "HTTPError": Exception})
        run_daily.scaffold_daily = scaffold
        saved = (fetch._sleep, len(fetch.ATTEMPT_LOG))
        fetch._sleep = e.sleeps.append
        try:
            yield e
        finally:
            fetch._sleep = saved[0]


def n_calls(e, day, area):
    return sum(1 for d, a, _ in e.calls if (d, a) == (day, area))


def test_flaky_demand_empty_x4_then_complete_publishes_and_logs_every_attempt():
    with tempfile.TemporaryDirectory() as t:
        summary = Path(t) / "summary.md"
        with scripted_feed({(ISO, "demand"): ["empty"] * 4}, EIRGRID_ATTEMPTS=10, GITHUB_STEP_SUMMARY=summary) as e:
            code, out = run_ci(["--date", ISO, "--restore-raw"])
            assert code is None and "STATUS=generated" in out, (code, out)
            assert n_calls(e, ISO, "demand") == 5, e.calls          # four empty, the fifth complete: stop
            assert n_calls(e, ISO, "wind") == 1, e.calls            # wind was complete first time and is not asked again
            assert len(e.sleeps) == 4 and all(60 <= s <= 90 for s in e.sleeps), e.sleeps   # one shared wait per round
            assert "Wind % of Demand" in e.post.read_text()
            raw = json.loads((e.data / "eirgrid_raw" / ISO / "demand.json").read_text())
            assert len(raw["Rows"]) == 96                           # the complete response is the archive, not an empty one
            table = summary.read_text()
            assert "### EirGrid fetch attempts" in table
            demand_rows = [l for l in table.splitlines() if l.startswith(f"| {ISO} | demand |")]
            assert len(demand_rows) == 5 and demand_rows[0].count("| incomplete |") == 1 and demand_rows[-1].endswith("| complete |"), demand_rows
            assert "| 0/48 |" in demand_rows[0] and "| 48/48 |" in demand_rows[-1], demand_rows
            assert "attempt 1/10: HTTP 200" in out and "retrying in" in out


def test_always_empty_demand_refuses_after_the_last_attempt_in_bounded_time():
    with scripted_feed({(ISO, "demand"): ["empty"] * 50}, EIRGRID_ATTEMPTS=10) as e:
        code, out = run_ci(["--date", ISO, "--restore-raw"])
        assert code == 1 and "no wind figures" in out, (code, out)   # the strict check, unchanged
        assert not e.post.exists(), "a post without wind figures was left behind"
        assert n_calls(e, ISO, "demand") == 10, e.calls             # exactly the configured attempts, then stop
        assert n_calls(e, ISO, "wind") == 1
        assert len(e.sleeps) == 9 and 9 * 60 <= sum(e.sleeps) <= 9 * 90, e.sleeps   # worst case 13.5 minutes of waiting
        assert e.requests_made.count((ISO, "wind")) == 1


def test_a_complete_first_fetch_makes_no_retry_and_no_wait():
    with scripted_feed(None, EIRGRID_ATTEMPTS=10) as e:
        code, out = run_ci(["--date", ISO, "--restore-raw"])
        assert code is None and "STATUS=generated" in out, (code, out)
        assert n_calls(e, ISO, "demand") == 1 and n_calls(e, ISO, "wind") == 1, e.calls
        assert e.sleeps == [] and "retrying in" not in out


def test_a_timeout_is_retried_with_a_30_second_read_timeout():
    with scripted_feed({(ISO, "wind"): ["timeout", "timeout"]}, EIRGRID_ATTEMPTS=10) as e:
        code, out = run_ci(["--date", ISO, "--restore-raw"])
        assert code is None and "STATUS=generated" in out, (code, out)
        assert n_calls(e, ISO, "wind") == 3 and len(e.sleeps) == 2, (e.calls, e.sleeps)
        assert all(to == (15, 30.0) for *_, to in e.calls), "connect 15 s, read 30 s on every request"
        assert "FAILED (TimeoutError" in out
        # demand was complete in round 1 and is not asked again while wind is retried
        assert n_calls(e, ISO, "demand") == 1
    with scripted_feed({(ISO, "wind"): ["timeout"]}, EIRGRID_ATTEMPTS=3, EIRGRID_READ_TIMEOUT_S=12,
                       EIRGRID_RETRY_MIN_S=1, EIRGRID_RETRY_MAX_S=2) as e:
        run_ci(["--date", ISO, "--restore-raw"])
        assert all(to == (15, 12.0) for *_, to in e.calls) and all(1 <= s <= 2 for s in e.sleeps), (e.calls, e.sleeps)


def test_the_previous_day_tail_ci_daily_fills_is_retried_too():
    with scripted_feed({(PREV, "demand"): ["empty", "empty"]}, EIRGRID_ATTEMPTS=10) as e:
        code, out = run_ci(["--date", ISO, "--restore-raw"])
        assert code is None and "STATUS=generated" in out, (code, out)
        assert n_calls(e, PREV, "demand") == 3 and n_calls(e, PREV, "wind") == 1, e.calls
        assert len(e.sleeps) == 2 and len((json.loads((e.data / "eirgrid_raw" / PREV / "demand.json").read_text()))["Rows"]) == 96
    # an archive that already has rows is not fetched at all (it could not be replaced anyway)
    with scripted_feed(None, EIRGRID_ATTEMPTS=10) as e:
        f = e.data / "eirgrid_raw" / PREV / "demand.json"
        f.parent.mkdir(parents=True)
        f.write_text(eirgrid_body(PREV, "demand", 100.0, 96))
        run_ci(["--date", ISO])
        assert n_calls(e, PREV, "demand") == 0, e.calls


TAIL_REL = f"data/eirgrid_raw/{PREV}/demand.json"


def write_tail(e, quarters: int) -> Path:
    """The previous day's archived demand file: 96 quarters is a complete day, 60 is 30 of the 48 half-hours."""
    f = e.data / "eirgrid_raw" / PREV / "demand.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(eirgrid_body(PREV, "demand", 100.0, quarters))
    return f


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def test_a_partial_unpinned_tail_is_refetched_superseded_once_and_archived_with_both_hashes():
    with scripted_feed(None, EIRGRID_ATTEMPTS=10) as e:
        old = write_tail(e, 60).read_bytes()                       # 30 of 48 half-hours, not in the manifest
        with contextlib.redirect_stdout(io.StringIO()):
            e.seed()                                               # the raw repo holds the partial file
        e.wipe_runner()
        code, out = run_ci(["--date", ISO, "--restore-raw"])       # the run restores it from the archive
        assert code is None and "STATUS=generated" in out, (code, out)
        f = e.data / "eirgrid_raw" / PREV / "demand.json"
        new = f.read_bytes()
        assert n_calls(e, PREV, "demand") == 1 and len(json.loads(new)["Rows"]) == 96, e.calls
        assert (f"[tail] superseded {TAIL_REL}: 30/48 -> 48/48 half-hours; sha256 {sha(old)} -> {sha(new)}") in out, out
        assert TAIL_REL in e.manifest.read_text(), "the superseded tail must be pinned: the post rests on it"
        # the push replaces the archived copy once and logs both hashes; afterwards the archive holds the complete file
        pushed = io.StringIO()
        with contextlib.redirect_stdout(pushed):
            e.push()
        assert f"replacing {TAIL_REL}" in pushed.getvalue() and sha(old) in pushed.getvalue() and sha(new) in pushed.getvalue()
        assert len(json.loads(e.archived(TAIL_REL))["Rows"]) == 96


def test_a_pinned_partial_tail_is_never_refetched():
    with scripted_feed(None, EIRGRID_ATTEMPTS=10) as e:
        f = write_tail(e, 60)
        before = f.read_bytes()
        update_manifest([f], e.manifest, e.root)                   # a published post rests on this exact file
        code, out = run_ci(["--date", ISO])
        assert code is None and "STATUS=generated" in out, (code, out)
        assert n_calls(e, PREV, "demand") == 0, e.calls
        assert f.read_bytes() == before and f"[tail] {TAIL_REL} holds 30/48 half-hours but the manifest pins it" in out, out


def test_a_complete_tail_makes_no_fetch():
    with scripted_feed(None, EIRGRID_ATTEMPTS=10) as e:
        wind = e.data / "eirgrid_raw" / PREV / "wind.json"
        wind.parent.mkdir(parents=True, exist_ok=True)
        wind.write_text(eirgrid_body(PREV, "wind", 100.0, 96))
        write_tail(e, 96)
        code, out = run_ci(["--date", ISO])
        assert code is None and "STATUS=generated" in out, (code, out)
        assert n_calls(e, PREV, "demand") == 0 and n_calls(e, PREV, "wind") == 0, e.calls
        assert "[tail]" not in out


def test_an_unpinned_partial_tail_is_not_replaced_by_a_response_that_is_no_better():
    with scripted_feed({(PREV, "demand"): ["q40"] * 10}, EIRGRID_ATTEMPTS=10) as e:   # live only ever gives 20 half-hours
        f = write_tail(e, 60)
        before = f.read_bytes()
        code, out = run_ci(["--date", ISO])
        assert code is None and "STATUS=generated" in out, (code, out)
        assert n_calls(e, PREV, "demand") == 10 and len(e.sleeps) == 9, (e.calls, e.sleeps)
        assert f.read_bytes() == before, "an incomplete response replaced an archived file that held more"
        assert f"[tail] live demand for {PREV} is no better (20/48); keeping the archived file (30/48)" in out, out
        assert TAIL_REL not in e.manifest.read_text()


def test_the_most_complete_response_is_archived_whatever_the_order():
    for order, best in ((["q60", "q40", "q20"], 60), (["q20", "q60", "q40"], 60), (["q40", "q40", "q40"], 40)):
        with tempfile.TemporaryDirectory() as t, scripted_feed({(ISO, "demand"): list(order)}, EIRGRID_ATTEMPTS=3) as e:
            with contextlib.redirect_stdout(io.StringIO()):
                frame = fetch.fetch_area(DAY, "demand", out_dir=t)
            rows = json.loads((Path(t) / "eirgrid_raw" / ISO / "demand.json").read_text())["Rows"]
            assert len(rows) == best and frame is not None and len(e.sleeps) == 2, (order, len(rows), e.sleeps)


def test_defaults_and_overrides():
    with env_vars():
        assert fetch.configured_attempts() == 1 and fetch.configured_attempts(ci=True) == 10
    with env_vars(CI="true"):
        assert fetch.configured_attempts() == 10
    with env_vars(CI="true", EIRGRID_ATTEMPTS=4):
        assert fetch.configured_attempts() == 4
    with env_vars(EIRGRID_ATTEMPTS="nonsense"):
        with contextlib.redirect_stdout(io.StringIO()):
            assert fetch.configured_attempts() == 1
    with env_vars():
        # backfill / heal call fetch_area with no attempts and no CI: one request, no wait, whatever comes back
        with scripted_feed({(ISO, "demand"): ["empty"] * 5}) as e:
            with contextlib.redirect_stdout(io.StringIO()):
                assert fetch.fetch_area(DAY, "demand", out_dir=e.data, overwrite_raw=False) is None
            assert n_calls(e, ISO, "demand") == 1 and e.sleeps == []


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
