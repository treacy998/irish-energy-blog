"""Chart axis labels on 48-, 50- and 46-period days. Run: python pipeline/test_chart_labels.py (or pytest)."""

import sys
import tempfile
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import charts
import charts_interactive as ci
from trading_day import clock_change_note, expected_periods, period_keys, period_labels

LONG, SHORT, NORMAL = date(2026, 10, 25), date(2027, 3, 28), date(2026, 10, 24)


def day_df(d: date) -> pd.DataFrame:
    n = expected_periods(d)
    return pd.DataFrame({
        "DeliveryDate": [pd.Timestamp(d)] * n, "Period": range(1, n + 1),
        "DAMPrice_EUR_MWh": [50.0 + i for i in range(n)], "WindGeneration_pct": [40.0] * n,
    })


def summary(d: date, n: int) -> dict:
    return {"date": d.isoformat(), "mean_price": 60.0, "peak_period": n, "peak_price": 99.0, "peak_time": "x",
            "min_period": 1, "min_price": 1.0, "min_time": "x"}


def capture_figs(fn, *args) -> list:
    """Run an interactive chart function and return the figures it would have saved."""
    figs, saved = [], ci._save
    ci._save = lambda fig, outpath: figs.append(fig)
    try:
        fn(*args)
    finally:
        ci._save = saved
    return figs


def test_normal_day_labels_are_the_plain_23_to_2230_grid():
    old = [f"{((23*60 + i*30) % 1440) // 60:02d}:{((23*60 + i*30) % 1440) % 60:02d}" for i in range(48)]
    assert period_labels(NORMAL) == old and period_keys(NORMAL) == old


def test_long_day_repeats_0100_0130_and_ends_2230_with_unique_keys():
    labels, keys = period_labels(LONG), period_keys(LONG)
    assert len(labels) == 50 and labels[4:8] == ["01:00", "01:30", "01:00", "01:30"] and labels[-1] == "22:30"
    assert keys[4:8] == ["01:00", "01:30", "01:00 (2nd)", "01:30 (2nd)"]
    assert len(set(keys)) == 50 and keys[-1] == "22:30"


def test_short_day_has_46_labels_without_the_0100_hour_and_ends_2230():
    labels = period_labels(SHORT)
    assert len(labels) == 46 and labels[-1] == "22:30" and not any(x.startswith("01:") for x in labels)
    assert labels[3:6] == ["00:30", "02:00", "02:30"]


def test_clock_change_note_only_on_change_days():
    assert clock_change_note(NORMAL) == ""
    assert "twice" in clock_change_note(LONG) and "50" in clock_change_note(LONG)
    assert "does not occur" in clock_change_note(SHORT) and "46" in clock_change_note(SHORT)


def test_matplotlib_ticks_show_the_repeated_hour_twice():
    fig, ax = plt.subplots()
    charts._format_time_axis(ax, LONG)
    text = [t.get_text() for t in ax.get_xticklabels()]
    assert text.count("01:00") == 2 and text[0] == "23:00" and len(ax.get_xticks()) == len(text)
    plt.close(fig)
    fig, ax = plt.subplots()
    charts._format_time_axis(ax, NORMAL)
    assert list(ax.get_xticks()) == list(range(0, 48, 4))
    assert [t.get_text() for t in ax.get_xticklabels()][:3] == ["23:00", "01:00", "03:00"]
    plt.close(fig)


def test_matplotlib_dam_chart_renders_on_clock_change_days():
    for d in (LONG, SHORT, NORMAL):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dam.png"
            charts.chart_dam_price_profile(day_df(d), summary(d, expected_periods(d)), out)
            assert out.stat().st_size > 0


def test_interactive_long_day_axis_has_50_unique_categories_and_label_ticks():
    fig, = capture_figs(ci.chart_dam_price_profile, day_df(LONG), summary(LONG, 50), Path("x"))
    xa = fig.layout.xaxis
    assert len(xa.categoryarray) == 50 and len(set(xa.categoryarray)) == 50
    assert list(fig.data[0].x) == list(xa.categoryarray)
    assert list(xa.ticktext).count("01:00") == 2 and set(xa.tickvals) <= set(xa.categoryarray)
    assert "clocks go back" in fig.layout.title.text


def test_interactive_short_day_axis_has_46_categories_and_no_0100_hour():
    fig, = capture_figs(ci.chart_dam_price_profile, day_df(SHORT), summary(SHORT, 46), Path("x"))
    cats = list(fig.layout.xaxis.categoryarray)
    assert len(cats) == 46 and cats[-1] == "22:30" and not any(c.startswith("01:") for c in cats)
    assert fig.layout.xaxis.tickvals is None          # labels are already unique, so no tick override


def test_interactive_normal_day_axis_is_unchanged():
    fig, = capture_figs(ci.chart_dam_price_profile, day_df(NORMAL), summary(NORMAL, 48), Path("x"))
    assert list(fig.layout.xaxis.categoryarray) == period_labels(NORMAL) and fig.layout.xaxis.tickvals is None
    assert "clocks" not in fig.layout.title.text


def test_price_duration_subtitle_uses_the_actual_period_count():
    for d, n in ((LONG, 50), (SHORT, 46), (NORMAL, 48)):
        fig, = capture_figs(ci.chart_price_duration, day_df(d), d.isoformat(), Path("x"))
        assert f"{n} half-hourly periods" in fig.layout.title.text, d


def test_week_compare_aligns_prior_days_on_the_target_days_clock_labels():
    both = pd.concat([day_df(date(2026, 10, 24)), day_df(LONG)], ignore_index=True)
    figs = capture_figs(ci.chart_week_comparison, both, LONG, Path("x"))
    prior, today = figs[0].data
    assert len(prior.x) == 48 and set(prior.x) <= set(figs[0].layout.xaxis.categoryarray) and len(today.x) == 50
    # a long day among the prior days: its second pass of the repeated hour has no counterpart on a normal day
    both = pd.concat([day_df(LONG), day_df(date(2026, 10, 26))], ignore_index=True)
    prior, today = capture_figs(ci.chart_week_comparison, both, date(2026, 10, 26), Path("x"))[0].data
    assert len(prior.x) == 48 and len(today.x) == 48 and not any("(2nd)" in k for k in prior.x)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
