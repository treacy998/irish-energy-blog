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


# ── Chart 4 — Price Duration Curve ────────────────────────────────────────

def chart_price_duration(df: pd.DataFrame, date_str: str, output_dir: Path):
    try:
        prices = df["DAMPrice_EUR_MWh"].dropna().values
        if len(prices) == 0:
            return None
        sorted_prices = np.sort(prices)[::-1]
        ranks = np.arange(1, len(sorted_prices) + 1)

        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        _style(ax, fig)

        ax.bar(ranks, sorted_prices, color=PRICE_LINE, alpha=0.72, width=0.85, zorder=3)

        for level in (100, 150, 200):
            ax.axhline(level, color=PEAK_COLOR, linewidth=0.9, linestyle="--", alpha=0.7, zorder=4)
            ax.text(48.8, level, f"€{level}", color=PEAK_COLOR, fontsize=7.5, va="center", ha="left")

        above_150 = int(np.sum(sorted_prices > 150))
        above_200 = int(np.sum(sorted_prices > 200))
        ax.text(0.97, 0.96, f"Above €150: {above_150}\nAbove €200: {above_200}",
                transform=ax.transAxes, color=TEXT_PRI, fontsize=8.5,
                va="top", ha="right",
                bbox=dict(facecolor=PANEL, edgecolor=BORDER, boxstyle="round,pad=0.4", alpha=0.9))

        ax.set_xlabel("Hours, ranked by price", color=TEXT_SEC, fontsize=8.5)
        ax.set_xlim(0.5, 50.5)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v:.0f}"))

        _header(fig,
                f"Price Duration Curve — {date_str}",
                "48 half-hourly periods ranked high to low  |  €/MWh")

        plt.tight_layout(rect=[0, 0, 1, 0.86])
        outpath = output_dir / f"pdc-{date_str}.png"
        fig.savefig(outpath, dpi=DPI, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"  Saved: {outpath}")
        return outpath
    except Exception as e:
        print(f"  Warning: price-duration chart failed ({e})")
        return None


# ── Chart 5 — Peak / Off-Peak Spread ──────────────────────────────────────

def chart_spread_tracker(df: pd.DataFrame, date_str: str, output_dir: Path):
    try:
        if "StartTime" not in df.columns:
            print("  Skipped spread-tracker (no StartTime column)")
            return None

        st = df["StartTime"]
        if pd.api.types.is_datetime64_any_dtype(st):
            hours = st.dt.hour
        else:
            hours = st.str[:2].astype(int)

        peak_mask = (hours >= 7) & (hours < 22)
        peak_prices   = df.loc[peak_mask,  "DAMPrice_EUR_MWh"].dropna()
        offpeak_prices = df.loc[~peak_mask, "DAMPrice_EUR_MWh"].dropna()

        if peak_prices.empty or offpeak_prices.empty:
            print("  Skipped spread-tracker (insufficient data)")
            return None

        peak_mean   = peak_prices.mean()
        offpeak_mean = offpeak_prices.mean()
        spread = peak_mean - offpeak_mean

        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        _style(ax, fig)

        y_pos  = [1, 0]
        values = [peak_mean, offpeak_mean]
        colors = [PEAK_COLOR, HIST_LINE]
        bars = ax.barh(y_pos, values, color=colors, alpha=0.82, height=0.45, zorder=3)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(["Peak avg", "Off-peak avg"], fontsize=10, color=TEXT_PRI)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v:.0f}"))

        max_val = max(peak_mean, offpeak_mean)

        # Value labels at end of each bar
        for bar, val in zip(bars, values):
            ax.text(val + max_val * 0.015,
                    bar.get_y() + bar.get_height() / 2,
                    f"€{val:.0f}/MWh", va="center", ha="left",
                    color=TEXT_PRI, fontsize=9, fontweight="bold")

        # Bracket connecting the inner edges of the two bars
        x_brk = max_val * 0.48
        ax.annotate("", xy=(x_brk, 0.225), xytext=(x_brk, 0.775),
                    arrowprops=dict(arrowstyle="<->", color=TEXT_SEC, lw=1.5))

        # Large spread value in the gap between bars
        ax.text(x_brk * 1.35, 0.5, f"€{spread:.0f}/MWh spread",
                va="center", ha="left", color=TEXT_PRI,
                fontsize=14, fontweight="bold",
                bbox=dict(facecolor=BG, edgecolor="none", alpha=0.75, pad=4))

        ax.set_ylim(-0.45, 1.72)
        ax.set_xlim(0, max_val * 1.4)

        _header(fig,
                f"Peak / Off-Peak Spread — {date_str}",
                "Peak: 07:00–22:00  |  Off-peak: 22:00–07:00  |  €/MWh")

        plt.tight_layout(rect=[0, 0, 1, 0.86])
        outpath = output_dir / f"spread-{date_str}.png"
        fig.savefig(outpath, dpi=DPI, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"  Saved: {outpath}")
        return outpath
    except Exception as e:
        print(f"  Warning: spread-tracker chart failed ({e})")
        return None


