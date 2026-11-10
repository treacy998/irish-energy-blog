"""Tests for weekly_chart / build_weekly_post / weekly.py on a synthetic in-memory store.
Run: python pipeline/test_weekly_post.py   (writes only under a temp directory)"""

import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import weekly
from charts import weekly_chart
from scaffold import build_weekly_post, weekly_verdict_text
from weekly_stats import verdict_sentence
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
    assert text.index("dearest of the last") < text.index("Inside the recent range")
    assert verdict_sentence(t) in text and "Against the previous" not in text


def test_verdict_sentence_bands():
    base = {"verdict_price": "normal", "n": 13}
    cases = {20.0: "at the bottom end", 35.0: "at the bottom end", 35.1: "mid-range", 64.9: "mid-range",
             65.0: "at the top end", 80.0: "at the top end"}
    for pct, where in cases.items():
        assert verdict_sentence({**base, "percentile": pct}) == f"Inside the recent range, {where}.", pct
    # outside 20-80 the existing wording stays, after the rank sentence
    assert verdict_sentence({"verdict_price": "dearer", "n": 13, "percentile": 85}) == "Against the previous 13 weeks: dearer."
    assert verdict_sentence({"verdict_price": "unusually cheaper", "n": 13, "percentile": 2}) == \
        "Against the previous 13 weeks: unusually cheaper."


def _scaled_store(week_start: date, factor: float, old_week: date | None = None, old_factor: float = 1.0):
    """make_store() with the week starting week_start scaled by factor, and optionally one earlier week scaled
    by old_factor: the dearest/cheapest edges the opening sentence has to word."""
    conn = make_store()
    def scale(start, f):
        conn.execute("UPDATE market_prices SET dam_price_eur_mwh = dam_price_eur_mwh * ? WHERE date BETWEEN ? AND ?",
                     (f, start.isoformat(), (start + timedelta(days=6)).isoformat()))
    scale(week_start, factor)
    if old_week:
        scale(old_week, old_factor)
    return conn


def test_dearest_week_names_the_last_equally_dear_week():
    old = date(2026, 3, 2)                                    # outside the 13 trailing weeks
    s = weekly_summary(date(2026, 9, 28), _scaled_store(date(2026, 9, 28), 3, old, 6))
    t = s["trailing"]
    assert t["rank"] == 1 and t["dearest_since"] == "2026-03-02", t
    text = weekly_verdict_text(s)
    assert text.startswith("Dearest of the last 14 weeks; dearest week since the week of 2 Mar."), text
    assert "last dearer" not in text and "no earlier week" not in text and "cheapest" not in text.lower()


def test_dearest_week_in_the_record_says_where_the_record_starts():
    s = weekly_summary(date(2026, 9, 28), _scaled_store(date(2026, 9, 28), 6))
    t = s["trailing"]
    assert t["rank"] == 1 and t["dearest_since"] is None and t["record_start"] == "2025-10-13", t
    assert weekly_verdict_text(s).startswith(
        "Dearest of the last 14 weeks; dearest week in the record (since 13 Oct 2025)."), weekly_verdict_text(s)


def test_cheapest_week_mirrors_it():
    old = date(2026, 3, 2)
    s = weekly_summary(date(2026, 9, 28), _scaled_store(date(2026, 9, 28), 0.2, old, 0.1))
    t = s["trailing"]
    assert t["rank"] == t["rank_of"] == 14 and t["cheapest_since"] == "2026-03-02", t
    assert weekly_verdict_text(s).startswith("Cheapest of the last 14 weeks; cheapest week since the week of 2 Mar."), \
        weekly_verdict_text(s)
    s = weekly_summary(date(2026, 9, 28), _scaled_store(date(2026, 9, 28), 0.1))
    assert s["trailing"]["cheapest_since"] is None
    assert weekly_verdict_text(s).startswith(
        "Cheapest of the last 14 weeks; cheapest week in the record (since 13 Oct 2025)."), weekly_verdict_text(s)


def test_a_middling_week_keeps_the_last_dearer_tail():
    text = weekly_verdict_text(weekly_summary(date(2026, 9, 28), make_store()))
    assert "dearest of the last 14 weeks; last dearer: week of" in text and "in the record" not in text


def test_year_on_year_leads_when_the_seasonal_baseline_is_usable():
    s = weekly_summary(date(2026, 10, 19), make_store())
    assert s["seasonal"] and s["seasonal"]["n"] >= 4
    ly = s["same_week_last_year"]["mean"]
    lead = f"{s['week_mean_c_per_kwh']:.2f} c/kWh, {s['week_mean'] / ly:.1f}x the same week last year ({ly / 10:.2f} c/kWh)."
    text = weekly_verdict_text(s)
    assert text.startswith(lead + " "), text
    # the trailing sentence follows, unchanged
    rest = text[len(lead) + 1:]
    assert "dearest of the last 14 weeks" in rest and verdict_sentence(s["trailing"]) in rest, rest
    assert text.index(lead) < text.index("dearest of the last") < text.index(verdict_sentence(s["trailing"]))


