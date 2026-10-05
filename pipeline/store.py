"""
store.py — Backfill a SQLite historical store from data/ and live EirGrid re-fetch.

Two tables:
    market_prices(date, period, start_time, dam_price_eur_mwh)
    system_conditions(date, period, start_time, wind_mw, wind_forecast_mw, demand_mw, wind_pct)

Design notes:
  - market_prices is built by replaying every SEMO CSV in data/ through
    process.load_dam_data() — the existing, unmodified parser.
  - system_conditions is built archive first: each area is parsed from
    data/eirgrid_raw/<date>/<area>.json with the same parser the live fetch
    uses, so the store holds exactly what published posts were written from.
    Only an area whose archive is missing or has zero rows is fetched live,
    and that fetch fills the gap in data/eirgrid_raw/ without ever replacing
    an archive that has rows.
  - system_conditions is expected to be sparse only in the sense that a date can
    be entirely ABSENT (EirGrid fetch failed). Missing days must never appear as
    zero-valued rows — a rolling baseline computed over silent zeros would read
    a fetch failure as "no wind that day," which is a different and false claim.
  - Idempotent: both tables are keyed on (date, period) with INSERT OR REPLACE,
    so re-running the backfill (or a daily incremental run) never duplicates rows.
"""

import sqlite3
import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from process import load_dam_data
from fetch import (
    AREA_FIELDS, archive_path, archive_row_count, combine_wind_and_demand,
    fetch_area, load_archived_area,
)

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = Path(__file__).parent.parent / "data" / "history.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS market_prices (
    date TEXT NOT NULL,
    period INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    dam_price_eur_mwh REAL NOT NULL,
    PRIMARY KEY (date, period)
);

