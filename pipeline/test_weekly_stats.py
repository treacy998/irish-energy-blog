"""Tests for weekly_stats on a synthetic in-memory store. Run: python pipeline/test_weekly_stats.py

The store has the real span (2025-10-07 onward) and the real clock-change days, so the
seasonal-baseline dates asserted here are the ones the live store produces.
"""

import json
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from trading_day import expected_periods
from weekly_stats import seasonal_baseline_starts, weekly_summary


def make_store(first=date(2025, 10, 7), last=date(2026, 10, 25)) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE market_prices (date TEXT, period INTEGER, start_time TEXT, dam_price_eur_mwh REAL,
                                    start_utc TEXT, PRIMARY KEY (date, period));
        CREATE TABLE system_conditions (date TEXT, period INTEGER, start_time TEXT, wind_mw REAL,
                                        wind_forecast_mw REAL, demand_mw REAL, wind_pct REAL, start_utc TEXT,
                                        PRIMARY KEY (date, period));""")
    d = first
    while d <= last:
        for p in range(1, expected_periods(d) + 1):
            price = 60 + (d.toordinal() * 7 % 53) * 2.5 + (p * 5 % 31) * 3 + (d.toordinal() // 7 % 11)
            conn.execute("INSERT INTO market_prices VALUES (?,?,?,?,NULL)", (d.isoformat(), p, f"{p:02d}:00", price))
            if d >= date(2026, 5, 3):
                conn.execute("INSERT INTO system_conditions VALUES (?,?,?,?,NULL,NULL,NULL,NULL)",
                             (d.isoformat(), p, f"{p:02d}:00", 500.0 + d.toordinal() % 13 * 100 + p))
        d += timedelta(days=1)
    conn.commit()
    return conn


def test_seasonal_dates_pinned():
    conn = make_store()
    r = weekly_summary(date(2026, 9, 28), conn)
    assert r["seasonal"] is None and r["seasonal_n"] == 1 and "need 4" in r["seasonal_reason"]
    r = weekly_summary(date(2026, 10, 12), conn)
    assert r["seasonal"] is None and r["seasonal_n"] == 3
    r = weekly_summary(date(2026, 10, 19), conn)
    assert r["seasonal_n"] == 4 and r["seasonal"]["n"] == 4 and not r["seasonal"]["suppressed"]
    assert r["seasonal"]["verdict_price"] is not None and r["seasonal"]["rank_of"] == 5
    starts, why = seasonal_baseline_starts(conn, date(2026, 10, 19))
    assert len(starts) == 4 and why is None
    assert seasonal_baseline_starts(conn, date(2026, 9, 28))[0] == []


def test_trailing_suppressed_below_8_weeks():
    for keep, suppressed in ((5, True), (7, True), (8, False)):
        conn = make_store()
        target = date(2026, 6, 1)
        conn.execute("DELETE FROM market_prices WHERE date < ?", ((target - timedelta(days=7 * keep)).isoformat(),))
        r = weekly_summary(target, conn)
        t = r["trailing"]
        assert t["n"] == keep and t["suppressed"] is suppressed, (keep, t["n"])
        if suppressed:
            assert r["verdict_price"] is None and t["rank"] is None and t["dearest_since"] is None
            assert t["verdict_volatility"] is None and t["reason"]
        else:
            assert r["verdict_price"] is not None and t["rank"] is not None


def test_missing_or_short_day_raises():
    conn = make_store()
    conn.execute("DELETE FROM market_prices WHERE date = '2026-09-30'")
    try:
        weekly_summary(date(2026, 9, 28), conn)
        raise AssertionError("missing day did not raise")
    except ValueError as e:
        assert "2026-09-30" in str(e)
    conn = make_store()
    conn.execute("DELETE FROM market_prices WHERE date = '2026-09-30' AND period = 48")
    try:
        weekly_summary(date(2026, 9, 28), conn)
        raise AssertionError("short day did not raise")
    except ValueError as e:
        assert "47 of 48" in str(e)


def test_not_a_monday_raises():
    try:
        weekly_summary(date(2026, 9, 29), make_store())
        raise AssertionError
    except ValueError:
        pass


def test_long_day_inside_week_counts_50_periods():
    conn = make_store()
    r = weekly_summary(date(2025, 10, 20), conn)       # contains 2025-10-26, 50 periods
    assert r["n_periods"] == 6 * 48 + 50
    avg = conn.execute("SELECT AVG(dam_price_eur_mwh) FROM market_prices WHERE date BETWEEN '2025-10-20' AND '2025-10-26'").fetchone()[0]
    assert r["week_mean"] == round(avg, 2)
    short = weekly_summary(date(2026, 3, 23), conn)    # contains 2026-03-29, 46 periods
    assert short["n_periods"] == 6 * 48 + 46


def test_reproducible_when_later_rows_are_removed():
    full = make_store()
    cut = make_store()
    cut.execute("DELETE FROM market_prices WHERE date > '2026-10-04'")
    cut.execute("DELETE FROM system_conditions WHERE date > '2026-10-04'")
    a = json.dumps(weekly_summary(date(2026, 9, 28), full), sort_keys=True)
    b = json.dumps(weekly_summary(date(2026, 9, 28), cut), sort_keys=True)
    assert a == b


def test_wind_is_not_imputed():
    conn = make_store()
    conn.execute("UPDATE system_conditions SET wind_mw = NULL WHERE date = '2026-09-30'")
    r = weekly_summary(date(2026, 9, 28), conn)
    assert r["wind_coverage"] == round(1 - 48 / 336, 3)
    early = weekly_summary(date(2025, 10, 20), conn)    # no system_conditions that early
    assert early["wind_mw_mean"] is None and early["wind_coverage"] == 0.0


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
