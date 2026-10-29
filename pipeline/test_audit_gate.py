"""The audit gate and `raw_archive.py materialise`. Run: python pipeline/test_audit_gate.py
(temp directories and a local bare git repo standing in for the raw archive; no network: requests.get and any live fetch raise)

Real: raw_archive.cmd_seed / cmd_materialise (git), store's backfill functions, audit_posts, ci_audit.main.
Stubbed: only the SEMOpx CSV parser (store.load_dam_data returns the fixture prices for the file's date).

1. A correct post passes the gate.
2. A post with one wrong figure fails it, naming the figure, and the workflow runs the gate before "Commit and push"
   with nothing that could let the commit step run after a failure.
3. materialise refuses a restored file whose hash differs from the manifest, and a manifest-pinned file that is missing
   from the archive, before building anything; it refuses a non-empty destination.
4. materialise is offline: a date with no archived EirGrid raw is reported, never fetched.
5. The weekly audit mode (--allow-skips) reports a post with no archived ground truth and does not fail on it; without
   --allow-skips it does fail. --only and --report leave the other posts and the checkout alone.
6. The weekly workflow is scheduled after the deadman check and cannot hide a failure behind its summary."""

import argparse
import contextlib
import io
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "audit"))
import audit_posts
import ci_audit
import fetch
import process
import raw_archive
import store
from test_ci_retry import eirgrid_body
from test_store_only import price_df
from update_manifest import update_manifest

DAY = date(2026, 10, 5)
ISO = DAY.isoformat()
WORKFLOWS = HERE.parent / ".github" / "workflows"


def semo_name(trade: date) -> str:
    return f"MarketResult_SEM-DA_PWR-MRC-D+1_{trade:%Y%m%d}100000_{trade:%Y%m%d}105501.csv"


class Gate:
    pass


@contextlib.contextmanager
def gate_env(back: int = 20, skip_eirgrid_for=()):
    """A raw archive holding deliveries DAY-back..DAY (SEMOpx fixtures, complete EirGrid files), the manifest pinning
    all of it, and a content tree with one correct post for DAY."""
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        g = Gate()
        g.tmp, g.data, g.manifest, g.remote = tmp, tmp / "src" / "data", tmp / "manifest.sha256", tmp / "raw.git"
        g.content = tmp / "content"
        g.data.mkdir(parents=True)
        raw = []
        for k in range(back, -1, -1):
            d = DAY - timedelta(days=k)
            f = g.data / semo_name(d - timedelta(days=1))
            f.write_text(f"fixture {d}\n")
            raw.append(f)
        for k in range(back + 1, -1, -1):
            d = DAY - timedelta(days=k)
            if d in skip_eirgrid_for:
                continue
            for area in ("wind", "demand"):
                f = g.data / "eirgrid_raw" / d.isoformat() / f"{area}.json"
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(eirgrid_body(d.isoformat(), area, 100.0, 96))
                raw.append(f)
        g.manifest.write_text("")
        update_manifest(raw, g.manifest, tmp / "src")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(g.remote)], check=True)

        saved = {
            raw_archive: {n: getattr(raw_archive, n) for n in ("DATA_DIR", "MANIFEST")},
            store: {n: getattr(store, n) for n in ("load_dam_data", "fetch_area")},
            audit_posts: {n: getattr(audit_posts, n) for n in ("POSTS_DIR", "WEEKLY_DIR")},
            fetch: {"requests": fetch.requests},
        }
        env_saved = {k: os.environ.get(k) for k in ("RAW_ARCHIVE_REMOTE", "GITHUB_STEP_SUMMARY")}

        def dam(path):
            stamp = re.search(r"_(\d{8})100000_", path.name).group(1)
            return price_df(date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:])) + timedelta(days=1))

        def no_network(*a, **k):
            raise AssertionError("a live request was made")

        try:
            raw_archive.DATA_DIR, raw_archive.MANIFEST = g.data, g.manifest
            os.environ["RAW_ARCHIVE_REMOTE"] = str(g.remote)
            os.environ.pop("GITHUB_STEP_SUMMARY", None)
            with contextlib.redirect_stdout(io.StringIO()):
                raw_archive.cmd_seed(argparse.Namespace(remote=str(g.remote)))
            store.load_dam_data = dam
            store.fetch_area = no_network
            fetch.requests = type("R", (), {"get": staticmethod(no_network), "RequestException": Exception, "HTTPError": Exception})
            audit_posts.POSTS_DIR, audit_posts.WEEKLY_DIR = g.content / "daily", g.content / "weekly"

            def write_post(d: date = DAY, mean_shift: float = 0.0):
                s = process.daily_summary(price_df(d), d)
                post = g.content / "daily" / d.isoformat() / "index.md"
                post.parent.mkdir(parents=True, exist_ok=True)
                post.write_text(
                    f"---\ntitle: \"I-SEM Daily Briefing\"\ndate: {d}\n---\n\n"
                    f"{{{{< statbar mean=\"€{float(s['mean_price']) + mean_shift:.1f}\" peak=\"€{s['peak_price']}\" "
                    f"min=\"€{s['min_price']}\" spread=\"€{s['price_range']}\" >}}}}\n\n"
                    f"| Metric | Value |\n|---|---|\n"
                    f"| Mean DAM Price | €{float(s['mean_price']) + mean_shift:.1f}/MWh |\n"
                    f"| Peak Price | €{s['peak_price']}/MWh ({s['peak_time']}) |\n"
                    f"| Min Price | €{s['min_price']}/MWh ({s['min_time']}) |\n"
                    f"| Price Range | €{s['price_range']}/MWh |\n")
                return post

            g.write_post = write_post
            g.dest = lambda name="store": g.tmp / name
            yield g
        finally:
            for mod, names in saved.items():
                for n, v in names.items():
                    setattr(mod, n, v)
            for k, v in env_saved.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v


