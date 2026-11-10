#!/usr/bin/env python3
"""
ci_archive.py — archive.yml's job: keep the private raw repo current. No post, no content commit.

    python pipeline/ci_archive.py                    # yesterday (Irish calendar) and the 14 days before it
    python pipeline/ci_archive.py --date 2026-11-09

1. Restore the window (the target day and the 14 before it) from the raw repo into data/: the archive is the
   source of truth, and a runner starts empty.
2. If every day in the window is complete (its SEMOpx file, and wind and demand with every half-hour the day can
   supply), stop: exit 0, no request is made. This is what makes the retry a no-op after a good first run.
3. Otherwise, newest first, fetch what a day lacks: its SEMOpx DA file (fetch.fetch_semo) and the EirGrid areas that
   are short (ci_daily.refresh_tail: empty areas are fetched, an incomplete unpinned archived file is replaced only
   by a complete response, one the manifest pins is never touched). Fetches retry as fetch.py does in CI.
   This is the heal pass: any of the last 14 days with an empty or short demand/wind file, or no file, is refetched.
4. Verify each file in the manifest's terms (raw_gap.verify: a pinned file must match its pin; a SEMOpx file must
   parse, with ROI-DA and NI-DA agreeing, and be that date's) and push them in one commit (raw_archive.push_files:
   an archived file is never replaced, except an incomplete unpinned EirGrid one by a complete one). A file with no
   half-hours is not pushed; a partial one is, if the archive has nothing, so a later run can complete it.
5. Exit 1 if the target day is still short (the retry, or a person, takes it from there). A short heal day is a
   warning: the feed is the cause, and the next run tries again.
"""

import argparse
import os
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ci_daily                                        # noqa: E402
import raw_archive as ra                               # noqa: E402
import raw_gap                                         # noqa: E402
from fetch import fetch_semo, path_halfhours           # noqa: E402
from trading_day import placeable_halfhours            # noqa: E402

HEAL_DAYS = 14


def window(target: date, heal_days: int = HEAL_DAYS) -> list[date]:
    return [target - timedelta(days=k) for k in range(heal_days, -1, -1)]          # oldest first, target last


def short(d: date) -> list[str]:
    """What data/ lacks for delivery date d, e.g. ['semo', 'demand 0/48']; [] when the day is complete."""
    out = []
    if raw_gap.local_path(d, "semo", ra.DATA_DIR) is None:
        out.append("semo")
    need = placeable_halfhours(d)
    for kind in ("wind", "demand"):
        have = path_halfhours(ra.DATA_DIR / "eirgrid_raw" / d.isoformat() / f"{kind}.json", kind)
        if have < need:
            out.append(f"{kind} {have}/{need}")
    return out


def restore(days: list[date], remote: str) -> int:
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t) / "raw"
        if not ra.clone(remote, tmp, sparse=ra.window_paths(days[0], days[-1])):
            print("raw repo is empty; nothing to restore")
            return 0
        files = [p for p in (tmp / "data").rglob("*") if p.is_file()] if (tmp / "data").exists() else []
        return ra.copy_new(tmp, files)


def note(msg: str) -> None:
    print(msg)
    out = os.environ.get("GITHUB_STEP_SUMMARY")
    if out:
        with open(out, "a") as f:
            f.write(msg + "\n")


def run(target: date, remote: str, heal_days: int = HEAL_DAYS) -> int:
    days = window(target, heal_days)
    n = restore(days, remote)
    print(f"restored {n} raw files for {days[0]}..{target}")
    todo = [d for d in reversed(days) if short(d)]                                   # target first, then newest heal day
    if not todo:
        note(f"archive: {days[0]}..{target} is complete; nothing to do")
        return 0
    for d in todo:
        print(f"{d}: short {', '.join(short(d))}")
    fetch_errors = {}
    for d in todo:
        if raw_gap.local_path(d, "semo", ra.DATA_DIR) is None:
            try:
                fetch_semo(delivery_date=d, out_dir=ra.DATA_DIR)
            except Exception as e:                                                   # noqa: BLE001 - reported, not hidden
                fetch_errors[d] = f"SEMOpx file: {type(e).__name__}: {e}"
        if any(not s.startswith("semo") for s in short(d)):
            ci_daily.refresh_tail(d)
    entries = ra.manifest_entries()
    items = [raw_gap.verify(d, k, ra.DATA_DIR, entries) for d in todo for k in raw_gap.KINDS]
    refused = [i for i in items if i.status == "refused"]
    if refused:
        for i in refused:
            print(f"::error::{i.d} {i.kind} refused: {i.note}")
        return 1
    pushable = [i for i in items if i.path and (i.status == "ok" or path_halfhours(i.path, i.kind) > 0)]
    if pushable:
        ra.push_files([i.path for i in pushable], remote, f"{target} (archive)", entries)
    for d in todo:
        left = short(d)
        if left:
            kind = "error" if d == target else "warning"
            why = f" ({fetch_errors[d]})" if d in fetch_errors else ""
            print(f"::{kind}::{d} is still short in the archive: {', '.join(left)}{why}")
    if short(target):
        note(f"archive: {target} is short: {', '.join(short(target))}")
        return 1
    note(f"archive: {target} complete; {len([d for d in todo if d != target])} earlier day(s) healed or still short")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("--date", metavar="YYYY-MM-DD", help="Delivery date (default: yesterday, Irish calendar).")
    ap.add_argument("--heal-days", type=int, default=HEAL_DAYS, help="Earlier days to check and heal (default 14).")
    ap.add_argument("--remote", help="Raw repo URL or path (default as raw_archive.py).")
    args = ap.parse_args()
    target = date.fromisoformat(args.date) if args.date else raw_gap.yesterday()
    return run(target, ra.remote_url(args.remote), args.heal_days)


if __name__ == "__main__":
    sys.exit(main())