def test_year_on_year_wording_and_ratio_rounding():
    from weekly_stats import year_on_year_sentence
    base = {"seasonal": {"suppressed": False}, "week_mean_c_per_kwh": 41.57, "week_mean": 415.7,
            "same_week_last_year": {"week_start": "2025-11-03", "mean": 140.57}}
    assert year_on_year_sentence(base) == "41.57 c/kWh, 3.0x the same week last year (14.06 c/kWh)."
    assert year_on_year_sentence({**base, "week_mean": 198.48, "week_mean_c_per_kwh": 19.85,
                                  "same_week_last_year": {"week_start": "x", "mean": 97.88}}) == \
        "19.85 c/kWh, 2.0x the same week last year (9.79 c/kWh)."
    assert year_on_year_sentence({**base, "week_mean": 50.0, "week_mean_c_per_kwh": 5.0}) == \
        "5.00 c/kWh, 0.4x the same week last year (14.06 c/kWh)."


def test_year_on_year_is_absent_while_the_seasonal_baseline_is_suppressed():
    from weekly_stats import year_on_year_sentence
    for ws in (date(2026, 9, 28), date(2026, 10, 12)):          # seasonal n = 1 and 3: "need 4"
        s = weekly_summary(ws, make_store())
        assert s["seasonal"] is None
        assert year_on_year_sentence(s) is None and "same week last year" not in weekly_verdict_text(s)
    full = weekly_summary(date(2026, 10, 26), make_store(last=date(2026, 11, 8)))
    assert full["seasonal"]["n"] == 5 and full["same_week_last_year"]["week_start"] == "2025-10-27"
    conn = make_store(last=date(2026, 11, 8))                   # n = 4, but last year's own week is incomplete
    conn.execute("DELETE FROM market_prices WHERE date = '2025-10-29'")
    s = weekly_summary(date(2026, 10, 26), conn)
    assert s["seasonal"] and s["seasonal"]["n"] == 4 and s["same_week_last_year"] is None
    assert year_on_year_sentence(s) is None and "same week last year" not in weekly_verdict_text(s)


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
    # rank 1 no longer says "no earlier week in the store was as dear": it says where the record starts
    assert text.startswith("Dearest of the last 14 weeks; dearest week in the record (since 13 Oct 2025).")


def test_post_contents_order_and_rules():
    s = weekly_summary(date(2026, 9, 28), make_store())
    with tempfile.TemporaryDirectory() as tmp:
        post = build_weekly_post(s, Path(tmp))
        md = post.read_text()
        assert post == Path(tmp) / "weekly" / "2026-10-04" / "index.md"
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


def _disk_store(tmp: Path) -> Path:
    import sqlite3
    db = tmp / "h.db"
    disk = sqlite3.connect(db)
    make_store().backup(disk)
    disk.execute("UPDATE system_conditions SET wind_pct = 20.0 WHERE date BETWEEN '2026-09-28' AND '2026-10-04'")
    disk.commit()
    disk.close()
    return db


def test_week_gaps_prices_and_demand():
    import sqlite3
    with tempfile.TemporaryDirectory() as tmp:
        db = _disk_store(Path(tmp))
        assert weekly.week_gaps(db, date(2026, 9, 28)) == []
        c = sqlite3.connect(db)
        c.execute("DELETE FROM market_prices WHERE date = '2026-10-04'")
        c.execute("UPDATE system_conditions SET wind_pct = NULL WHERE date = '2026-10-02'")
        c.commit(); c.close()
        gaps = weekly.week_gaps(db, date(2026, 9, 28))
        assert len(gaps) == 2 and "2026-10-02 demand 0/36" in gaps[0] and "2026-10-04 prices 0/48" in gaps[1], gaps


def test_ensure_week_current_retries_bounded_and_rechecks():
    import sqlite3
    with tempfile.TemporaryDirectory() as tmp:
        db = _disk_store(Path(tmp))
        c = sqlite3.connect(db)
        c.execute("UPDATE system_conditions SET wind_pct = NULL WHERE date = '2026-10-04'")
        c.commit(); c.close()
        calls = []

        def never(_db):
            calls.append(1)
            return 1
        assert weekly.ensure_week_current(db, date(2026, 9, 28), refresh=never, attempts=3, wait_s=0)
        assert len(calls) == 3, "bounded at 3 attempts"

        calls.clear()

        def heals_on_second(_db):
            calls.append(1)
            if len(calls) == 2:
                c = sqlite3.connect(db)
                c.execute("UPDATE system_conditions SET wind_pct = 20.0 WHERE date = '2026-10-04'")
                c.commit(); c.close()
            return 0
        assert weekly.ensure_week_current(db, date(2026, 9, 28), refresh=heals_on_second, attempts=3, wait_s=0) == []
        assert len(calls) == 2, "stops as soon as the week is clean"

        calls.clear()
        assert weekly.ensure_week_current(db, date(2026, 9, 28), refresh=never, attempts=3, wait_s=0) == []
        assert not calls, "a clean week is never refreshed"


def test_refresh_does_not_relax_the_completeness_check():
    import sqlite3
    with tempfile.TemporaryDirectory() as tmp:
        db = _disk_store(Path(tmp))
        c = sqlite3.connect(db)
        c.execute("DELETE FROM market_prices WHERE date = '2026-10-04'")
        c.commit(); c.close()
        remaining = weekly.ensure_week_current(db, date(2026, 9, 28), refresh=lambda _d: 0, attempts=2, wait_s=0)
        assert remaining
        try:
            weekly.build_weekly_draft(date(2026, 9, 30), db, Path(tmp) / "c", Path(tmp) / "ch")
            raise AssertionError("built a week whose final day is short")
        except ValueError as e:
            assert "2026-10-04" in str(e)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
