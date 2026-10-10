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
  - Wind is required, demand is not. EirGrid's demand endpoint intermittently
    returns {"Rows":[]} for minutes at a time while wind is unaffected, so a date
    with wind but no demand is stored with demand_mw and wind_pct NULL (never 0,
    never filled) and can be healed later. A date is only ABSENT if wind is
    unavailable. Missing days must never appear as zero-valued rows — a rolling
    baseline computed over silent zeros would read a fetch failure as "no wind
    that day," which is a different and false claim.
  - Idempotent: both tables are keyed on (date, period) with INSERT OR REPLACE,
    so re-running the backfill (or a daily incremental run) never duplicates rows.
"""

import contextlib
import io
import os
import sqlite3
import sys
import time
import traceback
from pathlib import Path
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).parent))
from process import load_dam_data
from trading_day import calendar_label_to_utc, expected_periods, iso_z, period_labels, period_starts_utc
from fetch import (
    AREA_FIELDS, archive_path, archive_row_count, combine_for_trading_day,
    compute_wind_pct, fetch_area, fetch_semo, fetch_wind_and_demand, load_archived_area,
    load_archived_previous_day, resample_demand,
)

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = Path(__file__).parent.parent / "data" / "history.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS market_prices (
    date TEXT NOT NULL,
    period INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    dam_price_eur_mwh REAL NOT NULL,
    start_utc TEXT,
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
    start_utc TEXT,
    PRIMARY KEY (date, period)
);
"""

# start_utc (ISO 'Z' text) is the unambiguous instant; start_time is a local
# display label that repeats 01:00-02:00 on the autumn change day. Databases
# created before it existed get the column added; old rows keep NULL.
_MIGRATIONS = ("market_prices", "system_conditions")


def build_db(db_path: Path | None = None) -> sqlite3.Connection:
    # Resolved at call time, not definition time: a default of DB_PATH would
    # bind the real database permanently and ignore a patched DB_PATH.
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.executescript(SCHEMA)
    for table in _MIGRATIONS:
        cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        if "start_utc" not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN start_utc TEXT")
    return conn


def upsert_market_prices(conn: sqlite3.Connection, df) -> int:
    """Upsert a load_dam_data() DataFrame into market_prices. Returns rows written.
    Raises ValueError, writing nothing, if a delivery date doesn't have exactly
    expected_periods(date) rows (48; 50 or 46 on the clock-change days).
    Does not commit."""
    for day, grp in df.groupby(df["DeliveryDate"].dt.date):
        if len(grp) != expected_periods(day):
            raise ValueError(f"{day}: {len(grp)} price rows, expected {expected_periods(day)}")
    records = [
        (
            row["DeliveryDate"].date().isoformat(),
            int(row["Period"]),
            row["StartTime"],
            float(row["DAMPrice_EUR_MWh"]),
            iso_z(row["StartUTC"]),
        )
        for _, row in df.iterrows()
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO market_prices "
        "(date, period, start_time, dam_price_eur_mwh, start_utc) VALUES (?, ?, ?, ?, ?)",
        records,
    )
    return len(records)


def condition_grid(d: date, df):
    """One row per period of d's trading day (50/46/48), wind/demand joined on the
    UTC instant of each period's start. A half-hour with no reading is NaN, never 0."""
    import pandas as pd

    n = expected_periods(d)
    grid = pd.DataFrame({
        "Period": range(1, n + 1),
        "StartTime": period_labels(d),
        "StartUTC": pd.DatetimeIndex(period_starts_utc(d)).astype("datetime64[ns, UTC]"),
    })
    cols = ["WindMW", "WindForecastMW", "DemandMW", "WindGeneration_pct"]
    have = df.assign(StartUTC=df["StartUTC"].astype("datetime64[ns, UTC]"))
    for c in cols:
        if c not in have.columns:
            have[c] = float("nan")
    return grid.merge(have[["StartUTC"] + cols], on="StartUTC", how="left")