CREATE TABLE IF NOT EXISTS system_conditions (
    date TEXT NOT NULL,
    period INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    wind_mw REAL,
    wind_forecast_mw REAL,
    demand_mw REAL,
    wind_pct REAL,
    PRIMARY KEY (date, period)
);
"""


def build_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    return conn


def upsert_market_prices(conn: sqlite3.Connection, df) -> int:
    """Upsert a load_dam_data() DataFrame into market_prices. Returns rows written.
    Does not commit."""
    records = [
        (
            row["DeliveryDate"].date().isoformat(),
            int(row["Period"]),
            row["StartTime"],
            float(row["DAMPrice_EUR_MWh"]),
        )
        for _, row in df.iterrows()
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO market_prices "
        "(date, period, start_time, dam_price_eur_mwh) VALUES (?, ?, ?, ?)",
        records,
    )
    return len(records)


def upsert_system_conditions(conn: sqlite3.Connection, d: date, df) -> int:
    """Upsert a fetch_wind_and_demand() DataFrame for date d into system_conditions.
    Returns rows written. Does not commit."""
    records = [
        (
            d.isoformat(),
            i + 1,  # period: 1..48, half-hourly, matches SEMO's Period numbering
            row["StartTime"].strftime("%H:%M"),
            float(row["WindMW"]) if pd_notna(row["WindMW"]) else None,
            float(row["WindForecastMW"]) if pd_notna(row.get("WindForecastMW")) else None,
            float(row["DemandMW"]) if pd_notna(row["DemandMW"]) else None,
            float(row["WindGeneration_pct"]) if pd_notna(row["WindGeneration_pct"]) else None,
        )
        for i, (_, row) in enumerate(df.sort_values("StartTime").iterrows())
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO system_conditions "
        "(date, period, start_time, wind_mw, wind_forecast_mw, demand_mw, wind_pct) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        records,
    )
    return len(records)


def persist_day(d: date, price_df, conditions_df=None, db_path: Path = DB_PATH) -> tuple[int, int]:
    """Incremental write for one delivery date, used by run_daily.

    Idempotent (same INSERT OR REPLACE keys as the backfill). conditions_df=None
    — an EirGrid fetch failure — writes no system_conditions rows at all, never
    zero-valued ones. Returns (price rows, condition rows).
    """
    conn = build_db(db_path)
    try:
        price_rows = upsert_market_prices(conn, price_df)
        cond_rows = 0
        if conditions_df is not None and not conditions_df.empty:
            cond_rows = upsert_system_conditions(conn, d, conditions_df)
        conn.commit()
    finally:
        conn.close()
    return price_rows, cond_rows


def backfill_market_prices(conn: sqlite3.Connection, data_dir: Path = DATA_DIR) -> int:
    """Replay every SEMO DAM CSV in data_dir. Returns rows written."""
    rows = 0
    for csv_path in sorted(data_dir.glob("MarketResult_SEM-DA_*.csv")):
        try:
            df = load_dam_data(csv_path)
        except ValueError as e:
            print(f"  [store] SKIP {csv_path.name}: {e}")
            continue
        rows += upsert_market_prices(conn, df)
    conn.commit()
    return rows


def backfill_system_conditions(
    conn: sqlite3.Connection, start: date, end: date, out_dir: Path = DATA_DIR,
    retries: int = 2, backoff: float = 2.0, dry_run: bool = False,
) -> tuple[int, list[str]]:
    """
    Fill system_conditions for every date in [start, end], archive first.

    Each area (wind, demand) is parsed from data/eirgrid_raw/<date>/<area>.json
    when that file holds at least one data row — no network call, and the
    values are exactly what the published post was written from. Only an area
    whose archive is missing or has zero rows is fetched live, with `retries`
    retries and exponential backoff (backoff, 2*backoff, ...). A live fetch
    never replaces an archive that has rows; a zero-row archive is overwritten.

    Commits after every date, so killing the run loses at most one day.
    Prints exactly one line per date: "<date> archive|api ok|FAIL rows=<n>"
    ("api" if any area needed the network). dry_run prints "<date> archive|api"
    and touches nothing.
    Returns (rows written, list of dates that failed).
    """
    import contextlib
    import io
    import time

    rows = 0
    failed = []
    d = start
    while d <= end:
        live = [a for a in AREA_FIELDS if archive_row_count(archive_path(d, a, out_dir)) == 0]
        source = "api" if live else "archive"
        if dry_run:
            print(f"{d.isoformat()} {source}")
            d += timedelta(days=1)
            continue

        # fetch.py prints its own diagnostics; keep the one-line-per-date contract.
        with contextlib.redirect_stdout(io.StringIO()):
            frames = {a: load_archived_area(d, a, out_dir) for a in AREA_FIELDS if a not in live}
            for area in AREA_FIELDS:
                if frames.get(area) is not None:
                    continue
                source = "api"
                for attempt in range(retries + 1):
                    frames[area] = fetch_area(d, area, out_dir=out_dir, overwrite_raw=False)
                    if frames[area] is not None or attempt == retries:
                        break
                    time.sleep(backoff * 2 ** attempt)
            df = combine_wind_and_demand(frames.get("wind"), frames.get("demand"))

        if df is None or df.empty:
            failed.append(d.isoformat())
            print(f"{d.isoformat()} {source} FAIL rows=0", flush=True)
        else:
            n = upsert_system_conditions(conn, d, df)
            conn.commit()
            rows += n
            print(f"{d.isoformat()} {source} ok rows={n}", flush=True)
        d += timedelta(days=1)

    return rows, failed


def pd_notna(value) -> bool:
    import pandas as pd
    return pd.notna(value)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backfill data/history.db system_conditions (archive first).")
    parser.add_argument("--start", metavar="YYYY-MM-DD", help="First date (default: first market_prices date).")
    parser.add_argument("--end", metavar="YYYY-MM-DD", help="Last date (default: last market_prices date).")
    parser.add_argument("--prices", action="store_true",
                        help="Also replay every SEMO CSV in data/ into market_prices first.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print which source each date would use; no network, no DB writes.")
    args = parser.parse_args()

    # A dry run only reads the date range, so it never takes a write lock.
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) if args.dry_run else build_db()
    if args.prices and not args.dry_run:
        print(f"market_prices: {backfill_market_prices(conn)} rows", flush=True)

    # Default range follows what market_prices actually covers, not a hardcoded guess.
    lo, hi = conn.execute("SELECT MIN(date), MAX(date) FROM market_prices").fetchone()
    start = date.fromisoformat(args.start or lo)
    end = date.fromisoformat(args.end or hi)

    _, failed = backfill_system_conditions(conn, start, end, dry_run=args.dry_run)
    conn.close()
    sys.exit(1 if failed else 0)
