"""Tests for weekly_chart / build_weekly_post / weekly.py on a synthetic in-memory store.
Run: python pipeline/test_weekly_post.py   (writes only under a temp directory)"""

import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import weekly
from charts import weekly_chart
from scaffold import build_weekly_post, weekly_verdict_text
from test_weekly_stats import make_store
from weekly_stats import weekly_summary


def test_last_complete_week():
    Z = ZoneInfo("Europe/Dublin")
    cases = {  # now -> Monday of the week to build
        datetime(2026, 10, 5, 6, 0, tzinfo=Z): date(2026, 9, 28),    # Monday: last week
        datetime(2026, 10, 11, 23, 0, tzinfo=Z): date(2026, 9, 28),   # Sunday: this week not over
        datetime(2026, 10, 12, 0, 5, tzinfo=Z): date(2026, 10, 5),    # next Monday
        datetime(2026, 10, 7, 12, 0, tzinfo=Z): date(2026, 9, 28),    # midweek
    }
    for now, want in cases.items():
        assert weekly.last_complete_week(now) == want, now


def test_verdict_text_rank_first_then_label():
    s = weekly_summary(date(2026, 9, 28), make_store())
    text = weekly_verdict_text(s)
    t = s["trailing"]
    assert text.startswith(f"{t['rank']}") and "dearest of the last 14 weeks; last dearer: week of" in text
    assert text.index("dearest of the last") < text.index(s["verdict_price"])


def test_verdict_text_suppressed_says_so_and_invents_nothing():
    conn = make_store()
    conn.execute("DELETE FROM market_prices WHERE date < '2026-06-15'")
    s = weekly_summary(date(2026, 8, 3), conn)                 # n=7 earlier weeks
    text = weekly_verdict_text(s)
    assert s["verdict_price"] is None and "No verdict this week" in text
    assert "dearest" not in text and "normal" not in text


def test_verdict_text_week_on_week_clause_only_beyond_10_percent():
    s = weekly_summary(date(2026, 9, 28), make_store())
    s["previous_week_mean"] = s["week_mean"] / 1.05
    assert "Week on week" not in weekly_verdict_text(s)
    s["previous_week_mean"] = s["week_mean"] / 1.2
    assert "Week on week: up 20%." in weekly_verdict_text(s)
    s["previous_week_mean"] = s["week_mean"] / 0.7
    assert "Week on week: down 30%." in weekly_verdict_text(s)


def test_rank_one_wording():
    s = weekly_summary(date(2026, 9, 28), make_store())
    s["trailing"].update(rank=1, dearest_since=None)
    text = weekly_verdict_text(s)
    assert text.startswith("Dearest of the last 14 weeks; no earlier week in the store was as dear.")


def test_post_contents_order_and_rules():
    s = weekly_summary(date(2026, 9, 28), make_store())
    with tempfile.TemporaryDirectory() as tmp:
        post = build_weekly_post(s, Path(tmp))
        md = post.read_text()
        assert post == Path(tmp) / "weekly" / "2026-09-28" / "index.md"
        assert "draft: true" in md and "week_start: 2026-09-28" in md
        body = md.split("---\n", 2)[2]
        assert body.index("dearest of the last") < body.index("![") < body.index("Week mean (c/kWh)") \
            < body.index("## How this week compares") < body.index("## Daily means")
        assert "Write 2-3 paragraphs" in md and "not your bill" in md
        for banned in ("gas", "interconnector", "outage", "wind %", "% wind"):
            assert banned not in md.lower(), banned
        try:
            build_weekly_post(s, Path(tmp))
            raise AssertionError("overwrote an existing post")
        except FileExistsError:
            pass
        build_weekly_post(s, Path(tmp), force=True)


def test_suppressed_post_has_no_verdict_rows():
    conn = make_store()
    conn.execute("DELETE FROM market_prices WHERE date < '2026-06-15'")
    s = weekly_summary(date(2026, 8, 3), conn)
    with tempfile.TemporaryDirectory() as tmp:
        md = build_weekly_post(s, Path(tmp)).read_text()
    assert "Rank vs trailing" not in md and "Price verdict" not in md and "no volatility verdict" in md


def test_chart_renders_with_and_without_seasonal_and_with_short_baseline():
    conn = make_store()
    with tempfile.TemporaryDirectory() as tmp:
        for name, ws, trim in (("plain", date(2026, 9, 28), None), ("seasonal", date(2026, 10, 19), None),
                               ("short", date(2026, 8, 3), "2026-06-15")):
            c = make_store()
            if trim:
                c.execute("DELETE FROM market_prices WHERE date < ?", (trim,))
            out = weekly_chart(weekly_summary(ws, c), Path(tmp) / f"{name}.png")
            assert out.exists() and out.stat().st_size > 10_000, name


def test_build_refuses_when_final_day_missing_and_never_writes_then():
    import sqlite3
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "h.db"
        disk = sqlite3.connect(db)
        make_store().backup(disk)
        disk.execute("DELETE FROM market_prices WHERE date = '2026-10-04'")
        disk.commit()
        disk.close()
        try:
            weekly.build_weekly_draft(date(2026, 9, 30), db, Path(tmp) / "c", Path(tmp) / "ch")
            raise AssertionError("built a week without its final day")
        except ValueError as e:
            assert "2026-10-04" in str(e)
        assert not (Path(tmp) / "c").exists() and not (Path(tmp) / "ch").exists()
        # intact store: builds, and a second run without force refuses
        disk = sqlite3.connect(db)
        make_store().backup(disk)
        disk.close()
        post = weekly.build_weekly_draft(date(2026, 9, 30), db, Path(tmp) / "c", Path(tmp) / "ch")
        assert post.exists() and (Path(tmp) / "ch" / "weekly" / "2026-09-28.png").exists()
        try:
            weekly.build_weekly_draft(date(2026, 9, 30), db, Path(tmp) / "c", Path(tmp) / "ch")
            raise AssertionError("overwrote without force")
        except FileExistsError:
            pass


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