def upsert_system_conditions(conn: sqlite3.Connection, d: date, df) -> int:
    """Replace date d's system_conditions with one row per trading-day period.
    df is a fetch_wind_and_demand()/combine_for_trading_day() frame. Returns rows
    written (expected_periods(d)). Does not commit.

    period is the SEMO period number (1 = local 23:00 the evening before), so a
    row lines up with market_prices on (date, period) and on start_utc. Periods
    with no reading are stored with NULLs, never zeros. The date's rows are
    deleted first so rows written under the older calendar-day numbering cannot
    survive beside the new ones."""
    grid = condition_grid(d, df)
    records = [
        (
            d.isoformat(),
            int(row["Period"]),
            row["StartTime"],
            float(row["WindMW"]) if pd_notna(row["WindMW"]) else None,
            float(row["WindForecastMW"]) if pd_notna(row["WindForecastMW"]) else None,
            float(row["DemandMW"]) if pd_notna(row["DemandMW"]) else None,
            float(row["WindGeneration_pct"]) if pd_notna(row["WindGeneration_pct"]) else None,
            iso_z(row["StartUTC"]),
        )
        for _, row in grid.iterrows()
    ]
    conn.execute("DELETE FROM system_conditions WHERE date=?", (d.isoformat(),))
    conn.executemany(
        "INSERT OR REPLACE INTO system_conditions "
        "(date, period, start_time, wind_mw, wind_forecast_mw, demand_mw, wind_pct, start_utc) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        records,
    )
    return len(records)


def persist_day(d: date, price_df, conditions_df=None, db_path: Path | None = None) -> tuple[int, int]:
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


class BackfillResult(NamedTuple):
    rows: int                   # system_conditions rows written
    wind_failed: list[str]      # dates with no usable wind: nothing stored
    demand_missing: list[str]   # dates stored with at least one NULL demand_mw


def backfill_system_conditions(
    conn: sqlite3.Connection, start: date, end: date, out_dir: Path = DATA_DIR,
    retries: int = 2, backoff: float = 2.0, dry_run: bool = False,
) -> BackfillResult:
    """
    Fill system_conditions for every date in [start, end], archive first.

    Each area (wind, demand) is parsed from data/eirgrid_raw/<date>/<area>.json
    when that file holds at least one data row — no network call, and the
    values are exactly what the published post was written from. Only an area
    whose archive is missing or has zero rows is fetched live. Wind gets
    `retries` retries with exponential backoff (backoff, 2*backoff, ...);
    demand is tried once (see --heal). A live fetch
    never replaces an archive that has rows; a zero-row archive is overwritten.

    Commits after every date, so killing the run loses at most one day.
    Prints exactly one line per date: "<date> archive|api ok|FAIL rows=<n>"
    ("api" if any area needed the network). dry_run prints "<date> archive|api"
    and touches nothing.
    A date with wind but an empty demand feed is stored with demand_mw and
    wind_pct NULL and counts as "ok"; only a date with no usable wind fails.
    Returns a BackfillResult: rows written, dates with no usable wind, and dates
    stored with a demand gap (candidates for --heal).
    """
    import contextlib
    import io
    import time

    rows = 0
    failed = []
    demand_missing = []
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
                # Demand is tried once: its feed is empty for minutes at a time, so
                # retrying within seconds never helped; --heal is the retry. Wind
                # is reliable, so a transient HTTP error there is worth retrying.
                tries = 1 if area == "demand" else retries + 1
                for attempt in range(tries):
                    frames[area] = fetch_area(d, area, out_dir=out_dir, overwrite_raw=False)
                    if frames[area] is not None or attempt == tries - 1:
                        break
                    time.sleep(backoff * 2 ** attempt)
            # Periods 1-2 (the evening before) come from the previous date's archive, offline.
            prev_wind, prev_demand = load_archived_previous_day(d, out_dir)
            df = combine_for_trading_day(d, frames.get("wind"), frames.get("demand"), prev_wind, prev_demand)

        if df is None or df.empty:
            failed.append(d.isoformat())
            print(f"{d.isoformat()} {source} FAIL rows=0", flush=True)
        else:
            n = upsert_system_conditions(conn, d, df)
            conn.commit()
            rows += n
            if df["DemandMW"].isna().any():
                demand_missing.append(d.isoformat())
            print(f"{d.isoformat()} {source} ok rows={n}", flush=True)
        d += timedelta(days=1)

    return BackfillResult(rows, failed, demand_missing)


