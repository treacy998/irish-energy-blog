"""Clock-change tests for trading_day. Run: python pipeline/test_trading_day.py (or pytest)."""

import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from trading_day import (
    expected_periods, period_label_indices, period_labels, period_start_utc,
    period_starts_utc, trading_day_start_utc,
)

UTC = timezone.utc


def test_expected_periods_from_zoneinfo():
    cases = {
        "2025-10-26": 50,   # clocks back
        "2026-03-29": 46,   # clocks forward
        "2026-10-25": 50,
        "2027-03-28": 46,
        "2026-10-24": 48,
        "2026-10-26": 48,
    }
    for ds, want in cases.items():
        assert expected_periods(date.fromisoformat(ds)) == want, ds


def test_day_start_is_local_2300_the_evening_before():
    # Facts read from real SEMOpx files: summer, autumn change, spring change.
    assert trading_day_start_utc(date(2026, 5, 4)) == datetime(2026, 5, 3, 22, 0, tzinfo=UTC)
    assert trading_day_start_utc(date(2025, 10, 26)) == datetime(2025, 10, 25, 22, 0, tzinfo=UTC)
    assert trading_day_start_utc(date(2026, 3, 29)) == datetime(2026, 3, 28, 23, 0, tzinfo=UTC)


def test_period_starts_are_30_minutes_apart_in_utc_and_end_at_next_day_start():
    for d in (date(2025, 10, 26), date(2026, 3, 29), date(2026, 7, 8)):
        starts = period_starts_utc(d)
        assert len(starts) == expected_periods(d)
        assert all((b - a).total_seconds() == 1800 for a, b in zip(starts, starts[1:]))
        assert starts[-1].timestamp() + 1800 == trading_day_start_utc(date.fromordinal(d.toordinal() + 1)).timestamp()


def test_long_day_repeats_0100_hour_and_labels_stay_distinguishable():
    d = date(2025, 10, 26)
    labels = period_labels(d)
    assert labels.count("01:00") == 2 and labels.count("01:30") == 2
    assert period_label_indices(d, "01:00") == [4, 6]
    assert period_start_utc(d, 5) != period_start_utc(d, 7)


def test_short_day_skips_0100_hour():
    labels = period_labels(date(2026, 3, 29))
    assert "01:00" not in labels and "01:30" not in labels


def test_period_out_of_range_raises():
    for d, bad in ((date(2026, 3, 29), 47), (date(2026, 7, 8), 49), (date(2025, 10, 26), 51), (date(2026, 7, 8), 0)):
        try:
            period_start_utc(d, bad)
        except ValueError:
            continue
        raise AssertionError((d, bad))


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
