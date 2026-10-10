"""Tests for the weekly-post audit: exact rank/count fields by default, unverified commentary numbers.
Run: python pipeline/test_audit_weekly.py   (temp directory only; synthetic in-memory store)"""

import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "audit"))
import audit_posts
from scaffold import build_weekly_post
from test_weekly_stats import make_store
from weekly_stats import weekly_summary

WEEK = date(2026, 9, 28)


def make_post(tmp: Path):
    summary = weekly_summary(WEEK, make_store())
    path = build_weekly_post(summary, tmp)
    return path, summary, audit_posts.weekly_ground_truth(summary)


def flags(rows):
    return [(r[1], r[2], r[3], r[4]) for r in rows if r[-1]]      # (field, published, computed, note)


def test_clean_generated_post_has_no_flags():
    with tempfile.TemporaryDirectory() as t:
        path, _, gt = make_post(Path(t))
        assert flags(audit_posts.audit_weekly_post(path, gt)) == []


def test_corrupted_rank_is_flagged_without_exact():
    with tempfile.TemporaryDirectory() as t:
        path, summary, gt = make_post(Path(t))
        rank = summary["trailing"]["rank"]
        text = path.read_text()
        bad = text.replace(f"| {rank} of {summary['trailing']['rank_of']} |", f"| {rank + 1} of {summary['trailing']['rank_of']} |")
        assert bad != text
        path.write_text(bad)
        got = flags(audit_posts.audit_weekly_post(path, gt))            # no exact argument
        assert [(f, p, c) for f, p, c, _ in got] == [("trailing_rank", float(rank + 1), rank)], got
        # the old default (tolerance 1.0) let exactly this through
        assert flags(audit_posts.audit_weekly_post(path, gt, exact=False)) == []


def test_off_by_one_count_and_wrong_since_date_are_flagged():
    with tempfile.TemporaryDirectory() as t:
        path, summary, gt = make_post(Path(t))
        n150 = summary["periods_above_150"]
        text = path.read_text().replace(f"| {n150} of", f"| {n150 + 1} of")
        since = summary["trailing"]["dearest_since"]
        text = text.replace(f"| {since} |", "| 2026-01-01 |")
        path.write_text(text)
        fields = {f for f, *_ in flags(audit_posts.audit_weekly_post(path, gt))}
        assert {"periods_above_150", "trailing_dearest_since"} <= fields, fields


def test_corrupted_rank_in_the_opening_sentence_is_flagged():
    with tempfile.TemporaryDirectory() as t:
        path, summary, gt = make_post(Path(t))
        tr = summary["trailing"]
        from weekly_stats import ordinal
        path.write_text(path.read_text().replace(f"{ordinal(tr['rank'])} dearest of the last",
                                                  f"{ordinal(tr['rank'] + 1)} dearest of the last"))
        assert "trailing_rank" in {f for f, *_ in flags(audit_posts.audit_weekly_post(path, gt))}


def with_commentary(path: Path, body: str) -> None:
    text = path.read_text()
    start = text.index("## Commentary")
    end = text.index("## Methodology")
    path.write_text(text[:start] + "## Commentary\n\n" + body + "\n\n" + text[end:])


def unverified(path: Path, summary: dict, gt: dict) -> list:
    rows = audit_posts.audit_weekly_post(path, gt, summary=summary)
    return [(r[2], r[5]) for r in rows if r[-1] == "unverified_commentary_number"]


def test_invented_commentary_numbers_are_flagged_and_real_ones_are_not():
    with tempfile.TemporaryDirectory() as t:
        path, summary, gt = make_post(Path(t))
        tr = summary["trailing"]
        from weekly_stats import ordinal
        mean, c = summary["week_mean"], summary["week_mean_c_per_kwh"]
        wind = summary["wind_mw_mean"]
        body = (
            f"At {c} c/kWh (€{mean}/MWh) this was the {ordinal(tr['rank'])} dearest of the last {tr['rank_of']} weeks, "
            f"since the week of {tr['dearest_since']}. Wind averaged {wind:.0f} MW, and {summary['periods_above_150']} "
            f"periods cleared above €150. The week ended on 4 October 2026, a Sunday, after Thursday 1 October.\n\n"
            f"Thursday peaked at €412.55/MWh and demand was 57% of capacity.\n"
        )
        with_commentary(path, body)
        got = unverified(path, summary, gt)
        assert [tok for tok, _ in got] == ["412.55", "57"], got
        # the first paragraph alone is clean
        with_commentary(path, body.split("\n\n")[0])
        assert unverified(path, summary, gt) == []


def test_commentary_precision_and_exemptions():
    with tempfile.TemporaryDirectory() as t:
        path, summary, gt = make_post(Path(t))
        mean = summary["week_mean"]
        wrong_precision = f"{mean + 0.01:.2f}"
        body = (f"Mean €{mean:,.2f} and {mean:.0f} and {mean:.1f}; not {wrong_precision}. "
                "See [the comparison](/compare?x=99) and 2026 vs 2025, the 5th, 3rd October, October 7.\n"
                "<!-- 12345 is a note to self -->\n")
        with_commentary(path, body)
        assert [tok for tok, _ in unverified(path, summary, gt)] == [wrong_precision]


def test_numbers_outside_the_commentary_section_are_not_this_checks_business():
    with tempfile.TemporaryDirectory() as t:
        path, summary, gt = make_post(Path(t))
        with_commentary(path, "No figures here.")
        assert unverified(path, summary, gt) == []
        assert audit_posts.commentary_numbers("## Other\n\nInvented 999 here.\n") == []


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
