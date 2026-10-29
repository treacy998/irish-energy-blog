#!/usr/bin/env python3
"""
ci_daily.py — one unattended daily run, for GitHub Actions (.github/workflows/daily.yml).

    python pipeline/ci_daily.py                  # yesterday's delivery date, Irish calendar
    python pipeline/ci_daily.py --date 2026-09-08

1. If site/content/daily/<date>/index.md is already in the checkout, stop: exit 0, no network, no
   changes. This is what makes the evening retry a no-op after a morning success.
2. data/ is gitignored, so a runner has no history. With --restore-raw, take the 6 days before the target
   and the previous day's EirGrid archive from the raw repo (pipeline/raw_archive.py), which is the
   source of truth for published figures; a failure there fails the run. The target day's own raw files
   are restored too if the archive holds them (an earlier run archived them, then died before the content
   push): the post is then generated from those bytes and nothing is fetched afresh for the day, so the
   later raw push cannot see a differing hash. Only an area with nothing archived is fetched. Whatever is
   still missing is fetched from SEMOpx
   (the 7-day week-compare chart needs them; a missing one is a failure, not a quietly shorter chart)
   and the previous day's EirGrid archive (a missing one leaves two half-hours NaN, as by design; refresh_tail
   says which areas are refetched, and when an incomplete archived file may be superseded). Live
   EirGrid fetches, this one and run_daily's for the target day, retry while an area has fewer non-null
   half-hours than the day can supply: up to 10 attempts about 60-90 s apart (fetch.py: EIRGRID_ATTEMPTS,
   EIRGRID_RETRY_MIN_S/MAX_S, EIRGRID_READ_TIMEOUT_S), each attempt logged and tabled in $GITHUB_STEP_SUMMARY.
3. Run run_daily.py --date <date> unchanged. Its stale-data gate and fetch.py's fail-closed paths
   are not touched; a nonzero exit fails this script.
4. Unless --allow-no-wind, fail if the post came out without wind figures (EirGrid's demand feed is
   intermittently empty; run_daily carries on without wind, which leaves a one-hour wind stub on the
   Price vs Wind chart). The new post and charts are removed so a retry can try again.
5. Merge the new raw-file checksums into pipeline/data-manifest.sha256 (see update_manifest.py).

Prints STATUS=noop|generated and DATE=<date>, and appends both to $GITHUB_OUTPUT when set.
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_daily import CONTENT_DIR, DATA_DIR, default_delivery_date
from fetch import archive_path, archive_row_count, archived_halfhours, configured_attempts, fetch_areas, fetch_semo
from trading_day import placeable_halfhours
import raw_archive
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


def refresh_tail(prev: date) -> list[Path]:
    """The previous day's EirGrid archive supplies the target day's first two half-hours; fetch what it lacks.

    Per area, by what is archived for `prev` (HALF = non-null half-hours, NEED = placeable_halfhours(prev)):
      complete (HALF >= NEED)               no request.
      nothing archived (zero rows)          fetched, retried (fetch.py), written if it has rows.
      incomplete and pinned by the manifest no request: it backs a published post and is never replaced.
      incomplete and not pinned             not evidence (raw_archive.may_supersede, PR #2): fetched with retries,
                                            and the archived file is replaced only by a COMPLETE response; a response
                                            that is no better leaves the archived bytes in place.
    "Pinned" means the manifest has any entry for the file. Returns the superseded files: main() adds them to this
    run's manifest update, so the raw push (which replaces an incomplete, unpinned archived copy once, logging both
    hashes) archives the bytes the post was built from; without that the post would rest on an unarchived file."""
    need = placeable_halfhours(prev)
    pinned = raw_archive.manifest_entries()
    fetch_now, replaceable = [], {}
    for area in ("wind", "demand"):
        path = archive_path(prev, area, DATA_DIR)
        have = archived_halfhours(prev, area, DATA_DIR)
        rel = f"data/eirgrid_raw/{prev.isoformat()}/{area}.json"
        if have >= need:
            continue
        if archive_row_count(path) == 0:
            fetch_now.append(area)
        elif rel in pinned:
            print(f"  [tail] {rel} holds {have}/{need} half-hours but the manifest pins it; not refetched")
        else:
            print(f"  [tail] {rel} holds {have}/{need} half-hours and is not pinned by the manifest: "
                  f"treating it as absent and fetching live")
            replaceable[area] = (have, path.read_bytes())
            path.unlink()                    # fetch_areas(overwrite_raw=False) writes only into an empty slot
            fetch_now.append(area)
    if fetch_now:
        fetch_areas(prev, fetch_now, out_dir=DATA_DIR, overwrite_raw=False, attempts=configured_attempts(ci=True))
    superseded = []
    for area, (have, old) in replaceable.items():
        path = archive_path(prev, area, DATA_DIR)
        now = archived_halfhours(prev, area, DATA_DIR)
        rel = f"data/eirgrid_raw/{prev.isoformat()}/{area}.json"
        if now >= need:
            print(f"  [tail] superseded {rel}: {have}/{need} -> {now}/{need} half-hours; "
                  f"sha256 {hashlib.sha256(old).hexdigest()} -> {raw_archive.sha256(path)}")
            superseded.append(path)
        else:
            path.write_bytes(old)
            print(f"  [tail] live {area} for {prev.isoformat()} is no better ({now}/{need}); "
                  f"keeping the archived file ({have}/{need})")
    return superseded


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("--date", metavar="YYYY-MM-DD", help="Delivery date (default: yesterday, Irish calendar).")
    ap.add_argument("--restore-raw", action="store_true",
                    help="First restore the history this run needs from the raw repo (fails closed).")
    ap.add_argument("--allow-no-wind", action="store_true",
                    help="Publish even if EirGrid wind/demand is incomplete for the day.")
    args = ap.parse_args()
    target = date.fromisoformat(args.date) if args.date else default_delivery_date()
    iso = target.isoformat()

    post = CONTENT_DIR / "daily" / iso / "index.md"
    if post.exists():
        print(f"{post.relative_to(CONTENT_DIR.parent.parent)} already exists; nothing to do.")
        emit("noop", target)
        return

    if args.restore_raw:
        raw_archive.cmd_restore(argparse.Namespace(date=iso, remote=raw_archive.remote_url(None)))

    history = [target - timedelta(days=k) for k in range(HISTORY_DAYS, 0, -1)]
    for d in history:
        try:
            fetch_semo(delivery_date=d, out_dir=DATA_DIR)
        except Exception as e:
            die(f"cannot fetch SEMOpx history for {d.isoformat()} ({type(e).__name__}: {e}); "
                f"the week-compare chart for {iso} would be wrong, so not generating it")
    prev = target - timedelta(days=1)
    superseded = refresh_tail(prev)
    for area in ("wind", "demand"):
        if archive_row_count(archive_path(prev, area, DATA_DIR)) == 0:
            print(f"::warning::no EirGrid {area} archive for {prev.isoformat()}; "
                  f"its evening half-hours stay NaN in the {iso} post")

    charts_dir = Path(CONTENT_DIR.parent / "static" / "charts" / iso)
    charts_existed = charts_dir.exists()
    env = {**os.environ, "CI": "1"}
    proc = subprocess.Popen([sys.executable, str(Path(__file__).parent / "run_daily.py"), "--date", iso,
                             "--prefer-archived-raw"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    for line in proc.stdout:
        print(line, end="")
        if line.lstrip().startswith("– EirGrid"):
            print(f"::warning::{iso}: {line.strip()}")
    if proc.wait() != 0:
        die(f"run_daily.py --date {iso} exited {proc.returncode}")
    if not post.exists():
        die(f"run_daily.py exited 0 but {post} was not written")

    if not args.allow_no_wind and "Wind % of Demand" not in post.read_text():
        shutil.rmtree(post.parent)
        if not charts_existed:
            shutil.rmtree(charts_dir, ignore_errors=True)
        die(f"{iso}: the post has no wind figures (EirGrid wind/demand incomplete); nothing kept. "
            f"Retry later, or pass --allow-no-wind to publish it without")

    raw = [f for f in (semo_file(d) for d in history + [target]) if f]
    raw += [DATA_DIR / "eirgrid_raw" / iso / f"{a}.json" for a in ("wind", "demand")]
    raw += superseded            # a refreshed previous-day tail backs this post, so it is pinned and pushed with it
    try:
        added = update_manifest(raw)
    except ManifestConflict as e:
        die(str(e))
    print(f"manifest: {len(added)} entries added")
    emit("generated", target)


if __name__ == "__main__":
    main()