def run(fn, *a, **k):
    out, code = io.StringIO(), None
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            fn(*a, **k)
        except SystemExit as e:
            code = e.code if e.code is not None else 0
    return code, out.getvalue()


def test_a_correct_post_passes_the_gate():
    with gate_env() as g:
        g.write_post()
        summary = g.tmp / "summary.md"
        os.environ["GITHUB_STEP_SUMMARY"] = str(summary)
        code, out = run(ci_audit.main, ["--date", ISO, "--dest", str(g.dest())])
        assert code is None, (code, out)
        assert "materialised" in out and "Flagged rows: 0" in out and "checked 1 posts, skipped 0" in out, out
        assert (g.dest() / "history.db").exists() and (g.dest() / "audit_report.csv").exists()
        assert "clean against the raw archive" in summary.read_text()


def test_one_wrong_figure_fails_the_gate_and_the_workflow_runs_it_before_the_commit():
    with gate_env() as g:
        g.write_post(mean_shift=5.0)                      # statbar and table both say 5 more than the archive's prices
        os.environ["GITHUB_STEP_SUMMARY"] = str(g.tmp / "summary.md")
        code, out = run(ci_audit.main, ["--date", ISO, "--dest", str(g.dest())])
        assert code == 1, (code, out)
        assert "mean_price" in out and "(MISMATCH)" in out and "not in baseline: 2" in out, out
        assert "FAILED" in (g.tmp / "summary.md").read_text()
    # The job stops at the first failing step, so the gate must come before the commit step and nothing may let the
    # commit step run after a failure.
    text = (WORKFLOWS / "daily.yml").read_text()
    steps = re.split(r"\n      - ", text.split("    steps:\n", 1)[1])
    names = [re.search(r"name: (.+)", s).group(1) if re.search(r"name: (.+)", s) else s.split("\n")[0] for s in steps]
    i_raw = names.index("Archive the raw data")
    i_gate = names.index("Audit the new post against the raw archive")
    i_commit = names.index("Commit and push")
    assert i_raw < i_gate < i_commit, names
    for s in (steps[i_gate], steps[i_commit]):
        assert "continue-on-error" not in s and "always()" not in s and "failure()" not in s, s
    assert "ci_audit.py" in steps[i_gate] and "scripts/ci_publish.sh" in steps[i_commit]


