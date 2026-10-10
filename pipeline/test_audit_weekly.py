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


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
