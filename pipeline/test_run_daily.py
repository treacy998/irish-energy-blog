"""Tests for run_daily's normal mode: a store failure is loud and exits nonzero after the post.
Run: python pipeline/test_run_daily.py   (temp directory only; fetches, charts and scaffold are stubbed)"""

import contextlib
import io
import os
import sqlite3
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import run_daily
from test_store_only import conditions_df, price_df

DAY = date(2026, 10, 5)


def run_main(db: Path, argv_extra=(), persist=None) -> tuple[object, str, list]:
    """Run run_daily.main() for DAY with everything external stubbed.
    Returns (exit code or None, stdout, scaffold calls)."""
    scaffolded = []
    names = ("fetch_semo", "load_dam_data", "fetch_wind_and_demand", "scaffold_daily",
             "upload_charts_for_date", "CHART_DIR", "persist_day")
    saved = {n: getattr(run_daily, n) for n in names}
    run_daily.fetch_semo = lambda delivery_date=None, out_dir=None: Path("MarketResult_SEM-DA_fake.csv")
    run_daily.load_dam_data = lambda p: price_df(DAY)
    run_daily.fetch_wind_and_demand = lambda d, out_dir=None: conditions_df(d)
    run_daily.scaffold_daily = lambda *a, **k: scaffolded.append((a, k))
    run_daily.upload_charts_for_date = lambda p: None
    run_daily.CHART_DIR = db.parent / "charts"
    if persist:
        run_daily.persist_day = persist
    old_argv, out, code = sys.argv, io.StringIO(), None
    sys.argv = ["run_daily.py", "--date", DAY.isoformat(), "--db", str(db), *argv_extra]
    try:
        with contextlib.redirect_stdout(out):
            try:
                run_daily.main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = old_argv
        for n, v in saved.items():
            setattr(run_daily, n, v)
    return code, out.getvalue(), scaffolded


def seeded_db(tmp: Path) -> Path:
    from store import persist_day
    db = tmp / "history.db"
    persist_day(date(2026, 10, 4), price_df(date(2026, 10, 4)), conditions_df(date(2026, 10, 4)), db_path=db)
    return db


def test_writable_store_is_written_and_exit_is_clean():
    with tempfile.TemporaryDirectory() as t:
        db = seeded_db(Path(t))
        code, out, scaffolded = run_main(db)
        assert code is None and "STORE" not in out and len(scaffolded) == 1, out
        assert sqlite3.connect(db).execute("SELECT COUNT(*) FROM market_prices WHERE date='2026-10-05'").fetchone()[0] == 48


def test_read_only_store_fails_loudly_after_the_post_is_generated():
    with tempfile.TemporaryDirectory() as t:
        db = seeded_db(Path(t))
        os.chmod(db, 0o444)
        code, out, scaffolded = run_main(db)
        assert code == 1, (code, out)
        assert out.index("STORE NOT WRITABLE") < out.index("[1/3]"), out        # before anything else
        assert "STORE WRITE FAILED 2026-10-05" in out
        assert len(scaffolded) == 1                                           # the post was still generated
        assert out.rindex("STORE WRITE FAILED") > out.index("Next steps")     # and the exit comes last
        assert sqlite3.connect(db).execute("SELECT COUNT(*) FROM market_prices WHERE date='2026-10-05'").fetchone()[0] == 0


def test_persist_exception_prints_date_and_exception_and_exits_nonzero():
    with tempfile.TemporaryDirectory() as t:
        db = seeded_db(Path(t))
        def boom(*a, **k):
            raise sqlite3.OperationalError("database is locked")
        code, out, scaffolded = run_main(db, persist=boom)
        assert code == 1 and len(scaffolded) == 1, (code, out)
        assert "STORE WRITE FAILED 2026-10-05: OperationalError: database is locked" in out, out
        assert "STORE NOT WRITABLE" not in out


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