# ── Chart 6 — BESS Dispatch ───────────────────────────────────────────────

def chart_bess_dispatch(df: pd.DataFrame, bess_result: dict, date_str: str, output_dir: Path):
    try:
        prices = df["DAMPrice_EUR_MWh"].values
        x = np.arange(len(prices))

        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        _style(ax, fig)

        ax.fill_between(x, prices, alpha=0.10, color=PRICE_FILL, zorder=1)
        ax.plot(x, prices, color=PRICE_LINE, linewidth=2.0, zorder=3)

        # Shade charge window (blue)
        c_idx = bess_result["charge_periods"]
        ax.axvspan(c_idx[0] - 0.5, c_idx[-1] + 0.5, color=HIST_LINE, alpha=0.30, zorder=2)
        c_mid = (c_idx[0] + c_idx[-1]) / 2
        ax.text(c_mid, ax.get_ylim()[1] if ax.get_ylim()[1] != 1.0 else max(prices) * 0.95,
                "Charge\nwindow", color=HIST_LINE, fontsize=8, ha="center", va="top",
                fontweight="bold", zorder=5)

        # Shade discharge window (amber)
        d_idx = bess_result["discharge_periods"]
        ax.axvspan(d_idx[0] - 0.5, d_idx[-1] + 0.5, color=PEAK_COLOR, alpha=0.30, zorder=2)
        d_mid = (d_idx[0] + d_idx[-1]) / 2
        ax.text(d_mid, ax.get_ylim()[1] if ax.get_ylim()[1] != 1.0 else max(prices) * 0.95,
                "Discharge\nwindow", color=PEAK_COLOR, fontsize=8, ha="center", va="top",
                fontweight="bold", zorder=5)

        # Spread bracket on the right side
        c_price = bess_result["charge_mean"]
        d_price = bess_result["discharge_mean"]
        x_brk = 46.5
        ax.annotate("", xy=(x_brk, c_price), xytext=(x_brk, d_price),
                    arrowprops=dict(arrowstyle="<->", color=TEXT_SEC, lw=1.5))
        ax.text(x_brk + 0.4, (c_price + d_price) / 2,
                f"€{bess_result['spread']:.0f}\nspread",
                color=TEXT_PRI, fontsize=8.5, va="center", ha="left", fontweight="bold",
                bbox=dict(facecolor=BG, edgecolor="none", alpha=0.75, pad=3))

        ax.axhline(c_price, color=HIST_LINE, linewidth=0.7, linestyle=":", alpha=0.6)
        ax.axhline(d_price, color=PEAK_COLOR, linewidth=0.7, linestyle=":", alpha=0.6)

        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v:.0f}"))
        _format_time_axis(ax)

        _header(
            fig,
            f"BESS Dispatch Signal — {date_str}",
            f"Optimal 1MW/2MWh cycle  |  charge {bess_result['charge_start']} (blue)  |  discharge {bess_result['discharge_start']} (amber)  |  gross profit €{bess_result['gross_profit']:.0f}",
        )

        plt.tight_layout(rect=[0, 0, 1, 0.86])
        outpath = output_dir / f"bess-{date_str}.png"
        fig.savefig(outpath, dpi=DPI, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"  Saved: {outpath}")
        return outpath
    except Exception as e:
        print(f"  Warning: BESS dispatch chart failed ({e})")
        return None


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


def generate_daily_charts(data_filepath: Path, target_date: date, eirgrid_df=None, bess_result=None):
    """Generate all charts for a given day. Returns the daily summary dict."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    date_str = target_date.isoformat()

    df      = load_dam_data(data_filepath)
    day_df  = get_day_data(data_filepath, target_date)
    summary = daily_summary(df, target_date)

    if eirgrid_df is not None:
        eg = eirgrid_df.copy()
        eg["StartTime"] = eg["StartTime"].dt.strftime("%H:%M")
        wind_cols = ["StartTime", "WindMW", "DemandMW", "WindGeneration_pct"]
        day_df = pd.merge(day_df, eg[wind_cols], on="StartTime", how="left")
        if day_df["WindGeneration_pct"].notna().any():
            summary["wind_pct_mean"] = round(day_df["WindGeneration_pct"].mean(), 1)
            summary["demand_mean_mw"] = round(day_df["DemandMW"].mean(), 0)

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

    chart_price_duration(day_df, date_str, CHART_DIR)
    chart_spread_tracker(day_df, date_str, CHART_DIR)

    if bess_result is not None:
        chart_bess_dispatch(day_df, bess_result, date_str, CHART_DIR)

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