def missing_price_dates(conn: sqlite3.Connection, start: date, end: date) -> list[str]:
    """Dates in [start, end] with no market_prices rows at all."""
    have = {r[0] for r in conn.execute(
        "SELECT DISTINCT date FROM market_prices WHERE date BETWEEN ? AND ?",
        (start.isoformat(), end.isoformat()),
    )}
    out, d = [], start
    while d <= end:
        if d.isoformat() not in have:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def wrong_price_counts(conn: sqlite3.Connection, start: date, end: date) -> list[str]:
    """'<date> <rows> of <expected>' for each date in [start, end] whose market_prices
    row count isn't expected_periods(date): 48, or 50/46 on the clock-change days."""
    out = []
    for ds, n in conn.execute(
        "SELECT date, COUNT(*) FROM market_prices WHERE date BETWEEN ? AND ? GROUP BY date ORDER BY date",
        (start.isoformat(), end.isoformat()),
    ):
        want = expected_periods(date.fromisoformat(ds))
        if n != want:
            out.append(f"{ds} {n} of {want}")
    return out


def heal_demand(
    conn: sqlite3.Connection, start: date, end: date, out_dir: Path = DATA_DIR,
    dry_run: bool = False,
) -> list[str]:
    """
    Fill demand_mw and wind_pct on stored dates whose demand was empty.

    Selects every date in [start, end] with at least one NULL demand_mw row. For
    each, demand only is fetched once — no retry loop, so the request count is
    exactly the number of selected dates. EirGrid's feed is empty for minutes at
    a time; the next heal run simply tries again. The raw archive is not read
    first: a partial archive (some half-hours) would otherwise block the
    re-fetch of the rest.

    Only that date's rows with NULL demand_mw are updated, matched on start_time;
    wind_mw, wind_forecast_mw and every other date are left alone. wind_pct uses
    the same computation as the normal path. Raw demand.json is written only if
    the response has rows. Commits after every date.

    Prints exactly one line per date: "<date> heal ok|still-empty rows_filled=<n>",
    or "<date> heal FAIL <exception class>: <message>" if the request raised or
    returned a non-200 status (that date is skipped; the run continues).
    dry_run prints "<date> heal dry-run", makes no request and writes nothing.
    Returns the dates that were filled.
    """
    import contextlib
    import io

    import pandas as pd

    dates = [r[0] for r in conn.execute(
        "SELECT DISTINCT date FROM system_conditions "
        "WHERE date BETWEEN ? AND ? AND demand_mw IS NULL ORDER BY date",
        (start.isoformat(), end.isoformat()),
    )]

    healed = []
    for ds in dates:
        d = date.fromisoformat(ds)
        if dry_run:
            print(f"{ds} heal dry-run")
            continue

        try:
            with contextlib.redirect_stdout(io.StringIO()):   # keep one line per date
                demand = fetch_area(d, "demand", out_dir=out_dir, overwrite_raw=False, raise_errors=True)
                demand_30 = resample_demand(demand) if demand is not None else None
        except Exception as e:
            # A request error or non-200: say which, and carry on with the next date.
            print(f"{ds} heal FAIL {type(e).__name__}: {' '.join(str(e).split())}", flush=True)
            continue

        filled = 0
        if demand_30 is not None:
            by_utc = {iso_z(t): float(v)
                      for t, v in zip(demand_30["StartUTC"], demand_30["DemandMW"])}
            # The evening-before periods (1-2) are in the previous date's demand, read offline.
            prev_demand = load_archived_area(d - timedelta(days=1), "demand", out_dir)
            prev_30 = resample_demand(prev_demand) if prev_demand is not None else None
            if prev_30 is not None:
                by_utc.update({iso_z(t): float(v) for t, v in zip(prev_30["StartUTC"], prev_30["DemandMW"])
                               if iso_z(t) not in by_utc})
            rows = conn.execute(
                "SELECT period, start_time, start_utc, wind_mw FROM system_conditions "
                "WHERE date=? AND demand_mw IS NULL",
                (ds,),
            ).fetchall()
            cur = pd.DataFrame(rows, columns=["period", "start_time", "start_utc", "wind_mw"])
            cur["wind_mw"] = pd.to_numeric(cur["wind_mw"])              # NULL -> NaN
            # Rows stored before start_utc existed: derive it from the calendar
            # date + local label (None, so unmatched, inside a clock-change hour).
            cur["start_utc"] = [
                u if u else (lambda t: iso_z(t) if t is not None else None)(calendar_label_to_utc(d, lab))
                for u, lab in zip(cur["start_utc"], cur["start_time"])
            ]
            cur["demand_mw"] = cur["start_utc"].map(by_utc)             # unmatched -> NaN
            cur = cur[cur["demand_mw"].notna()].copy()
            cur["wind_pct"] = compute_wind_pct(cur["wind_mw"], cur["demand_mw"])
            for r in cur.itertuples(index=False):
                filled += conn.execute(
                    "UPDATE system_conditions SET demand_mw=?, wind_pct=? "
                    "WHERE date=? AND period=? AND demand_mw IS NULL",
                    (float(r.demand_mw), None if pd.isna(r.wind_pct) else float(r.wind_pct), ds, int(r.period)),
                ).rowcount
        conn.commit()

        if filled:
            healed.append(ds)
        print(f"{ds} heal {'ok' if filled else 'still-empty'} rows_filled={filled}", flush=True)
    return healed


