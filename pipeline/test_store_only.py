"""Tests for store.catch_up_store (run_daily.py --store-only) and store_write_problem.
Run: python pipeline/test_store_only.py   (temp directory only; every fetch is stubbed, no network)"""

import contextlib
import io
import os
import sqlite3
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import store
from trading_day import expected_periods, period_labels, period_starts_utc

Z = ZoneInfo("Europe/Dublin")
NOW = datetime(2026, 10, 9, 6, 30, tzinfo=Z)          # yesterday = 2026-10-08


def price_df(d: date) -> pd.DataFrame:
    n = expected_periods(d)
    return pd.DataFrame({
        "DeliveryDate": pd.Timestamp(d), "Period": range(1, n + 1), "StartTime": period_labels(d),
        "DAMPrice_EUR_MWh": [100.0 + p for p in range(1, n + 1)],
        "StartUTC": pd.DatetimeIndex(period_starts_utc(d)).astype("datetime64[ns, UTC]"),
    })


def conditions_df(d: date) -> pd.DataFrame:
    n = expected_periods(d)
    return pd.DataFrame({
        "StartUTC": pd.DatetimeIndex(period_starts_utc(d)).astype("datetime64[ns, UTC]"),
        "WindMW": [500.0] * n, "WindForecastMW": [450.0] * n, "DemandMW": [4000.0] * n,
        "WindGeneration_pct": [12.5] * n,
    })


class Harness:
    """A temp store seeded through `last`, with the network stubbed. unpublished = dates whose
    SEMO report does not exist; broken = dates whose fetch raises something else."""

    def __init__(self, tmp: Path, last=date(2026, 10, 4), unpublished=(), broken=(), wind_ok=True):
        self.db = tmp / "history.db"
        self.data = tmp / "data"
        self.unpublished, self.broken, self.wind_ok = set(unpublished), set(broken), wind_ok
        self.semo_calls, self.wind_calls, self.heal_calls = [], [], []
        store.persist_day(last, price_df(last), conditions_df(last), db_path=self.db)

    def run(self, **kw) -> tuple[int, str]:
        def fetch_semo(d, out_dir=None):
            self.semo_calls.append(d)
            if d in self.unpublished:
                raise FileNotFoundError(f"no report for {d}")
            if d in self.broken:
                raise RuntimeError("boom")
            return d
        def fetch_wind(d, out_dir=None, overwrite_raw=True):
            self.wind_calls.append((d, overwrite_raw))
            return conditions_df(d) if self.wind_ok else None
        def heal(conn, start, end, out_dir=None, dry_run=False):
            self.heal_calls.append((start, end))
        saved = (store.fetch_semo, store.load_dam_data, store.fetch_wind_and_demand, store.heal_demand)
        store.fetch_semo, store.load_dam_data = fetch_semo, price_df
        store.fetch_wind_and_demand, store.heal_demand = fetch_wind, heal
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                rc = store.catch_up_store(self.db, self.data, now=NOW, sleep_s=0, **kw)
        finally:
            store.fetch_semo, store.load_dam_data, store.fetch_wind_and_demand, store.heal_demand = saved
        return rc, out.getvalue()

    def max_date(self) -> str:
        return sqlite3.connect(self.db).execute("SELECT MAX(date) FROM market_prices").fetchone()[0]


def test_catches_up_from_store_max_through_yesterday_one_line_per_date():
    with tempfile.TemporaryDirectory() as t:
        h = Harness(Path(t))
        rc, out = h.run()
        assert rc == 0, out
        assert h.semo_calls == [date(2026, 10, d) for d in (5, 6, 7, 8)], h.semo_calls
        assert [l.split()[0] for l in out.splitlines()] == ["2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08"]
        assert "price_rows=48 cond_rows=48" in out.splitlines()[0]
        assert h.max_date() == "2026-10-08"


def test_raw_archives_are_never_overwritten():
    with tempfile.TemporaryDirectory() as t:
        h = Harness(Path(t))
        h.run()
        assert h.wind_calls and all(flag is False for _, flag in h.wind_calls), h.wind_calls


def test_yesterdays_price_not_published_is_exit_0_and_next_run_self_heals():
    with tempfile.TemporaryDirectory() as t:
        h = Harness(Path(t), unpublished={date(2026, 10, 8)})
        rc, out = h.run()
        assert rc == 0 and "2026-10-08 price not published yet" in out, out
        assert h.max_date() == "2026-10-07"
        h.unpublished.clear()
        rc, out = h.run()                                   # the retry starts from the store's max date
        assert rc == 0 and h.max_date() == "2026-10-08" and h.semo_calls[-1] == date(2026, 10, 8)


def test_older_missing_price_is_nonzero_and_stops_before_leaving_a_hole():
    with tempfile.TemporaryDirectory() as t:
        h = Harness(Path(t), unpublished={date(2026, 10, 6)})
        rc, out = h.run()
        assert rc == 1 and "2026-10-06 price FAIL" in out, out
        assert date(2026, 10, 7) not in h.semo_calls and h.max_date() == "2026-10-05"


def test_exception_on_yesterday_is_nonzero_not_mistaken_for_unpublished():
    with tempfile.TemporaryDirectory() as t:
        h = Harness(Path(t), broken={date(2026, 10, 8)})
        rc, out = h.run()
        assert rc == 2 and "not published" not in out and "RuntimeError: boom" in out, out


def test_at_most_14_dates_per_run_and_the_rest_is_nonzero():
    with tempfile.TemporaryDirectory() as t:
        h = Harness(Path(t), last=date(2026, 9, 1))
        rc, out = h.run()
        assert rc == 1 and len(h.semo_calls) == 14 and h.max_date() == "2026-09-15", (rc, h.max_date())
        assert "oldest 14" in out


def test_heal_pass_covers_the_last_14_days_through_yesterday():
    with tempfile.TemporaryDirectory() as t:
        h = Harness(Path(t))
        h.run()
        assert h.heal_calls == [(date(2026, 9, 25), date(2026, 10, 8))], h.heal_calls


def test_wind_unavailable_stores_prices_and_says_so():
    with tempfile.TemporaryDirectory() as t:
        h = Harness(Path(t), wind_ok=False)
        rc, out = h.run()
        assert rc == 0 and "cond_rows=0 wind unavailable" in out, out
        n = sqlite3.connect(h.db).execute("SELECT COUNT(*) FROM system_conditions WHERE date='2026-10-05'").fetchone()[0]
        assert n == 0                                       # no zero-valued rows


def test_read_only_store_fails_loudly_and_fetches_nothing():
    with tempfile.TemporaryDirectory() as t:
        h = Harness(Path(t))
        os.chmod(h.db, 0o444)
        rc, out = h.run()
        assert rc == 2 and out.startswith("STORE NOT WRITABLE"), out
        assert h.semo_calls == [] and h.max_date() == "2026-10-04"


def test_current_store_fetches_nothing():
    with tempfile.TemporaryDirectory() as t:
        h = Harness(Path(t), last=date(2026, 10, 8))
        rc, out = h.run()
        assert rc == 0 and h.semo_calls == [] and "current through 2026-10-08" in out


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
