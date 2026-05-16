"""
charts.py — Generate standard chart set for daily briefings.

Outputs PNG files to site/static/charts/ for embedding in blog posts.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date

from process import load_dam_data, get_day_data, daily_summary

# ── Palette ────────────────────────────────────────────────────────────────
BG         = "#0D1B2A"   # figure background — deep navy
PANEL      = "#112236"   # axes background — slightly lighter
PRICE_LINE = "#2EC4B6"   # teal — main price series
PRICE_FILL = "#1A6B65"   # dark teal — area fill under price
PEAK_COLOR = "#FFB703"   # amber — peak annotation
MIN_COLOR  = "#E63946"   # red — minimum annotation
MEAN_LINE  = "#FFFFFF"   # white — mean reference line
WIND_LINE  = "#7FB069"   # green — wind % series
WIND_FILL  = "#3D6B38"   # dark green — wind area fill
HIST_LINE  = "#85B7EB"   # pale blue — prior days in week-compare
TEXT_PRI   = "#F0F4F8"   # primary text — titles
TEXT_SEC   = "#8BA3BE"   # secondary text — axis labels
GRID       = "#1A2F47"   # grid lines
BORDER     = "#1E3450"   # spine colour

FIG_W = 12
FIG_H = 4.8
DPI   = 150

CHART_DIR = Path(__file__).parent.parent / "site" / "static" / "charts"
DATA_DIR  = Path(__file__).parent.parent / "data"


# ── Style helpers ──────────────────────────────────────────────────────────

def _style(ax, fig):
    """Apply dark navy style to an axes."""
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXT_SEC, labelsize=8.5)
    ax.xaxis.label.set_color(TEXT_SEC)
    ax.yaxis.label.set_color(TEXT_SEC)
    for spine in ax.spines.values():
        spine.set_color(BORDER)
        spine.set_linewidth(0.5)
    ax.grid(True, color=GRID, linewidth=0.5, linestyle="--", alpha=0.8)
    ax.set_axisbelow(True)


def _header(fig, title, subtitle):
    """Two-line header + site watermark on every chart."""
    fig.text(0.013, 0.97, title,    color=TEXT_PRI, fontsize=11,  fontweight="bold", va="top")
    fig.text(0.013, 0.87, subtitle, color=TEXT_SEC, fontsize=8.5, va="top")
    fig.text(0.988, 0.97, "inis.energy", color=TEXT_SEC, fontsize=7.5,
             va="top", ha="right", alpha=0.55)


def _format_time_axis(ax):
    """Standard x-axis formatting for half-hourly data (periods 0–47)."""
    ax.set_xlabel("")
    ax.set_xticks(range(0, 48, 4))
    ax.set_xticklabels(
        [f"{(i // 2):02d}:{(i % 2) * 30:02d}" for i in range(0, 48, 4)],
        rotation=45, ha="right", color=TEXT_SEC, fontsize=8,
    )


# ── Chart 1 — DAM price profile ────────────────────────────────────────────

def chart_dam_price_profile(day_df: pd.DataFrame, summary: dict, outpath: Path):
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    _style(ax, fig)

    x      = day_df["Period"].values - 1
    prices = day_df["DAMPrice_EUR_MWh"].values
    mean   = summary["mean_price"]

    ax.fill_between(x, prices, alpha=0.12, color=PRICE_FILL, zorder=1)
    ax.plot(x, prices, color=PRICE_LINE, linewidth=2.2, zorder=3)
    ax.axhline(mean, color=MEAN_LINE, linewidth=0.7, linestyle="--", alpha=0.35)

    peak_x = summary["peak_period"] - 1
    min_x  = summary["min_period"]  - 1

    ax.scatter([peak_x], [summary["peak_price"]], color=PEAK_COLOR, s=55, zorder=6)
    ax.annotate(
        f"Peak  €{summary['peak_price']:.0f}  ({summary['peak_time']})",
        xy=(peak_x, summary["peak_price"]),
        xytext=(0, 10), textcoords="offset points",
        color=PEAK_COLOR, fontsize=8.5, fontweight="bold", ha="center",
    )

    ax.scatter([min_x], [summary["min_price"]], color=MIN_COLOR, s=55, zorder=6)
    ax.annotate(
        f"Min  €{summary['min_price']:.0f}  ({summary['min_time']})",
        xy=(min_x, summary["min_price"]),
        xytext=(0, -14), textcoords="offset points",
        color=MIN_COLOR, fontsize=8.5, ha="center",
    )

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v:.0f}"))
    _format_time_axis(ax)

    _header(
        fig,
        f"I-SEM Day-Ahead Market — {summary['date']}",
        "Half-hourly DAM clearing prices  |  €/MWh  |  Irish time",
    )

    plt.tight_layout(rect=[0, 0, 1, 0.86])
    fig.savefig(outpath, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  Saved: {outpath}")


# ── Chart 2 — Price vs Wind ────────────────────────────────────────────────

def chart_price_vs_wind(day_df: pd.DataFrame, summary: dict, outpath: Path):
    if "WindGeneration_pct" not in day_df.columns:
        print("  Skipped price-vs-wind (no wind data)")
        return

    fig, ax1 = plt.subplots(figsize=(FIG_W, FIG_H))
    _style(ax1, fig)

    x      = day_df["Period"].values - 1
    prices = day_df["DAMPrice_EUR_MWh"].values
    wind   = day_df["WindGeneration_pct"].values

    ax1.fill_between(x, prices, alpha=0.12, color=PRICE_FILL, zorder=1)
    ax1.plot(x, prices, color=PRICE_LINE, linewidth=2.2, zorder=3)
    ax1.tick_params(axis="y", colors=PRICE_LINE)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v:.0f}"))

    ax2 = ax1.twinx()
    ax2.fill_between(x, wind, alpha=0.10, color=WIND_FILL, zorder=1)
    ax2.plot(x, wind, color=WIND_LINE, linewidth=1.6, linestyle="--", zorder=3)
    ax2.tick_params(axis="y", colors=WIND_LINE, labelsize=8.5)
    ax2.set_ylim(0, 105)
    for spine in ax2.spines.values():
        spine.set_color(BORDER)
        spine.set_linewidth(0.5)

    _format_time_axis(ax1)

    _header(
        fig,
        f"Price vs Wind Generation — {summary['date']}",
        "DAM price (€/MWh, teal)  and  wind generation share (%, green dashed)",
    )

    plt.tight_layout(rect=[0, 0, 1, 0.86])
    fig.savefig(outpath, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  Saved: {outpath}")


# ── Chart 3 — Week comparison ──────────────────────────────────────────────

def chart_week_comparison(df: pd.DataFrame, target_date: date, outpath: Path):
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    _style(ax, fig)

    dates_available = sorted(df["DeliveryDate"].dt.date.unique())
    if target_date not in dates_available:
        print("  Skipped week comparison (target date not in data)")
        plt.close(fig)
        return

    target_idx   = dates_available.index(target_date)
    recent_dates = dates_available[max(0, target_idx - 6): target_idx + 1]
    n            = len(recent_dates)

    for i, d in enumerate(recent_dates):
        day = df[df["DeliveryDate"].dt.date == d]
        x   = day["Period"].values - 1
        y   = day["DAMPrice_EUR_MWh"].values

        if d == target_date:
            ax.fill_between(x, y, color=PRICE_FILL, alpha=0.09, zorder=1)
            ax.plot(x, y, color=PRICE_LINE, linewidth=2.4, zorder=3)
        else:
            alpha = 0.20 + 0.30 * (i / max(n - 1, 1))
            ax.plot(x, y, color=HIST_LINE, linewidth=0.9, alpha=alpha)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v:.0f}"))
    _format_time_axis(ax)

    _header(
        fig,
        f"Week in Context — {target_date}",
        "Last 7 days overlaid  |  today highlighted in teal  |  earlier days faded",
    )

    plt.tight_layout(rect=[0, 0, 1, 0.86])
    fig.savefig(outpath, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  Saved: {outpath}")


# ── Master function (called by scaffold.py) ────────────────────────────────

def _load_all_dam_data() -> pd.DataFrame:
    """Load and concatenate every real SEMO DAM file in data/ (excludes sample data)."""
    frames = []
    for p in sorted(DATA_DIR.glob("MarketResult_SEM-DA_*.csv")):
        try:
            frames.append(load_dam_data(p))
        except Exception as e:
            print(f"  Warning: skipped {p.name} ({e})")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True).drop_duplicates(
        subset=["DeliveryDate", "Period"]
    ).sort_values(["DeliveryDate", "Period"])


def generate_daily_charts(data_filepath: Path, target_date: date):
    """Generate all charts for a given day. Returns the daily summary dict."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    date_str = target_date.isoformat()

    df      = load_dam_data(data_filepath)
    day_df  = get_day_data(data_filepath, target_date)
    summary = daily_summary(df, target_date)

    print(f"\nGenerating charts for {date_str}...")

    chart_dam_price_profile(
        day_df, summary,
        CHART_DIR / f"dam-{date_str}.png",
    )
    chart_price_vs_wind(
        day_df, summary,
        CHART_DIR / f"price-wind-{date_str}.png",
    )

    # Combine all available data files so the week-compare has history
    combined = _load_all_dam_data()
    chart_week_comparison(
        combined if not combined.empty else df,
        target_date,
        CHART_DIR / f"week-compare-{date_str}.png",
    )

    return summary


# ── CLI convenience ────────────────────────────────────────────────────────

if __name__ == "__main__":
    raw    = DATA_DIR / "semo_dam_raw.csv"
    sample = DATA_DIR / "semo_dam_sample.csv"
    data_file = raw if raw.exists() else sample
    if not data_file.exists():
        print("No data file found — drop a SEMO CSV into data/ first.")
        raise SystemExit(1)

    df     = load_dam_data(data_file)
    target = df["DeliveryDate"].dt.date.iloc[0]
    generate_daily_charts(data_file, target)