def backfill_prices(conn: sqlite3.Connection, start: date, end: date, data_dir: Path = DATA_DIR,
                    sleep_s: float = 1.0) -> list[str]:
    """Prices only: fetch each SEMO DA report for [start, end] and upsert market_prices.

    For each delivery date, fetch_semo() downloads the file into data_dir (skipping
    the download if it is already there), load_dam_data() parses it and checks
    every period against the trading-day mapping, and upsert_market_prices() writes
    it with start_utc. Idempotent (INSERT OR REPLACE). Commits per date; sleeps
    sleep_s between dates. Nothing else is touched: no wind or demand requests.

    Prints one line per date: "<date> ok|FAIL rows=<n> expected=<n>", where expected
    is expected_periods(date): 48, or 50 / 46 on the clock-change days. A FAIL
    (no report on the endpoint, a parse or period-count error, a request error)
    prints its reason to stderr and the run carries on. Returns the FAIL dates."""
    failed = []
    d = start
    while d <= end:
        want = expected_periods(d)
        rows = 0
        try:
            df = load_dam_data(fetch_semo(d, out_dir=data_dir))
            if df["DeliveryDate"].iloc[0].date() != d:
                raise ValueError(f"file is for {df['DeliveryDate'].iloc[0].date()}, not {d}")
            rows = upsert_market_prices(conn, df)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"  [store] {d.isoformat()}: {type(e).__name__}: {e}", file=sys.stderr)
            rows = 0
        ok = rows == want
        if not ok:
            failed.append(d.isoformat())
        print(f"{d.isoformat()} {'ok' if ok else 'FAIL'} rows={rows} expected={want}", flush=True)
        d += timedelta(days=1)
        if d <= end and sleep_s:
            time.sleep(sleep_s)
    return failed


def _would_lose_values(stored: dict, grid) -> bool:
    """True if any stored non-NULL wind/forecast/demand would become NULL in the rebuilt grid.
    stored is {period: (wind_mw, wind_forecast_mw, demand_mw)}; grid is condition_grid()'s frame."""
    for row in grid.itertuples(index=False):
        old = stored.get(int(row.Period))
        if old is None:
            continue
        new = (row.WindMW, row.WindForecastMW, row.DemandMW)
        if any(o is not None and not pd_notna(n) for o, n in zip(old, new)):
            return True
    return False


