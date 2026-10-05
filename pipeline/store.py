"""
store.py — Backfill a SQLite historical store from data/ and live EirGrid re-fetch.

Two tables:
    market_prices(date, period, start_time, dam_price_eur_mwh)
    system_conditions(date, period, start_time, wind_mw, wind_forecast_mw, demand_mw, wind_pct)

Design notes:
  - market_prices is built by replaying every SEMO CSV in data/ through
    process.load_dam_data() — the existing, unmodified parser.
  - system_conditions is built by calling fetch.fetch_wind_and_demand() per date
    rather than parsing data/eirgrid_raw/*.json. There is no parser for the raw
    JSON today (fetch.py only ever fetches live and archives as a side effect),
    and the live EirGrid endpoint serves clean data back to at least 2026-05-10
    with no observed "ages out" boundary — so live re-fetch covers the full
    range uniformly instead of adding a second parser for ~20 sparse archived
    days. This also means running the backfill re-populates data/eirgrid_raw/
    for any date that was missing or incomplete (e.g. 2026-08-17..19, where the
    fetch worked but the archive write silently didn't happen).
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
from fetch import fetch_wind_and_demand

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
    retries: int = 3, retry_delay: float = 2.0, overwrite_raw: bool = False,
) -> tuple[int, list[str]]:
    """
    Live-fetch wind/demand for every date in [start, end] via fetch_wind_and_demand.
    EirGrid's demand endpoint intermittently returns no rows for a valid date —
    confirmed transient by retrying failed dates, which succeed within a few
    attempts — so each date gets `retries` attempts before being recorded failed.
    Returns (rows written, list of dates that failed / had no data).

    Raw EirGrid JSON already in out_dir/eirgrid_raw/ is left alone unless
    overwrite_raw=True: those files are what published posts were written from.
    """
    import time

    rows = 0
    failed = []
    d = start
    while d <= end:
        df = None
        for attempt in range(retries):
            df = fetch_wind_and_demand(d, out_dir=out_dir, overwrite_raw=overwrite_raw)
            if df is not None and not df.empty:
                break
            if attempt < retries - 1:
                time.sleep(retry_delay)
        if df is None or df.empty:
            failed.append(d.isoformat())
            d += timedelta(days=1)
            continue

        rows += upsert_system_conditions(conn, d, df)
        d += timedelta(days=1)

    conn.commit()
    return rows, failed


def pd_notna(value) -> bool:
    import pandas as pd
    return pd.notna(value)


if __name__ == "__main__":
    conn = build_db()

    price_rows = backfill_market_prices(conn)
    print(f"market_prices: {price_rows} rows")

    # Date range driven by what market_prices actually covers, not a hardcoded guess.
    date_range = conn.execute("SELECT MIN(date), MAX(date) FROM market_prices").fetchone()
    if date_range[0] is None:
        print("No market_prices rows — nothing to backfill for system_conditions.")
        sys.exit(0)

    start = date.fromisoformat(date_range[0])
    end = date.fromisoformat(date_range[1])
    print(f"Backfilling system_conditions for {start}..{end} (live EirGrid fetch)...")

    cond_rows, failed = backfill_system_conditions(conn, start, end)
    print(f"system_conditions: {cond_rows} rows")
    if failed:
        print(f"FAILED / no data for {len(failed)} date(s): {failed}")

    conn.close()
