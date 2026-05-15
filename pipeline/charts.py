"""
charts.py — Generate standard chart set for daily briefings.

Outputs PNG files to site/static/charts/ for embedding in blog posts.
Consistent styling across all charts for brand recognition.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date

from process import load_dam_data, get_day_data, daily_summary

# ─── Chart styling ──────────────────────────────────────────────
CHART_DIR = Path(__file__).parent.parent / "site" / "static" / "charts"
DATA_DIR = Path(__file__).parent.parent / "data"

# Consistent colour palette
COLORS = {
    "price": "#1a5276",       # deep blue — primary price line
    "price_fill": "#aed6f1",  # light blue — area fill under price
    "wind": "#27ae60",        # green — wind generation
    "demand": "#e67e22",      # orange — demand
    "peak": "#e74c3c",        # red — peak marker
    "min": "#2ecc71",         # green — min marker
    "grid": "#ecf0f1",        # light grey — gridlines
    "text": "#2c3e50",        # dark grey — text
    "bg": "#ffffff",          # white background
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.facecolor": COLORS["bg"],
    "figure.facecolor": COLORS["bg"],
    "axes.grid": True,
    "grid.color": COLORS["grid"],
    "grid.alpha": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def _format_time_axis(ax):
    """Standard x-axis formatting for half-hourly data."""
    ax.set_xlabel("")
    ax.set_xticks(range(0, 48, 4))
    ax.set_xticklabels([
        f"{(i // 2):02d}:{(i % 2) * 30:02d}" for i in range(0, 48, 4)
    ], rotation=45, ha="right")


def chart_dam_price_profile(day_df: pd.DataFrame, summary: dict, outpath: Path):
    """
    Primary daily chart: DAM price profile with peak/min markers.
    This is the hero chart for every daily briefing.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    periods = day_df["Period"].values
    prices = day_df["DAMPrice_EUR_MWh"].values

    # Price line and fill
    ax.plot(periods - 1, prices, color=COLORS["price"], linewidth=2, zorder=3)
    ax.fill_between(periods - 1, prices, alpha=0.15, color=COLORS["price_fill"], zorder=2)

    # Peak and min markers
    peak_idx = summary["peak_period"] - 1
    min_idx = summary["min_period"] - 1
    ax.scatter(peak_idx, summary["peak_price"], color=COLORS["peak"],
               s=80, zorder=5, label=f"Peak: €{summary['peak_price']}/MWh ({summary['peak_time']})")
    ax.scatter(min_idx, summary["min_price"], color=COLORS["min"],
               s=80, zorder=5, label=f"Min: €{summary['min_price']}/MWh ({summary['min_time']})")

    # Mean price line
    ax.axhline(summary["mean_price"], color=COLORS["text"], linestyle="--",
               alpha=0.4, linewidth=1, label=f"Mean: €{summary['mean_price']}/MWh")

    _format_time_axis(ax)
    ax.set_ylabel("€/MWh", fontsize=12, color=COLORS["text"])
    ax.set_title(f"I-SEM Day-Ahead Price — {summary['date']}", fontsize=14,
                 fontweight="bold", color=COLORS["text"], pad=15)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("€%.0f"))

    fig.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def chart_price_vs_wind(day_df: pd.DataFrame, summary: dict, outpath: Path):
    """
    Secondary chart: price overlaid with wind generation %.
    Shows the inverse relationship clearly.
    """
    if "WindGeneration_pct" not in day_df.columns:
        print("  Skipped price-vs-wind (no wind data)")
        return

    fig, ax1 = plt.subplots(figsize=(10, 5))

    periods = day_df["Period"].values - 1
    prices = day_df["DAMPrice_EUR_MWh"].values
    wind = day_df["WindGeneration_pct"].values

    # Price on left axis
    ax1.plot(periods, prices, color=COLORS["price"], linewidth=2, label="DAM Price")
    ax1.set_ylabel("€/MWh", color=COLORS["price"], fontsize=12)
    ax1.tick_params(axis="y", labelcolor=COLORS["price"])
    ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("€%.0f"))

    # Wind on right axis
    ax2 = ax1.twinx()
    ax2.fill_between(periods, wind, alpha=0.25, color=COLORS["wind"])
    ax2.plot(periods, wind, color=COLORS["wind"], linewidth=1.5, alpha=0.8, label="Wind %")
    ax2.set_ylabel("Wind Generation %", color=COLORS["wind"], fontsize=12)
    ax2.tick_params(axis="y", labelcolor=COLORS["wind"])
    ax2.set_ylim(0, 100)

    _format_time_axis(ax1)
    ax1.set_title(f"Price vs Wind — {summary['date']}", fontsize=14,
                  fontweight="bold", color=COLORS["text"], pad=15)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)

    fig.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def chart_week_comparison(df: pd.DataFrame, target_date: date, outpath: Path):
    """
    Comparison chart: overlay the last 7 days of DAM prices.
    Option 5 benchmarking element — shows how today compares to recent days.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    dates_available = sorted(df["DeliveryDate"].dt.date.unique())
    target_idx = dates_available.index(target_date) if target_date in dates_available else -1

    if target_idx < 0:
        print("  Skipped week comparison (target date not in data)")
        return

    # Get up to 7 most recent days up to and including target
    recent_dates = dates_available[max(0, target_idx - 6):target_idx + 1]

    cmap = plt.cm.Blues(np.linspace(0.3, 1.0, len(recent_dates)))

    for i, d in enumerate(recent_dates):
        day = df[df["DeliveryDate"].dt.date == d]
        alpha = 0.4 if d != target_date else 1.0
        lw = 1 if d != target_date else 2.5
        ax.plot(day["Period"].values - 1, day["DAMPrice_EUR_MWh"].values,
                color=cmap[i], alpha=alpha, linewidth=lw, label=str(d))

    _format_time_axis(ax)
    ax.set_ylabel("€/MWh", fontsize=12, color=COLORS["text"])
    ax.set_title(f"7-Day Price Comparison — week ending {target_date}",
                 fontsize=14, fontweight="bold", color=COLORS["text"], pad=15)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("€%.0f"))

    fig.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def generate_daily_charts(data_filepath: Path, target_date: date):
    """
    Master function: generate all charts for a given day.
    Call this from the command line or from scaffold.py.
    """
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    date_str = target_date.isoformat()

    df = load_dam_data(data_filepath)
    day_df = get_day_data(data_filepath, target_date)
    summary = daily_summary(df, target_date)

    print(f"\nGenerating charts for {date_str}...")

    chart_dam_price_profile(
        day_df, summary,
        CHART_DIR / f"dam-{date_str}.png"
    )
    chart_price_vs_wind(
        day_df, summary,
        CHART_DIR / f"price-wind-{date_str}.png"
    )
    chart_week_comparison(
        df, target_date,
        CHART_DIR / f"week-compare-{date_str}.png"
    )

    return summary


if __name__ == "__main__":
    raw = DATA_DIR / "semo_dam_raw.csv"
    sample = DATA_DIR / "semo_dam_sample.csv"
    data_file = raw if raw.exists() else sample
    if not data_file.exists():
        print("No data file found — download semo_dam_raw.csv or run generate_sample_data.py")
        raise SystemExit(1)

    df = load_dam_data(data_file)
    target = df["DeliveryDate"].dt.date.iloc[0]
    generate_daily_charts(data_file, target)
