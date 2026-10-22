"""
weekly.py — Build the weekly-post draft: weekly_summary -> weekly_chart -> build_weekly_post.

Everything comes from data/history.db (prices and wind MW). Building is read-only; it makes
no EirGrid or SEMOpx request of its own. The post is written with draft: true and needs a human read.

Before it builds, main() checks the week for gaps (a day without all its prices, or a day with too
little demand for a wind % to be published) and, if there are any, asks for the store to be brought
current (scripts/nightly.sh, which takes the lock, backs the store up and keeps it read-only
afterwards), at most REFRESH_ATTEMPTS times, then re-checks. That is a catch-up of the same store the
nightly job maintains, with the same fail-closed fetchers (raw EirGrid archives with rows are never
replaced). The completeness check below is unchanged: a week whose final day is still short is refused.

A week is Monday to Sunday of delivery dates. The script refuses to build a week whose
final day is not in the store, and weekly_summary() raises if any other day is missing
or short, so a partial week is never summarised.

Usage:
    python pipeline/weekly.py                   # the last complete Mon-Sun (Irish calendar)
    python pipeline/weekly.py 2026-09-30         # the week containing this date
    python pipeline/weekly.py --force            # overwrite an existing draft
"""

import argparse
import os
import sqlite3
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import store
from charts import CHART_DIR, weekly_chart
from scaffold import CONTENT_DIR, build_weekly_post
from process import min_wind_rows
from trading_day import expected_periods
from weekly_stats import weekly_summary


def iso_week_bounds(d: date) -> tuple[date, date]:
    """Return (Monday, Sunday) of the ISO week containing d."""
    monday = d - timedelta(days=d.weekday())
    return monday, monday + timedelta(days=6)


def last_complete_week(now: datetime | None = None) -> date:
    """Monday of the most recent Mon-Sun week that has fully ended, by the Irish calendar.
    On a Sunday that week is the previous one: the Sunday itself has not finished."""
    today = (now or datetime.now(ZoneInfo("Europe/Dublin"))).date()
    last_sunday = today - timedelta(days=(today.weekday() + 1) % 7 or 7)
    return last_sunday - timedelta(days=6)


REFRESH_ATTEMPTS = 3
REFRESH_WAIT_S = 120      # EirGrid's demand feed flips empty/non-empty within minutes; retries seconds apart don't help
NIGHTLY = Path(__file__).parent.parent / "scripts" / "nightly.sh"


def week_gaps(db: Path, monday: date) -> list[str]:
    """Days of the week starting `monday` that are not publishable as they stand: fewer prices than
    expected, or fewer non-NULL wind_pct rows than a daily post needs (process.min_wind_rows)."""
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        gaps = []
        for i in range(7):
            d = monday + timedelta(days=i)
            ds = d.isoformat()
            prices = conn.execute("SELECT COUNT(*) FROM market_prices WHERE date=?", (ds,)).fetchone()[0]
            wind = conn.execute("SELECT COUNT(*) FROM system_conditions WHERE date=? AND wind_pct IS NOT NULL",
                                (ds,)).fetchone()[0]
            if prices != expected_periods(d):
                gaps.append(f"{ds} prices {prices}/{expected_periods(d)}")
            elif wind < min_wind_rows(d):
                gaps.append(f"{ds} demand {wind}/{min_wind_rows(d)} rows needed")
        return gaps
    finally:
        conn.close()


def refresh_store(db: Path) -> int:
    """Bring the store current through the guarded nightly path. Returns its exit code."""
    env = {**os.environ, "HISTORY_DB": str(db)}
    return subprocess.run(["bash", str(NIGHTLY)], env=env).returncode


def ensure_week_current(db: Path, monday: date, refresh=refresh_store, attempts: int = REFRESH_ATTEMPTS,
                        wait_s: float = REFRESH_WAIT_S) -> list[str]:
    """Re-check the week and, while it has gaps, refresh the store (at most `attempts` times, wait_s
    apart). Returns the gaps still present. Never alters the completeness check that follows."""
    gaps = week_gaps(db, monday)
    for n in range(1, attempts + 1):
        if not gaps:
            break
        print(f"weekly: gaps in the week of {monday}: {'; '.join(gaps)}; refreshing the store "
              f"({n}/{attempts})", file=sys.stderr)
        rc = refresh(db)
        print(f"weekly: refresh exit {rc}", file=sys.stderr)
        gaps = week_gaps(db, monday)
        if gaps and n < attempts:
            time.sleep(wait_s)
    return gaps


def build_weekly_draft(any_date_in_week: date, db_path: Path | None = None, content_root: Path | None = None,
                       chart_dir: Path | None = None, force: bool = False) -> Path:
    """Summarise, chart and scaffold the week containing any_date_in_week. Returns the post path.

    Raises ValueError if the store lacks the week's final day (or any other day), and
    FileExistsError if the post exists and force is False (before anything is written)."""
    monday, sunday = iso_week_bounds(any_date_in_week)
    post = Path(content_root or CONTENT_DIR) / "weekly" / sunday.isoformat() / "index.md"
    if post.exists() and not force:
        raise FileExistsError(f"{post} exists; use --force to overwrite")

    db = Path(db_path) if db_path else store.DB_PATH          # resolved at call time
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        have = conn.execute("SELECT COUNT(*) FROM market_prices WHERE date=?", (sunday.isoformat(),)).fetchone()[0]
        if have != expected_periods(sunday):
            raise ValueError(f"store lacks the week's final day {sunday} ({have} of {expected_periods(sunday)} "
                             f"periods); run the daily pipeline or --backfill-prices first")
        summary = weekly_summary(monday, conn)
    finally:
        conn.close()

    weekly_chart(summary, Path(chart_dir or CHART_DIR) / "weekly" / f"{monday.isoformat()}.png")
    return build_weekly_post(summary, content_root, force=force)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build the weekly post draft from data/history.db.")
    parser.add_argument("date", nargs="?", metavar="YYYY-MM-DD",
                        help="Any date in the week to build (default: the last complete Mon-Sun).")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing draft and chart.")
    parser.add_argument("--db", type=Path, help="History database (default: data/history.db).")
    parser.add_argument("--content-root", type=Path, help="Content tree to write into (default: site/content).")
    parser.add_argument("--chart-dir", type=Path, help="Chart root (default: site/static/charts).")
    args = parser.parse_args(argv)
    target = date.fromisoformat(args.date) if args.date else last_complete_week()
    monday = iso_week_bounds(target)[0]
    post = Path(args.content_root or CONTENT_DIR) / "weekly" / iso_week_bounds(target)[1].isoformat() / "index.md"
    # Refresh only the real store, and only when a post is going to be built. A --db override is a test
    # or a copy; nightly.sh would back up and rewrite the real one.
    if args.db is None and Path(store.DB_PATH).exists() and (args.force or not post.exists()):
        remaining = ensure_week_current(Path(store.DB_PATH), monday)
        if remaining:
            print(f"weekly: gaps remain after refreshing: {'; '.join(remaining)}", file=sys.stderr)
    try:
        post = build_weekly_draft(target, args.db, args.content_root, args.chart_dir, args.force)
    except (ValueError, FileExistsError) as e:
        print(f"weekly: {e}", file=sys.stderr)
        return 1
    print(f"Weekly draft: {post}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