def test_materialise_refuses_a_hash_mismatch_a_missing_pinned_file_and_a_used_destination():
    with gate_env() as g:
        ok_lines = g.manifest.read_text().splitlines()
        # 1. a manifest entry whose hash differs from the archived bytes
        target = next(l for l in ok_lines if "eirgrid_raw/2026-10-05/demand.json" in l)
        g.manifest.write_text("\n".join(("0" * 64 + target[64:]) if l == target else l for l in ok_lines) + "\n")
        code, out = run(raw_archive.cmd_materialise, argparse.Namespace(
            start=(DAY - timedelta(days=14)).isoformat(), to=ISO, dest=str(g.dest("a")), remote=str(g.remote)))
        assert code and "HASH MISMATCH data/eirgrid_raw/2026-10-05/demand.json" in out, (code, out)
        assert not (g.dest("a") / "history.db").exists(), "a store was built from files that failed verification"
        # 2. a pinned file for the range that the archive does not hold (same trade-date stamp as a real file, another name)
        gone = f"data/MarketResult_SEM-DA_PWR-MRC-D+1_{(DAY - timedelta(days=4)):%Y%m%d}100000_{(DAY - timedelta(days=4)):%Y%m%d}115959.csv"
        g.manifest.write_text("\n".join(ok_lines) + f"\n{'1' * 64}  {gone}\n")
        code, out = run(raw_archive.cmd_materialise, argparse.Namespace(
            start=(DAY - timedelta(days=14)).isoformat(), to=ISO, dest=str(g.dest("b")), remote=str(g.remote)))
        assert code and f"MISSING FROM ARCHIVE {gone}" in out, (code, out)
        assert not (g.dest("b") / "history.db").exists()
        # 3. a destination that already has something in it
        (g.dest("c")).mkdir()
        (g.dest("c") / "x").write_text("y")
        g.manifest.write_text("\n".join(ok_lines) + "\n")
        code, out = run(raw_archive.cmd_materialise, argparse.Namespace(
            start=ISO, to=ISO, dest=str(g.dest("c")), remote=str(g.remote)))
        assert code and "not empty" in str(code), (code, out)


def test_materialise_is_offline_and_reports_dates_with_no_archived_eirgrid_raw():
    gap = DAY - timedelta(days=9)
    with gate_env(skip_eirgrid_for=(gap,)) as g:
        # store.fetch_area and fetch.requests.get both raise if called (see gate_env): reaching the end proves no request
        code, out = run(raw_archive.cmd_materialise, argparse.Namespace(
            start=(DAY - timedelta(days=14)).isoformat(), to=ISO, dest=str(g.dest()), remote=str(g.remote)))
        assert code is None, (code, out)
        assert f"no archived EirGrid wind for 1 date(s) ({gap}..{gap})" in out, out
        db = sqlite3.connect(g.dest() / "history.db")
        assert db.execute("SELECT count(DISTINCT date) FROM market_prices").fetchone()[0] == 15
        assert db.execute("SELECT count(*) FROM system_conditions WHERE date=?", (gap.isoformat(),)).fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM system_conditions WHERE date=?", (ISO,)).fetchone()[0] == 48


def test_weekly_mode_reports_a_post_with_no_archived_ground_truth_without_failing_on_it():
    with gate_env() as g:
        g.write_post()
        old = date(2026, 5, 4)                              # before anything the archive holds
        g.write_post(old)
        code, out = run(raw_archive.cmd_materialise, argparse.Namespace(
            start=(DAY - timedelta(days=14)).isoformat(), to=ISO, dest=str(g.dest()), remote=str(g.remote)))
        assert code is None, out
        store_db = str(g.dest() / "history.db")
        report = str(g.tmp / "weekly.csv")
        code, out = run(audit_posts.main, ["--store", store_db, "--exact", "--allow-skips", "--report", report])
        assert code is None, (code, out)
        assert "SKIPPED 2026-05-04: no archived ground truth: no market_prices rows in history.db for this date" in out, out
        assert "checked 1 posts, skipped 1" in out and "Flagged rows: 0" in out
        code, out = run(audit_posts.main, ["--store", store_db, "--exact", "--report", report])     # without --allow-skips
        assert code == 1 and "skipped without ground truth" in out, (code, out)
        # --only audits that one post and not the other, and --report put the CSV where asked
        code, out = run(audit_posts.main, ["--store", store_db, "--only", ISO, "--report", report])
        assert code is None and "checked 1 posts, skipped 0" in out, (code, out)
        assert Path(report).exists()


def test_the_weekly_workflow_runs_after_the_deadman_and_cannot_hide_a_failure():
    weekly = (WORKFLOWS / "audit-weekly.yml").read_text()
    deadman = (WORKFLOWS / "deadman.yml").read_text()
    wk = re.search(r'cron: "(\d+) (\d+) \* \* (\d)"', weekly)
    dm = re.search(r'cron: "(\d+) (\d+) \* \* (\d)"', deadman)
    assert wk and dm and wk.group(3) == dm.group(3) == "1", (wk, dm)               # both on Monday
    assert (int(wk.group(2)), int(wk.group(1))) > (int(dm.group(2)), int(dm.group(1))), "audit must be after the deadman"
    assert "--allow-skips" in weekly and "--exact" in weekly and "--store" in weekly
    assert 'exit "$rc"' in weekly and "|| rc=$?" in weekly, "the job must exit with the audit's own status after the summary"
    assert "permissions:\n  contents: read" in weekly and "git push" not in weekly and "git commit" not in weekly


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
