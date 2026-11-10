#!/usr/bin/env python3
"""
ci_weekly.py — weekly.yml's build step: the weekly draft, built from the raw repo and nothing else.

    python pipeline/ci_weekly.py [--week-start YYYY-MM-DD] [--final]

The week is the last complete Mon-Sun by the Irish calendar unless --week-start (a Monday) says otherwise.

1. If site/content/weekly/<sunday>/index.md is already in the checkout (master), stop: STATUS=noop.
2. If the branch weekly/<sunday> already exists on origin, stop: STATUS=branch (the PR step makes sure it has a PR).
3. Materialise a throwaway store from the raw repo into $RUNNER_TEMP (raw_archive.materialise: every restored file is
   checked against the manifest). Nothing else is read and no feed is contacted: weekly.py runs on that store with
   --db, so it never refreshes or fetches.
4. Check the week for gaps (weekly.week_gaps: a day short of prices, or of the demand a wind % needs). With gaps:
   without --final (the first attempt) STATUS=waiting, exit 0, a warning; with --final (the retry) exit 1.
5. Build the draft and chart (weekly.build_weekly_draft), and write the PR title and body. STATUS=built.

Prints STATUS=, MONDAY=, SUNDAY=, TITLE_FILE=, BODY_FILE=, and appends them to $GITHUB_OUTPUT when set.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import raw_archive as ra                               # noqa: E402
import weekly                                          # noqa: E402

FIRST_PRICE_DAY = "2025-10-07"        # the first delivery date the archive holds prices for; the baselines need all of it


def emit(**kv) -> None:
    for k, v in kv.items():
        print(f"{k.upper()}={v}")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.writelines(f"{k}={v}\n" for k, v in kv.items())


def branch_exists(branch: str) -> bool:
    r = subprocess.run(["git", "ls-remote", "--exit-code", "--heads", "origin", branch], capture_output=True, text=True)
    return r.returncode == 0


def front(post: Path, key: str) -> str:
    m = re.search(rf"^{key}:\s*\"?(.*?)\"?\s*$", post.read_text(), re.M)
    return m.group(1) if m else ""


def pr_text(post: Path, monday: date, sunday: date) -> tuple[str, str]:
    title = f"Weekly roundup draft: {front(post, 'title').removeprefix('Weekly Analysis — ')}"
    body = "\n".join([
        f"Draft weekly post for {monday} to {sunday}, built from the raw repo by `weekly.yml` (`pipeline/ci_weekly.py`).",
        "", f"> {front(post, 'summary')}", "",
        "Before merging:",
        "- [ ] Write the `## Commentary` section (it is still the scaffold placeholder).",
        "- [ ] Set `draft: false` in the front matter.",
        "- [ ] Read the chart (`site/static/charts/weekly/" + f"{monday}.png`) and the tables against the week.",
        "",
        "`audit-weekly` checks every published post against the raw archive on Monday 09:30 UTC, after this merges.",
    ]) + "\n"
    return title, body


def run(monday: date, remote: str, dest: Path, content_root: Path, chart_dir: Path, final: bool,
        history_from: str = FIRST_PRICE_DAY, exists_on_origin=branch_exists, out_dir: Path | None = None) -> int:
    sunday = monday + timedelta(days=6)
    post = content_root / "weekly" / sunday.isoformat() / "index.md"
    if post.exists():
        print(f"{post} is already on the default branch; nothing to do.")
        emit(status="noop", monday=monday, sunday=sunday)
        return 0
    if exists_on_origin(f"weekly/{sunday}"):
        print(f"branch weekly/{sunday} already exists; nothing to build.")
        emit(status="branch", monday=monday, sunday=sunday)
        return 0
    built = ra.cmd_materialise(argparse.Namespace(start=history_from, to=sunday.isoformat(), dest=str(dest), remote=remote))
    if built and built["market_splits"]:                      # a split day is missing from every baseline: never "waiting"
        for e in built["market_splits"]:
            print(f"::error::MARKET SPLIT {e.delivery_date}: periods {', '.join(str(p) for p in e.periods)}; {e}")
        return 1
    db = dest / "history.db"
    gaps = weekly.week_gaps(db, monday)
    if gaps:
        msg = f"the week of {monday} is not complete in the raw archive: {'; '.join(gaps)}"
        if final:
            print(f"::error::{msg}; this was the last attempt")
            return 1
        print(f"::warning::{msg}; the retry will try again")
        emit(status="waiting", monday=monday, sunday=sunday)
        return 0
    built = weekly.build_weekly_draft(monday, db, content_root, chart_dir)
    out = out_dir or Path(os.environ.get("RUNNER_TEMP") or tempfile.gettempdir())
    title, body = pr_text(built, monday, sunday)
    (out / "pr-title.txt").write_text(title + "\n")
    (out / "pr-body.md").write_text(body)
    print(f"built {built}")
    emit(status="built", monday=monday, sunday=sunday, title_file=out / "pr-title.txt", body_file=out / "pr-body.md")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("--week-start", metavar="YYYY-MM-DD", help="A Monday (default: the last complete week).")
    ap.add_argument("--final", action="store_true", help="This is the last attempt: an incomplete week fails the run.")
    ap.add_argument("--remote", help="Raw repo URL or path (default as raw_archive.py).")
    ap.add_argument("--dest", type=Path, help="Fresh directory for the throwaway store (default $RUNNER_TEMP/weekly-store).")
    args = ap.parse_args()
    monday = date.fromisoformat(args.week_start) if args.week_start else weekly.last_complete_week()
    if monday.weekday() != 0:
        raise SystemExit(f"{monday} is not a Monday")
    dest = args.dest or Path(os.environ.get("RUNNER_TEMP") or tempfile.gettempdir()) / "weekly-store"
    return run(monday, ra.remote_url(args.remote), dest, weekly.CONTENT_DIR, weekly.CHART_DIR, args.final)


if __name__ == "__main__":
    sys.exit(main())
