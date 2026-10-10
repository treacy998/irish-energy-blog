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
from scaffold import PostExistsError, check_post_overwrite
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


def post(draft: str, body: str) -> str:
    return f"---\ntitle: \"t\"\ndraft: {draft}\n---\n\n{body}\n"


def refuses(path: Path, new_md: str, force=False) -> bool:
    try:
        check_post_overwrite(path, new_md, force)
        return False
    except PostExistsError:
        return True


def test_overwrite_guard_on_a_temp_content_tree():
    with tempfile.TemporaryDirectory() as t:
        out = Path(t) / "site" / "content" / "daily" / "2026-10-05" / "index.md"
        out.parent.mkdir(parents=True)
        scaffold = post("false", "## Commentary\n\n<!-- Write 2-3 paragraphs -->")
        assert not refuses(out, scaffold)                                    # no file yet
        out.write_text(post("true", "## Commentary\n\n<!-- Write 2-3 paragraphs -->"))
        assert not refuses(out, scaffold)                                    # untouched draft: rewritable
        out.write_text(post("true", "## Commentary\n\nWind collapsed on Thursday."))
        edited = out.read_text()
        assert refuses(out, scaffold) and out.read_text() == edited          # draft, but you wrote in it
        out.write_text(post("false", "## Commentary\n\n<!-- Write 2-3 paragraphs -->"))
        assert refuses(out, scaffold)                                        # published, body identical
        out.write_text(post("false", "## Commentary\n\nWritten and published."))
        published = out.read_text()
        assert refuses(out, scaffold) and out.read_text() == published       # published and edited
        assert not refuses(out, scaffold, force=True)                        # --force is the only way through


def test_run_daily_exits_nonzero_when_the_post_is_refused_and_still_stores():
    with tempfile.TemporaryDirectory() as t:
        db = seeded_db(Path(t))
        saved = run_daily.scaffold_daily
        def refuse(*a, **k):
            raise PostExistsError("site/content/daily/2026-10-05/index.md exists and it is published; refusing")
        code, out, _ = None, "", None
        try:
            # run_main replaces scaffold_daily, so wrap: install the refusing stub after its own stub is set
            import contextlib as cl, io as _io
            names = ("fetch_semo", "load_dam_data", "fetch_wind_and_demand", "upload_charts_for_date", "CHART_DIR")
            keep = {n: getattr(run_daily, n) for n in names}
            run_daily.fetch_semo = lambda delivery_date=None, out_dir=None: Path("MarketResult_SEM-DA_fake.csv")
            run_daily.load_dam_data = lambda p: price_df(DAY)
            run_daily.fetch_wind_and_demand = lambda d, out_dir=None: conditions_df(d)
            run_daily.upload_charts_for_date = lambda p: None
            run_daily.CHART_DIR = Path(t) / "charts"
            run_daily.scaffold_daily = refuse
            buf, argv = _io.StringIO(), sys.argv
            sys.argv = ["run_daily.py", "--date", DAY.isoformat(), "--db", str(db)]
            try:
                with cl.redirect_stdout(buf):
                    try:
                        run_daily.main()
                    except SystemExit as e:
                        code = e.code
            finally:
                sys.argv = argv
            out = buf.getvalue()
            for n, v in keep.items():
                setattr(run_daily, n, v)
        finally:
            run_daily.scaffold_daily = saved
        assert code == 1 and "POST NOT WRITTEN: " in out and "STORE" not in out, (code, out)
        assert sqlite3.connect(db).execute("SELECT COUNT(*) FROM market_prices WHERE date='2026-10-05'").fetchone()[0] == 48


def test_read_only_store_that_already_holds_the_day_is_skipped_quietly():
    with tempfile.TemporaryDirectory() as t:
        db = seeded_db(Path(t))
        from store import persist_day
        persist_day(DAY, price_df(DAY), conditions_df(DAY), db_path=db)       # the nightly run got there first
        os.chmod(db, 0o444)
        before = sqlite3.connect(db).execute("SELECT COUNT(*), SUM(dam_price_eur_mwh) FROM market_prices").fetchone()
        def must_not_be_called(*a, **k):
            raise AssertionError("persist_day called for a day the store already holds")
        code, out, scaffolded = run_main(db, persist=must_not_be_called)
        assert code is None and len(scaffolded) == 1, (code, out)
        assert "STORE NOT WRITABLE" not in out and "STORE WRITE FAILED" not in out, out
        assert "already stored" in out and "already holds 2026-10-05 in full" in out, out
        assert sqlite3.connect(db).execute("SELECT COUNT(*), SUM(dam_price_eur_mwh) FROM market_prices").fetchone() == before


def test_a_partial_day_is_not_treated_as_stored():
    with tempfile.TemporaryDirectory() as t:
        db = seeded_db(Path(t))
        from store import day_is_stored, persist_day
        persist_day(DAY, price_df(DAY), None, db_path=db)
        conn = sqlite3.connect(db)
        conn.execute("DELETE FROM market_prices WHERE date=? AND period=48", (DAY.isoformat(),))
        conn.commit(); conn.close()
        assert not day_is_stored(DAY, db) and not day_is_stored(date(2026, 10, 6), db) and day_is_stored(date(2026, 10, 4), db)
        os.chmod(db, 0o444)
        code, out, _ = run_main(db)
        assert code == 1 and "STORE NOT WRITABLE" in out and "STORE WRITE FAILED 2026-10-05" in out, out


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
