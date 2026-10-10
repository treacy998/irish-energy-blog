"""Tests that --rebuild-conditions never replaces stored values with NULLs from an empty archive.
Run: python pipeline/test_rebuild_safety.py
Temp directory only: a synthetic store, plus (if data/ exists) a /tmp copy of the real database and
archives behind a connection guard. No network."""

import contextlib
import io
import json
import shutil
import sqlite3
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import store
from fetch import archive_path
from test_store_only import conditions_df, price_df

ROOT = Path(__file__).parent.parent
EMPTY = '{"Rows":[]}'


def raw_json(d: date, fields: dict) -> str:
    t0 = datetime(d.year, d.month, d.day)
    rows = [{"EffectiveTime": (t0 + timedelta(minutes=15 * i)).strftime("%d-%b-%Y %H:%M:%S"),
             "FieldName": field, "Region": "ROI", "Value": value}
            for field, value in fields.items() for i in range(96)]
    return json.dumps({"Rows": rows})


def write_archives(out: Path, days, demand_empty=()):
    for d in days:
        for area, fields in (("wind", {"WIND_ACTUAL": 900, "WIND_FCAST": 850}), ("demand", {"SYSTEM_DEMAND": 4100})):
            p = archive_path(d, area, out)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(EMPTY if (area == "demand" and d in demand_empty) else raw_json(d, fields))


def rows_of(conn, d: date):
    return conn.execute("SELECT * FROM system_conditions WHERE date=? ORDER BY period", (d.isoformat(),)).fetchall()


def rebuild(conn, start, end, out) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        store.rebuild_conditions(conn, start, end, out_dir=out)
    return buf.getvalue()


def test_empty_demand_archive_keeps_stored_rows_synthetic():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        db, out = t / "h.db", t / "data"
        d = date(2026, 10, 2)
        store.persist_day(d, price_df(d), conditions_df(d), db_path=db)     # stored demand 4000, wind 500
        write_archives(out, [d - timedelta(days=1), d, d + timedelta(days=1)], demand_empty={d})
        conn = store.build_db(db)
        before = rows_of(conn, d)
        text = rebuild(conn, d, d, out)
        assert "2026-10-02 rebuild SKIPPED archive empty, store kept" in text, text
        assert rows_of(conn, d) == before and all(r[5] == 4000.0 for r in before)


def test_previous_days_empty_archive_also_protects_periods_1_and_2():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        db, out = t / "h.db", t / "data"
        d = date(2026, 10, 3)
        store.persist_day(d, price_df(d), conditions_df(d), db_path=db)
        write_archives(out, [d - timedelta(days=1), d], demand_empty={d - timedelta(days=1)})
        conn = store.build_db(db)
        before = rows_of(conn, d)
        assert "SKIPPED archive empty, store kept" in rebuild(conn, d, d, out)
        assert rows_of(conn, d) == before


def test_a_date_whose_store_demand_is_already_null_is_still_rebuilt():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        db, out = t / "h.db", t / "data"
        d = date(2026, 10, 2)
        cond = conditions_df(d)
        cond["DemandMW"], cond["WindGeneration_pct"] = float("nan"), float("nan")
        store.persist_day(d, price_df(d), cond, db_path=db)
        write_archives(out, [d - timedelta(days=1), d, d + timedelta(days=1)], demand_empty={d})
        conn = store.build_db(db)
        text = rebuild(conn, d, d, out)
        assert "rebuilt rows=48" in text and "SKIPPED" not in text, text   # nothing to lose, so rebuild proceeds


def test_run_continues_after_a_skipped_date():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        db, out = t / "h.db", t / "data"
        for d in (date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 3)):
            store.persist_day(d, price_df(d), conditions_df(d), db_path=db)
        write_archives(out, [date(2026, 9, 30) + timedelta(days=i) for i in range(5)], demand_empty={date(2026, 10, 2)})
        lines = rebuild(store.build_db(db), date(2026, 10, 1), date(2026, 10, 3), out).splitlines()
        assert lines[0].startswith("2026-10-01 rebuilt") and lines[1].startswith("2026-10-02 rebuild SKIPPED"), lines
        assert lines[2].startswith("2026-10-03 rebuild SKIPPED"), lines     # its periods 1-2 need 10-02 demand


def test_real_database_copy_with_emptied_2026_10_01_demand_archive():
    real_db, real_raw = ROOT / "data" / "history.db", ROOT / "data" / "eirgrid_raw"
    if not real_db.exists() or not real_raw.exists():
        print("  (skipped: no real data/ here)")
        return
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        db, out = t / "b.db", t / "data"
        shutil.copyfile(real_db, db)
        for i in range(6):                                        # 2026-09-29 .. 2026-10-04
            d = date(2026, 9, 29) + timedelta(days=i)
            shutil.copytree(real_raw / d.isoformat(), out / "eirgrid_raw" / d.isoformat())
        archive_path(date(2026, 10, 1), "demand", out).write_text(EMPTY)      # the emptied copy
        real = sqlite3.connect
        guard = lambda path, *a, **k: real(path, *a, **k) if str(path).startswith(str(t)) else (_ for _ in ()).throw(
            AssertionError(f"connection guard: refusing {path}"))
        sqlite3.connect = guard
        try:
            conn = store.build_db(db)
            d1 = date(2026, 10, 1)
            before = rows_of(conn, d1)
            assert before and all(r[5] is not None for r in before), "store should hold demand for 10-01"
            text = rebuild(conn, date(2026, 9, 30), date(2026, 10, 4), out)
            after = rows_of(conn, d1)
        finally:
            sqlite3.connect = real
        print("  " + text.strip().replace("\n", "\n  "))
        assert "2026-10-01 rebuild SKIPPED archive empty, store kept" in text
        assert after == before


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