def rebuild_conditions(conn: sqlite3.Connection, start: date, end: date, out_dir: Path = DATA_DIR) -> int:
    """Rebuild system_conditions for [start, end] from local archives only (no network).

    Each date is replaced by one row per trading-day period with start_utc set,
    through the same condition_grid/upsert path the daily run uses. A date with
    no usable wind archive is left as it is and reported SKIP. Commits per date.

    A date is never made poorer: if the rebuild would turn a stored non-NULL wind,
    forecast or demand value into NULL (its own archive, or the previous day's for
    periods 1-2, is empty or missing), the store's rows are kept and the date is
    reported "<date> rebuild SKIPPED archive empty, store kept". The run carries on.

    Prints one line per date: "<date> rebuilt rows=<n> wind_null=<n> demand_null=<n>".
    Returns the number of dates rebuilt."""
    import contextlib
    import io

    done = 0
    d = start
    while d <= end:
        ds = d.isoformat()
        with contextlib.redirect_stdout(io.StringIO()):
            wind = load_archived_area(d, "wind", out_dir)
            demand = load_archived_area(d, "demand", out_dir)
            prev_wind, prev_demand = load_archived_previous_day(d, out_dir)
            df = combine_for_trading_day(d, wind, demand, prev_wind, prev_demand)
        stored = {r[0]: r[1:] for r in conn.execute(
            "SELECT period, wind_mw, wind_forecast_mw, demand_mw FROM system_conditions WHERE date=?", (ds,))}
        if df is None or df.empty:
            if any(v is not None for vals in stored.values() for v in vals):
                print(f"{ds} rebuild SKIPPED archive empty, store kept", flush=True)
            else:
                print(f"{ds} rebuild SKIP no usable wind archive", flush=True)
        elif _would_lose_values(stored, condition_grid(d, df)):
            print(f"{ds} rebuild SKIPPED archive empty, store kept", flush=True)
        else:
            n = upsert_system_conditions(conn, d, df)
            conn.commit()
            wn, dn = conn.execute(
                "SELECT SUM(wind_mw IS NULL), SUM(demand_mw IS NULL) FROM system_conditions WHERE date=?", (ds,)
            ).fetchone()
            print(f"{ds} rebuilt rows={n} wind_null={wn} demand_null={dn}", flush=True)
            done += 1
        d += timedelta(days=1)
    return done


def rebuild_price_utc(conn: sqlite3.Connection, start: date, end: date, data_dir: Path = DATA_DIR) -> int:
    """Set start_utc on market_prices for [start, end] from the local SEMO CSVs (no network).

    Prices are loaded by process.load_dam_data(), the same parser backfill_market_prices
    replays; where several files exist for one delivery date the last in name order wins,
    as in that replay. Only start_utc is written, and only on a row whose (date, period,
    start_time) matches the file, so a price is never touched. Commits per date.
    Prints one line per date: "<date> prices start_utc rows=<file rows> updated=<n>".
    Returns the number of dates processed."""
    by_date = {}
    for csv_path in sorted(data_dir.glob("MarketResult_SEM-DA_*.csv")):
        try:
            df = load_dam_data(csv_path)
        except ValueError as e:
            print(f"  [store] SKIP {csv_path.name}: {e}")
            continue
        by_date[df["DeliveryDate"].iloc[0].date()] = df
    done = 0
    for d in sorted(by_date):
        if not start <= d <= end:
            continue
        df = by_date[d]
        updated = 0
        for _, row in df.iterrows():
            updated += conn.execute(
                "UPDATE market_prices SET start_utc=? WHERE date=? AND period=? AND start_time=?",
                (iso_z(row["StartUTC"]), d.isoformat(), int(row["Period"]), row["StartTime"]),
            ).rowcount
        conn.commit()
        print(f"{d.isoformat()} prices start_utc rows={len(df)} updated={updated}", flush=True)
        done += 1
    return done


def pd_notna(value) -> bool:
    import pandas as pd
    return pd.notna(value)


def _label(name: str, dates: list[str]) -> str:
    return f"{name}: {len(dates)} dates: {','.join(dates) if dates else 'none'}"


def store_write_problem(db_path: Path | None = None, must_exist: bool = True) -> str | None:
    """Why the store can't be written, or None if it can. SQLite needs the file writable and,
    for its journal, the directory; a chmod 444 file fails here instead of mid-transaction.
    must_exist=False accepts a missing file (the first write creates it) if its directory is writable."""
    db = Path(db_path or DB_PATH)
    if not db.exists():
        if must_exist:
            return f"{db} does not exist"
        return None if os.access(db.parent, os.W_OK) else f"{db.parent} is not writable"
    if not os.access(db, os.W_OK):
        return f"{db} is not writable (mode {oct(db.stat().st_mode & 0o777)})"
    if not os.access(db.parent, os.W_OK):
        return f"{db.parent} is not writable (SQLite cannot create its journal)"
    return None


