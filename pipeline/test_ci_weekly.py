"""ci_weekly.py (weekly.yml): the weekly draft built from the raw repo alone.
Run: python pipeline/test_ci_weekly.py   (temp directories and a local bare repo as the raw remote; any EirGrid or
SEMOpx request fails the test)"""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ci_weekly
import fetch
import raw_archive as ra
from test_raw_gap import put_eirgrid, put_semo

MONDAY = date(2026, 11, 2)
SUNDAY = MONDAY + timedelta(days=6)
FROM = MONDAY - timedelta(weeks=10)          # ten earlier weeks: more than the 8 a trailing verdict needs


@contextlib.contextmanager
def env(last_day_missing=False):
    saved = (ra.DATA_DIR, ra.MANIFEST, fetch.requests, os.environ.get("GITHUB_OUTPUT"))
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        e = type("Env", (), {})()
        e.tmp, e.content, e.charts, e.dest = tmp, tmp / "content", tmp / "charts", tmp / "store"
        e.remote = tmp / "raw.git"
        e.out = tmp / "github_output"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(e.remote)], check=True)
        ra.MANIFEST = tmp / "manifest.sha256"
        ra.MANIFEST.write_text("")
        seed = tmp / "seed"
        d = FROM
        while d <= SUNDAY:
            if not (last_day_missing and d == SUNDAY):
                put_semo(seed, d)
            d += timedelta(days=1)
        d = MONDAY - timedelta(days=1)
        while d <= SUNDAY:
            if not (last_day_missing and d == SUNDAY):
                put_eirgrid(seed, d)
            d += timedelta(days=1)
        ra.DATA_DIR = seed / "data"
        with contextlib.redirect_stdout(io.StringIO()):
            ra.push_files(sorted(p for p in (seed / "data").rglob("*") if p.is_file()), str(e.remote), "seed", {})

        def no_feed(*a, **k):
            raise AssertionError("a feed was contacted")
        fetch.requests = type("R", (), {"get": staticmethod(no_feed), "RequestException": Exception, "HTTPError": Exception})
        os.environ["GITHUB_OUTPUT"] = str(e.out)

        def run(final=False, on_origin=False):
            out, code = io.StringIO(), 0
            e.out.write_text("")
            with contextlib.redirect_stdout(out):
                code = ci_weekly.run(MONDAY, str(e.remote), e.dest, e.content, e.charts, final, history_from=FROM.isoformat(),
                                     exists_on_origin=lambda b: on_origin, out_dir=tmp)
            outputs = dict(l.split("=", 1) for l in e.out.read_text().splitlines())
            return code, out.getvalue(), outputs
        e.run = run
        e.post = e.content / "weekly" / SUNDAY.isoformat() / "index.md"
        try:
            yield e
        finally:
            ra.DATA_DIR, ra.MANIFEST, fetch.requests = saved[0], saved[1], saved[2]
            if saved[3] is None:
                os.environ.pop("GITHUB_OUTPUT", None)
            else:
                os.environ["GITHUB_OUTPUT"] = saved[3]


def test_builds_the_draft_and_chart_from_the_archive_without_contacting_a_feed():
    with env() as e:
        code, out, o = e.run()
        assert code == 0 and o["status"] == "built" and o["sunday"] == str(SUNDAY) and o["monday"] == str(MONDAY), (out, o)
        text = e.post.read_text()
        assert "draft: true" in text and f"week_start: {MONDAY}" in text and "<!--" in text      # placeholder Commentary
        assert (e.charts / "weekly" / f"{MONDAY}.png").stat().st_size > 10_000
        assert not (e.dest.parent / "site").exists()
        title = Path(o["title_file"]).read_text().strip()
        body = Path(o["body_file"]).read_text()
        assert title == "Weekly roundup draft: 2–8 November 2026", title
        assert "- [ ] Write the `## Commentary` section" in body and "- [ ] Set `draft: false`" in body and "audit-weekly" in body


def test_exits_0_when_the_post_is_already_on_the_default_branch():
    with env() as e:
        e.post.parent.mkdir(parents=True)
        e.post.write_text("---\ntitle: x\n---\n")
        saved, ra.cmd_materialise = ra.cmd_materialise, lambda a: (_ for _ in ()).throw(AssertionError("materialised"))
        try:
            code, out, o = e.run(final=True)
        finally:
            ra.cmd_materialise = saved
        assert code == 0 and o["status"] == "noop" and "nothing to do" in out and not e.charts.exists(), out


def test_an_existing_branch_is_left_for_the_pr_step():
    with env() as e:
        code, out, o = e.run(on_origin=True)
        assert code == 0 and o["status"] == "branch" and not e.post.exists() and not e.dest.exists(), (out, o)


def test_a_missing_last_day_waits_on_the_first_attempt_and_fails_the_retry():
    with env(last_day_missing=True) as e:
        code, out, o = e.run(final=False)
        assert code == 0 and o["status"] == "waiting" and f"::warning::the week of {MONDAY} is not complete" in out, out
        assert f"{SUNDAY} prices 0/48" in out and not e.post.exists()
        import shutil
        shutil.rmtree(e.dest)                                                  # the retry runs on a fresh runner
        code, out, o = e.run(final=True)
        assert code == 1 and "::error::" in out and "this was the last attempt" in out and not o and not e.post.exists(), (out, o)


def test_the_workflow_runs_monday_at_08_and_11_and_only_opens_a_pr():
    text = (Path(__file__).parent.parent / ".github" / "workflows" / "weekly.yml").read_text()
    assert '- cron: "0 8 * * 1"' in text and '- cron: "0 11 * * 1"' in text
    assert "python pipeline/ci_weekly.py" in text and "scripts/ci_weekly_pr.sh" in text
    assert "FINAL: ${{ github.event.schedule != '0 8 * * 1' }}" in text          # the retry and manual runs are final
    assert "contents: write" in text and "pull-requests: write" in text and "git push origin HEAD:master" not in text


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
