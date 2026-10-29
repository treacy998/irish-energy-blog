#!/usr/bin/env python3
"""
ci_audit.py — the audit gate between "generated" and "published" in .github/workflows/daily.yml.

    python pipeline/ci_audit.py --date 2026-10-28 --dest "$RUNNER_TEMP/audit-store"

1. raw_archive.py materialise: restore the archived raw for the 14 days before the target day and the target
   day itself from the raw repo into a fresh --dest, check every restored file against pipeline/data-manifest.sha256,
   and build a throwaway history.db from it. The store the audit uses is therefore built from the archived bytes,
   not from anything the generating step left in the checkout, and the target day's raw must already be in the
   archive (the job pushes raw first, content second, and runs this between them).
2. audit_posts.py --store <that db> --only <date>: recompute the day's figures from it and compare every figure
   in the new post. Any flagged row that is not in pipeline/audit/audit_known.csv fails the run, and so does a
   post with no ground truth (an unaudited post is not a clean one).

A nonzero exit stops the job before the commit/push step. Nothing is written into the checkout; the CSV
report goes under --dest. Offline apart from the clone of the raw repo.
"""

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "audit"))
import raw_archive
import audit_posts

HISTORY_DAYS = 14   # trailing days restored with the target day


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("--date", required=True, metavar="YYYY-MM-DD", help="Delivery date of the post to audit.")
    ap.add_argument("--dest", required=True, metavar="DIR", help="A new, empty directory for the throwaway store.")
    ap.add_argument("--days", type=int, default=HISTORY_DAYS, help="Trailing days to restore (default 14).")
    ap.add_argument("--remote", help="Raw repo URL or path (default as raw_archive.py).")
    args = ap.parse_args(argv)
    target = date.fromisoformat(args.date)
    dest = Path(args.dest)

    raw_archive.cmd_materialise(argparse.Namespace(
        start=(target - timedelta(days=args.days)).isoformat(), to=target.isoformat(), dest=str(dest),
        remote=raw_archive.remote_url(args.remote)))
    try:
        audit_posts.main(["--store", str(dest / "history.db"), "--only", target.isoformat(),
                          "--report", str(dest / "audit_report.csv")])
    except SystemExit as e:
        if e.code:
            note = f"audit gate FAILED for {target}: the post is not published"
            print(f"::error::{note}" if os.environ.get("GITHUB_ACTIONS") else f"ERROR: {note}")
            summary_line(f"**Audit gate: {target} FAILED.** Nothing was committed. See the job log.")
        raise
    summary_line(f"Audit gate: {target} clean against the raw archive ({args.days} trailing days restored, manifest verified).")


def summary_line(text: str):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as f:
            f.write(f"\n{text}\n")


if __name__ == "__main__":
    main()