def day_is_stored(d: date, db_path: Path | None = None) -> bool:
    """True if market_prices already holds d in full: expected_periods(d) rows, none with a NULL
    price. Read-only (mode=ro), so it works on a chmod 444 database."""
    db = Path(db_path or DB_PATH)
    if not db.exists():
        return False
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        n, nulls = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(dam_price_eur_mwh IS NULL), 0) FROM market_prices WHERE date=?",
            (d.isoformat(),)).fetchone()
    except sqlite3.Error:
        return False
    finally:
        conn.close()
    return n == expected_periods(d) and nulls == 0


def catch_up_store(db_path: Path | None = None, data_dir: Path = DATA_DIR, now: datetime | None = None,
                   sleep_s: float = 1.0, max_dates: int = 14, heal_days: int = 14) -> int:
    """Store only: no posts, no charts, no BESS. Fetch prices and conditions for every delivery
    date from MAX(market_prices.date)+1 through yesterday (Irish calendar), oldest first, at most
    max_dates per run, sleep_s apart, each written with persist_day. Then one heal pass over the
    last heal_days days. A missed run self-heals: the next one starts from the store's max date.

    Raw EirGrid archives are fetched with overwrite_raw=False, so an archive that has rows is
    never replaced. A date whose price fails stops the run, so the store never gains a hole
    behind its max date.

    One line per date. Exit code: 0 = nothing missing, or only yesterday's price is not
    published yet; 1 = an older price is missing (or more dates remain than max_dates);
    2 = the store is not writable, or an exception (including any failure other than
    'no report yet' for yesterday) was raised."""
    db = Path(db_path or DB_PATH)
    problem = store_write_problem(db)
    if problem:
        print(f"STORE NOT WRITABLE: {problem}", flush=True)
        return 2
    yesterday = (now or datetime.now(ZoneInfo("Europe/Dublin"))).date() - timedelta(days=1)

    conn = build_db(db)
    try:
        last = conn.execute("SELECT MAX(date) FROM market_prices").fetchone()[0]
    finally:
        conn.close()
    if last is None:
        print("store has no market_prices rows; seed it with store.py --backfill-prices first", flush=True)
        return 2

    todo, d = [], date.fromisoformat(last) + timedelta(days=1)
    while d <= yesterday:
        todo.append(d)
        d += timedelta(days=1)
    rc = 0
    if len(todo) > max_dates:
        print(f"{len(todo)} dates behind; fetching the oldest {max_dates} this run", flush=True)
        rc = 1
        todo = todo[:max_dates]
    if not todo:
        print(f"store is current through {last}", flush=True)

    for i, d in enumerate(todo):
        if i and sleep_s:
            time.sleep(sleep_s)
        ds = d.isoformat()
        try:
            with contextlib.redirect_stdout(io.StringIO()):     # keep one line per date
                price_df = load_dam_data(fetch_semo(d, out_dir=data_dir))
            if price_df["DeliveryDate"].iloc[0].date() != d:
                raise ValueError(f"file is for {price_df['DeliveryDate'].iloc[0].date()}, not {d}")
        except Exception as e:
            reason = f"{type(e).__name__}: {' '.join(str(e).split())}"
            if d == yesterday and isinstance(e, FileNotFoundError):     # fetch_semo: no such report yet
                print(f"{ds} price not published yet ({reason})", flush=True)
            else:
                print(f"{ds} price FAIL ({reason}); stopping, later dates would leave a hole", flush=True)
                rc = max(rc, 2 if d == yesterday else 1)
            break
        try:
            cond_note = ""
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    conditions = fetch_wind_and_demand(d, out_dir=data_dir, overwrite_raw=False)
            except Exception as e:
                conditions, cond_note = None, f" conditions-error {type(e).__name__}: {' '.join(str(e).split())}"
            price_rows, cond_rows = persist_day(d, price_df, conditions, db_path=db)
            if conditions is None and not cond_note:
                cond_note = " wind unavailable"
            print(f"{ds} ok price_rows={price_rows} cond_rows={cond_rows}{cond_note}", flush=True)
        except Exception as e:
            print(f"STORE WRITE FAILED {ds}: {e}", flush=True)
            return 2

    try:
        conn = build_db(db)
        try:
            heal_demand(conn, yesterday - timedelta(days=heal_days - 1), yesterday, out_dir=data_dir)
        finally:
            conn.close()
    except Exception as e:
        traceback.print_exc()
        print(f"heal pass raised {type(e).__name__}: {e}", flush=True)
        return 2
    return rc


