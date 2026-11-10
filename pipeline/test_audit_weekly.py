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


def test_verdict_sentence_is_audited_old_wording_flags():
    with tempfile.TemporaryDirectory() as t:
        path, summary, gt = make_post(Path(t))
        assert flags(audit_posts.audit_weekly_post(path, gt)) == []
        text = path.read_text()
        want = gt["trailing_verdict_sentence"]
        assert want in text
        path.write_text(text.replace(want, "Against the previous 13 weeks: normal."))
        got = flags(audit_posts.audit_weekly_post(path, gt))
        assert {f for f, *_ in got} == {"trailing_verdict_sentence"}
        assert got[0][1:3] == ("Against the previous 13 weeks: normal.", want)


def test_extremum_clause_is_audited_for_dearest_and_cheapest_weeks():
    from test_weekly_post import _scaled_store
    for factor, old_factor, word in ((3, 6, "dearest"), (0.2, 0.1, "cheapest")):
        with tempfile.TemporaryDirectory() as t:
            summary = weekly_summary(WEEK, _scaled_store(WEEK, factor, date(2026, 3, 2), old_factor))
            path = build_weekly_post(summary, Path(t))
            gt = audit_posts.weekly_ground_truth(summary)
            assert gt["trailing_extremum_clause"].startswith(f"{word} week since the week of 2 Mar")
            assert flags(audit_posts.audit_weekly_post(path, gt)) == [], word      # includes Cheapest-of rank parsing
            text = path.read_text()
            path.write_text(text.replace("the week of 2 Mar", "the week of 9 Mar"))
            got = {f for f, *_ in flags(audit_posts.audit_weekly_post(path, gt))}
            assert got == {"trailing_extremum_clause"}, got


def test_year_on_year_sentence_and_verdict_sentence_are_audited_from_the_shared_functions():
    from weekly_stats import verdict_sentence, year_on_year_sentence
    with tempfile.TemporaryDirectory() as t:
        summary = weekly_summary(date(2026, 10, 19), make_store())          # seasonal n = 4
        path = build_weekly_post(summary, Path(t))
        gt = audit_posts.weekly_ground_truth(summary)
        text = path.read_text()
        assert gt["year_on_year_sentence"] == year_on_year_sentence(summary) and year_on_year_sentence(summary) in text
        assert gt["trailing_verdict_sentence"] == verdict_sentence(summary["trailing"]) and verdict_sentence(summary["trailing"]) in text
        assert flags(audit_posts.audit_weekly_post(path, gt)) == []
        ratio = year_on_year_sentence(summary).split(", ")[1].split("x")[0]
        path.write_text(text.replace(f", {ratio}x the same", f", {float(ratio) + 0.1:.1f}x the same"))
        assert {f for f, *_ in flags(audit_posts.audit_weekly_post(path, gt))} == {"year_on_year_sentence"}
        path.write_text(text.replace(verdict_sentence(summary["trailing"]), "Against the previous 13 weeks: cheaper."))
        assert {f for f, *_ in flags(audit_posts.audit_weekly_post(path, gt))} == {"trailing_verdict_sentence"}
    with tempfile.TemporaryDirectory() as t:                               # n < 4: no lead, no ground truth
        summary = weekly_summary(WEEK, make_store())
        assert "year_on_year_sentence" not in audit_posts.weekly_ground_truth(summary)


def test_the_daily_means_table_and_the_week_mean_are_audited_to_the_cent():
    from test_weekly_stats import _set_day
    conn = make_store()
    _set_day(conn, "2026-09-29", 488.45, 488.61)
    summary = weekly_summary(WEEK, conn)
    gt = audit_posts.weekly_ground_truth(summary)
    assert gt["daily_c_per_kwh[Tue 29 Sep]"] == 48.85 and gt["daily_eur_mwh[Tue 29 Sep]"] == 488.45
    with tempfile.TemporaryDirectory() as t:
        path = build_weekly_post(summary, Path(t))
        assert flags(audit_posts.audit_weekly_post(path, gt)) == []
        text = path.read_text()
        for old, new, field in (("| Tue 29 Sep | 48.85 |", "| Tue 29 Sep | 48.84 |", "daily_c_per_kwh[Tue 29 Sep]"),
                                ("| 488.45 |", "| 488.46 |", "daily_eur_mwh[Tue 29 Sep]"),
                                (f"| Week mean (c/kWh) | {summary['week_mean_c_per_kwh']} |",
                                 f"| Week mean (c/kWh) | {summary['week_mean_c_per_kwh'] + 0.5} |", "week_mean_c_per_kwh")):
            assert old in text, old
            path.write_text(text.replace(old, new, 1))
            got = flags(audit_posts.audit_weekly_post(path, gt))
            assert [f for f, *_ in got] == [field], (field, got)             # a cent (or half a c/kWh) out is a flag now


def test_commentary_accepts_the_correctly_rounded_daily_mean_and_rejects_the_double_rounded_one():
    from test_weekly_stats import _set_day
    conn = make_store()
    _set_day(conn, "2026-09-29", 488.45, 488.61)
    summary = weekly_summary(WEEK, conn)
    figs = audit_posts.summary_figures(summary)
    assert audit_posts._matches_at_precision("48.85", figs)
    assert not audit_posts._matches_at_precision("48.84", figs)              # 48.845 is no longer derived from 488.45
    assert audit_posts._matches_at_precision("488.45", figs)


def test_empty_section_flag():
    fm = "---\ntitle: x\ndraft: false\n---\n\n"
    broker = ("## Broker Takeaway\n\n<!-- hint\nspanning lines -->\n\n"
              "**Renewing:**\n\n**On variable:**\n\n**Already fixed:**\n\n")
    got = audit_posts.empty_sections(fm + "## Price Profile\n\ntext\n\n" + broker + "## Commentary\n\nwords\n")
    assert [h for h, _ in got] == ["Broker Takeaway"]
    assert audit_posts.empty_sections(fm + "## Commentary\n\n<!-- note -->\n\n## Methodology\n\nbody\n") == \
        [("Commentary", 6)]
    # a label with content is not empty; a trailing empty heading at EOF is
    assert audit_posts.empty_sections(fm + "## Broker Takeaway\n\n**Renewing:** call now\n\n**On variable:**\n") == []
    assert [h for h, _ in audit_posts.empty_sections(fm + "## Last\n")] == ["Last"]
    # the weekly Commentary placeholder is exempt only while draft: true
    draft = "---\ntitle: x\ndraft: true\n---\n\n## Commentary\n\n<!-- todo -->\n\n## Methodology\n\nbody\n"
    assert audit_posts.empty_sections(draft) == []
    assert [h for h, _ in audit_posts.empty_sections(draft.replace("draft: true", "draft: false"))] == ["Commentary"]
    assert [h for h, _ in audit_posts.empty_sections(draft.replace("Commentary", "Other"))] == ["Other"]


def test_generated_weekly_draft_has_no_empty_section_flag():
    with tempfile.TemporaryDirectory() as t:
        path, summary, gt = make_post(Path(t))
        assert audit_posts.audit_empty_sections(path) == []


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
