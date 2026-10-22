#!/usr/bin/env python3
"""
ci_daily.py — one unattended daily run, for GitHub Actions (.github/workflows/daily.yml).

    python pipeline/ci_daily.py                  # yesterday's delivery date, Irish calendar
    python pipeline/ci_daily.py --date 2026-09-08

1. If site/content/daily/<date>/index.md is already in the checkout, stop: exit 0, no network, no
   changes. This is what makes the evening retry a no-op after a morning success.
2. data/ is gitignored, so a runner has no history. Fetch the 6 days before the target from SEMOpx
   (the 7-day week-compare chart needs them; a missing one is a failure, not a quietly shorter chart)
   and the previous day's EirGrid archive (a missing one leaves two half-hours NaN, as by design).
3. Run run_daily.py --date <date> unchanged. Its stale-data gate and fetch.py's fail-closed paths
   are not touched; a nonzero exit fails this script.
4. Merge the new raw-file checksums into pipeline/data-manifest.sha256 (see update_manifest.py).

Prints STATUS=noop|generated and DATE=<date>, and appends both to $GITHUB_OUTPUT when set.
"""

import argparse
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_daily import CONTENT_DIR, DATA_DIR, default_delivery_date
from fetch import fetch_area, fetch_semo
from update_manifest import ManifestConflict, update_manifest

HISTORY_DAYS = 6  # chart_week_comparison: the target day plus the 6 before it


def emit(status: str, target: date):
    print(f"STATUS={status}\nDATE={target.isoformat()}")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"status={status}\ndate={target.isoformat()}\n")


def die(msg: str):
    print(f"::error::{msg}" if os.environ.get("GITHUB_ACTIONS") else f"ERROR: {msg}")
    sys.exit(1)


def semo_file(delivery: date) -> Path | None:
    stamp = (delivery - timedelta(days=1)).strftime("%Y%m%d")
    found = sorted(DATA_DIR.glob(f"MarketResult_SEM-DA_PWR-MRC-D+1_{stamp}*.csv"))
    return found[0] if found else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("--date", metavar="YYYY-MM-DD", help="Delivery date (default: yesterday, Irish calendar).")
    args = ap.parse_args()
    target = date.fromisoformat(args.date) if args.date else default_delivery_date()
    iso = target.isoformat()

    post = CONTENT_DIR / "daily" / iso / "index.md"
    if post.exists():
        print(f"{post.relative_to(CONTENT_DIR.parent.parent)} already exists; nothing to do.")
        emit("noop", target)
        return

    history = [target - timedelta(days=k) for k in range(HISTORY_DAYS, 0, -1)]
    for d in history:
        try:
            fetch_semo(delivery_date=d, out_dir=DATA_DIR)
        except Exception as e:
            die(f"cannot fetch SEMOpx history for {d.isoformat()} ({type(e).__name__}: {e}); "
                f"the week-compare chart for {iso} would be wrong, so not generating it")
    for area in ("wind", "demand"):
        if fetch_area(target - timedelta(days=1), area, out_dir=DATA_DIR, overwrite_raw=False) is None:
            print(f"::warning::no EirGrid {area} archive for {(target - timedelta(days=1)).isoformat()}; "
                  f"its evening half-hours stay NaN in the {iso} post")

    env = {**os.environ, "CI": "1"}
    proc = subprocess.Popen([sys.executable, str(Path(__file__).parent / "run_daily.py"), "--date", iso],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    for line in proc.stdout:
        print(line, end="")
        if line.lstrip().startswith("– EirGrid"):
            print(f"::warning::{iso}: {line.strip()}")
    if proc.wait() != 0:
        die(f"run_daily.py --date {iso} exited {proc.returncode}")
    if not post.exists():
        die(f"run_daily.py exited 0 but {post} was not written")

    raw = [f for f in (semo_file(d) for d in history + [target]) if f]
    raw += [DATA_DIR / "eirgrid_raw" / iso / f"{a}.json" for a in ("wind", "demand")]
    try:
        added = update_manifest(raw)
    except ManifestConflict as e:
        die(str(e))
    print(f"manifest: {len(added)} entries added")
    emit("generated", target)


if __name__ == "__main__":
    main()