def _run(args) -> int:
    # A dry run only reads the date range, so it never takes a write lock.
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) if args.dry_run else build_db()
    try:
        if args.prices and not args.dry_run:
            print(f"market_prices: {backfill_market_prices(conn, DATA_DIR)} rows", flush=True)

        if args.backfill_prices:
            failed = backfill_prices(conn, date.fromisoformat(args.start), date.fromisoformat(args.end))
            return 1 if failed else 0

        if args.rebuild_prices or args.rebuild_conditions:
            lo, hi = conn.execute("SELECT MIN(date), MAX(date) FROM market_prices").fetchone()
            start = date.fromisoformat(args.start or lo)
            end = date.fromisoformat(args.end or hi)
            if args.rebuild_prices:
                rebuild_price_utc(conn, start, end)
            if args.rebuild_conditions:
                rebuild_conditions(conn, start, end)
            return 0

        if args.heal:
            lo, hi = conn.execute("SELECT MIN(date), MAX(date) FROM system_conditions").fetchone()
            heal_demand(conn, date.fromisoformat(args.start or lo), date.fromisoformat(args.end or hi),
                        out_dir=DATA_DIR, dry_run=args.dry_run)
            return 0

        # Default range follows what market_prices actually covers, not a hardcoded guess.
        lo, hi = conn.execute("SELECT MIN(date), MAX(date) FROM market_prices").fetchone()
        start = date.fromisoformat(args.start or lo)
        end = date.fromisoformat(args.end or hi)

        result = backfill_system_conditions(conn, start, end, out_dir=DATA_DIR, dry_run=args.dry_run)
        if args.dry_run:
            return 0

        price_missing = missing_price_dates(conn, start, end)
        price_wrong = wrong_price_counts(conn, start, end)
        if price_wrong:
            print(_label("price period count wrong", price_wrong))
        if result.wind_failed:
            print(_label("wind missing", result.wind_failed))
        if price_missing:
            print(_label("price missing", price_missing))
        # Always the last line. Empty-demand dates are expected gaps for --heal, not failures.
        print(_label("demand missing", result.demand_missing))
        return 1 if (result.wind_failed or price_missing or price_wrong) else 0
    finally:
        conn.close()


def main(argv=None) -> int:
    """Exit codes: 0 = done (empty-demand dates are allowed); 1 = wind or prices
    missing for at least one date; 2 = an exception aborted the run."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Backfill data/history.db system_conditions (archive first).",
        epilog="exit codes: 0 ok (demand gaps allowed), 1 wind or prices missing, 2 exception",
    )
    parser.add_argument("--start", metavar="YYYY-MM-DD", help="First date (default: first market_prices date).")
    parser.add_argument("--end", metavar="YYYY-MM-DD", help="Last date (default: last market_prices date).")
    parser.add_argument("--prices", action="store_true",
                        help="Also replay every SEMO CSV in data/ into market_prices first.")
    parser.add_argument("--heal", action="store_true",
                        help="Instead of a backfill, fill demand_mw/wind_pct on stored dates where "
                             "demand was empty (one request per date, no retries).")
    parser.add_argument("--backfill-prices", action="store_true",
                        help="Prices only: fetch the SEMO DA report for each date in --start..--end (both "
                             "required) and upsert market_prices. Idempotent, commits per date, 1 s between "
                             "dates; exit 0 only if no date FAILed.")
    parser.add_argument("--rebuild-conditions", action="store_true",
                        help="Offline: rebuild system_conditions for --start/--end from data/eirgrid_raw, "
                             "one row per trading-day period with start_utc set (replaces the date's rows).")
    parser.add_argument("--rebuild-prices", action="store_true",
                        help="Offline: set start_utc on market_prices for --start/--end from the local SEMO files.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Backfill: print which source each date would use. Heal: list the dates "
                             "that would be fetched. No network, no DB writes.")
    args = parser.parse_args(argv)
    if args.dry_run and (args.rebuild_prices or args.rebuild_conditions or args.backfill_prices):
        parser.error("--dry-run does not apply to the rebuild/backfill-prices flags")
    if args.backfill_prices and not (args.start and args.end):
        parser.error("--backfill-prices needs both --start and --end")
    try:
        return _run(args)
    except Exception:
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
