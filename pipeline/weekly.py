"""
weekly.py — Build the weekly-post draft: weekly_summary -> weekly_chart -> build_weekly_post.

Everything comes from data/history.db (prices and wind MW), read-only. There is no
EirGrid or SEMOpx request here, so no raw archive under data/ can be fetched over or
replaced by this script. The post is written with draft: true and needs a human read.

A week is Monday to Sunday of delivery dates. The script refuses to build a week whose
final day is not in the store, and weekly_summary() raises if any other day is missing
or short, so a partial week is never summarised.

Usage:
    python pipeline/weekly.py                   # the last complete Mon-Sun (Irish calendar)
    python pipeline/weekly.py 2026-09-30         # the week containing this date
    python pipeline/weekly.py --force            # overwrite an existing draft
"""

import argparse
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import store
from charts import CHART_DIR, weekly_chart
from scaffold import CONTENT_DIR, build_weekly_post
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


def build_weekly_draft(any_date_in_week: date, db_path: Path | None = None, content_root: Path | None = None,
                       chart_dir: Path | None = None, force: bool = False) -> Path:
    """Summarise, chart and scaffold the week containing any_date_in_week. Returns the post path.

    Raises ValueError if the store lacks the week's final day (or any other day), and
    FileExistsError if the post exists and force is False (before anything is written)."""
    monday, sunday = iso_week_bounds(any_date_in_week)
    post = Path(content_root or CONTENT_DIR) / "weekly" / monday.isoformat() / "index.md"
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
    try:
        post = build_weekly_draft(target, args.db, args.content_root, args.chart_dir, args.force)
    except (ValueError, FileExistsError) as e:
        print(f"weekly: {e}", file=sys.stderr)
        return 1
    print(f"Weekly draft: {post}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
