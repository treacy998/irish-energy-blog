"""ci_deadman.py (deadman.yml): the raw repo has yesterday's files; on Tuesdays the last Sunday's weekly post exists.
Run: python pipeline/test_ci_deadman.py   (temp directories and a local bare repo as the raw remote; no network)"""

import contextlib
import io
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ci_deadman
import raw_archive as ra
from test_raw_gap import put_day, put_eirgrid, put_semo

TODAY = date(2026, 11, 10)                       # a Tuesday
YESTERDAY = TODAY - timedelta(days=1)


@contextlib.contextmanager
def raw_repo(**kw):
    saved = (ra.DATA_DIR, ra.MANIFEST)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        remote = tmp / "raw.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
        ra.MANIFEST = tmp / "m"
        ra.MANIFEST.write_text("")
        seed = tmp / "seed"
        put_day(seed, YESTERDAY - timedelta(days=1))                       # something is always there
        if kw.get("semo", True):
            put_semo(seed, YESTERDAY)
        if kw.get("eirgrid", True):
            put_eirgrid(seed, YESTERDAY, quarters=kw.get("quarters", 96), demand_quarters=kw.get("demand_quarters"))
        ra.DATA_DIR = seed / "data"
        with contextlib.redirect_stdout(io.StringIO()):
            ra.push_files(sorted(p for p in (seed / "data").rglob("*") if p.is_file()), str(remote), "seed", {})
        try:
            yield str(remote)
        finally:
            ra.DATA_DIR, ra.MANIFEST = saved


def test_a_complete_yesterday_is_fine():
    with raw_repo() as remote:
        assert ci_deadman.check_raw(remote, TODAY) == []


def test_every_missing_file_is_named():
    with raw_repo(semo=False, eirgrid=False) as remote:
        assert ci_deadman.check_raw(remote, TODAY) == [f"the raw repo has no {k} file for {YESTERDAY}" for k in ("semo", "wind", "demand")]
    with raw_repo(semo=False) as remote:
        assert ci_deadman.check_raw(remote, TODAY) == [f"the raw repo has no semo file for {YESTERDAY}"]


def test_an_incomplete_eirgrid_file_is_a_problem_too():
    with raw_repo(demand_quarters=60) as remote:
        assert ci_deadman.check_raw(remote, TODAY) == [f"the raw repo's demand file for {YESTERDAY} holds 30/48 half-hours"]


def test_last_sunday_from_any_weekday():
    assert ci_deadman.last_sunday(date(2026, 11, 10)) == date(2026, 11, 8)      # Tuesday
    assert ci_deadman.last_sunday(date(2026, 11, 9)) == date(2026, 11, 8)       # Monday
    assert ci_deadman.last_sunday(date(2026, 11, 8)) == date(2026, 11, 1)       # a Sunday: that week is not over


def test_weekly_post_on_master_or_in_an_open_pr_or_neither():
    with tempfile.TemporaryDirectory() as t:
        content = Path(t) / "site" / "content"
        asked = []
        no_pr = lambda b: asked.append(b) or False
        problems = ci_deadman.check_weekly(TODAY, content, no_pr)
        assert asked == ["weekly/2026-11-08"] and len(problems) == 1, problems
        assert "no weekly post for the week ending 2026-11-08" in problems[0] and "weekly/2026-11-08 has no open pull request" in problems[0]
        assert ci_deadman.check_weekly(TODAY, content, lambda b: b == "weekly/2026-11-08") == []
        post = content / "weekly" / "2026-11-08" / "index.md"
        post.parent.mkdir(parents=True)
        post.write_text("---\n---\n")
        asked.clear()
        assert ci_deadman.check_weekly(TODAY, content, no_pr) == [] and asked == []      # on master: no PR lookup needed


def test_the_workflow_is_daily_at_12_and_checks_the_week_on_tuesdays():
    text = (Path(__file__).parent.parent / ".github" / "workflows" / "deadman.yml").read_text()
    assert text.count("- cron:") == 1 and '- cron: "0 12 * * *"' in text
    assert '[ "$(date -u +%u)" = "2" ]' in text and "--weekly" in text and "python pipeline/ci_deadman.py" in text
    assert "contents: read" in text and "pull-requests: read" in text and "git push" not in text
    assert "site/content/daily" not in text                                           # the daily posts are no longer CI's


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
