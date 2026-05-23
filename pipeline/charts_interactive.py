"""
charts_interactive.py — Interactive Plotly HTML charts for local analysis.

Generates standalone HTML files alongside the PNGs. Open in a browser
to hover for exact values, zoom, pan, and toggle series.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Palette — mirrors the matplotlib palette in charts.py
PRICE_LINE = "#395e16"
PRICE_FILL = "rgba(57,94,22,0.12)"
PEAK_COLOR = "#B8722A"
MIN_COLOR  = "#A83C3C"
MEAN_LINE  = "#2A2520"
WIND_LINE  = "#7A6D5E"
WIND_FILL  = "rgba(122,109,94,0.12)"
BG         = "#FAFAF9"
PANEL      = "#F3F2EF"
TEXT_PRI   = "#1C1612"
TEXT_SEC   = "#78706A"
GRID       = "#E8E4DE"
HIST_COLORS = ["#C8C4BE", "#B8B2AA", "#A09690", "#887E78", "#6B6460"]


def _base_layout(title: str, subtitle: str) -> dict:
    return dict(
        title=dict(
            text=f"<b>{title}</b><br><sub>{subtitle}</sub>",
            font=dict(color=TEXT_PRI, size=14),
            x=0.01, xanchor="left",
        ),
        paper_bgcolor=BG,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT_SEC, size=11),
        xaxis=dict(gridcolor=GRID, gridwidth=0.5, linecolor="#D4CFC8"),
        yaxis=dict(gridcolor=GRID, gridwidth=0.5, linecolor="#D4CFC8", tickprefix="€"),
        legend=dict(bgcolor=BG, bordercolor="#D4CFC8", borderwidth=1),
        margin=dict(l=60, r=40, t=80, b=60),
        height=420,
    )


def _period_to_label(periods):
    # I-SEM period 1 = 23:00; each period is 30 min
    return [f"{((23*60 + (p-1)*30) % 1440) // 60:02d}:{((23*60 + (p-1)*30) % 1440) % 60:02d}" for p in periods]


def _full_day_categoryarray():
    """All 48 period labels in I-SEM day order (23:00 … 22:30)."""
    return _period_to_label(range(1, 49))


def _save(fig: go.Figure, outpath: Path):
    fig.write_html(str(outpath), include_plotlyjs="cdn", full_html=True)
    print(f"  Saved: {outpath}")


# ── Chart 1 — DAM price profile ────────────────────────────────────────────

def chart_dam_price_profile(day_df: pd.DataFrame, summary: dict, outpath: Path):
    x      = (day_df["Period"].values - 1).tolist()
    labels = _period_to_label(day_df["Period"].values)
    prices = day_df["DAMPrice_EUR_MWh"].values.tolist()
    mean   = summary["mean_price"]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=labels, y=prices,
        mode="lines",
        line=dict(color=PRICE_LINE, width=2.5),
        fill="tozeroy", fillcolor=PRICE_FILL,
        name="DAM Price",
        hovertemplate="%{x}  €%{y:.1f}/MWh<extra></extra>",
    ))

    fig.add_hline(
        y=mean, line_dash="dash", line_color=MEAN_LINE, line_width=1.2, opacity=0.65,
        annotation_text=f"avg €{mean:.0f}", annotation_position="right",
        annotation_font_color=MEAN_LINE,
    )

    peak_label = _period_to_label([summary["peak_period"]])[0]
    min_label  = _period_to_label([summary["min_period"]])[0]

    fig.add_trace(go.Scatter(
        x=[peak_label], y=[summary["peak_price"]],
        mode="markers+text",
        marker=dict(color=PEAK_COLOR, size=9),
        text=[f"Peak €{summary['peak_price']:.0f}"],
        textposition="top center",
        textfont=dict(color=PEAK_COLOR, size=10),
        name="Peak",
        hovertemplate=f"Peak  €{summary['peak_price']:.0f}  ({summary['peak_time']})<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=[min_label], y=[summary["min_price"]],
        mode="markers+text",
        marker=dict(color=MIN_COLOR, size=9),
        text=[f"Min €{summary['min_price']:.0f}"],
        textposition="bottom center",
        textfont=dict(color=MIN_COLOR, size=10),
        name="Min",
        hovertemplate=f"Min  €{summary['min_price']:.0f}  ({summary['min_time']})<extra></extra>",
    ))

    fig.update_layout(**_base_layout(
        f"I-SEM Day-Ahead Market — {summary['date']}",
        "Half-hourly DAM clearing prices  |  €/MWh  |  Irish time",
    ))
    fig.update_xaxes(categoryarray=_full_day_categoryarray(), categoryorder="array")
    _save(fig, outpath)


# ── Chart 2 — Price vs Wind ────────────────────────────────────────────────

def chart_price_vs_wind(day_df: pd.DataFrame, summary: dict, outpath: Path):
    if "WindGeneration_pct" not in day_df.columns or day_df["WindGeneration_pct"].isna().all():
        print("  Skipped interactive price-vs-wind (no wind data)")
        return

    labels = _period_to_label(day_df["Period"].values)
    prices = day_df["DAMPrice_EUR_MWh"].values.tolist()
    wind   = day_df["WindGeneration_pct"].values.tolist()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=labels, y=prices,
        mode="lines", line=dict(color=PRICE_LINE, width=2.5),
        fill="tozeroy", fillcolor=PRICE_FILL,
        name="DAM Price (€/MWh)",
        hovertemplate="%{x}  €%{y:.1f}/MWh<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=labels, y=wind,
        mode="lines", line=dict(color=WIND_LINE, width=2, dash="dash"),
        fill="tozeroy", fillcolor=WIND_FILL,
        name="Wind %",
        hovertemplate="%{x}  %{y:.1f}% wind<extra></extra>",
    ), secondary_y=True)

    layout = _base_layout(
        f"Price vs Wind Generation — {summary['date']}",
        "DAM price (€/MWh, green)  ·  wind share (%, brown dashed)  ·  Irish time",
    )
    layout.setdefault("yaxis", {}).update(title="€/MWh", gridcolor=GRID)
    layout["yaxis2"] = dict(title="Wind %", ticksuffix="%", range=[0, 105], gridcolor=GRID)
    fig.update_layout(**layout)
    fig.update_xaxes(categoryarray=_full_day_categoryarray(), categoryorder="array")
    _save(fig, outpath)


# ── Chart 3 — Week comparison ──────────────────────────────────────────────

def chart_week_comparison(df: pd.DataFrame, target_date: date, outpath: Path):
    dates_available = sorted(df["DeliveryDate"].dt.date.unique())
    if target_date not in dates_available:
        print("  Skipped interactive week comparison (target date not in data)")
        return

    target_idx   = dates_available.index(target_date)
    recent_dates = dates_available[max(0, target_idx - 6): target_idx + 1]

    fig = go.Figure()
    hist_idx = 0

    for d in recent_dates:
        day    = df[df["DeliveryDate"].dt.date == d]
        labels = _period_to_label(day["Period"].values)
        prices = day["DAMPrice_EUR_MWh"].values.tolist()

        if d == target_date:
            fig.add_trace(go.Scatter(
                x=labels, y=prices,
                mode="lines",
                line=dict(color=PRICE_LINE, width=2.8),
                fill="tozeroy", fillcolor=PRICE_FILL,
                name=f"{d.strftime('%a %d %b')}  ← today",
                hovertemplate=f"{d}  %{{x}}  €%{{y:.1f}}<extra></extra>",
            ))
        else:
            color = HIST_COLORS[min(hist_idx, len(HIST_COLORS) - 1)]
            fig.add_trace(go.Scatter(
                x=labels, y=prices,
                mode="lines",
                line=dict(color=color, width=0.9 + 0.25 * hist_idx),
                opacity=0.85,
                name=d.strftime("%a %d %b"),
                hovertemplate=f"{d}  %{{x}}  €%{{y:.1f}}<extra></extra>",
            ))
            hist_idx += 1

    fig.update_layout(**_base_layout(
        f"Week in Context — {target_date}",
        "Last 7 days overlaid  ·  today (green) vs prior days  ·  click legend to toggle",
    ))
    fig.update_xaxes(categoryarray=_full_day_categoryarray(), categoryorder="array")
    _save(fig, outpath)


# ── Chart 4 — Price Duration Curve ────────────────────────────────────────

def chart_price_duration(day_df: pd.DataFrame, date_str: str, outpath: Path):
    prices = day_df["DAMPrice_EUR_MWh"].dropna().values
    if len(prices) == 0:
        return
    sorted_prices = np.sort(prices)[::-1]
    ranks = list(range(1, len(sorted_prices) + 1))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ranks, y=sorted_prices.tolist(),
        marker_color=PRICE_LINE, marker_line_width=0, opacity=0.78,
        name="Price",
        hovertemplate="Rank %{x}  €%{y:.1f}/MWh<extra></extra>",
    ))

    for level in (100, 150, 200):
        fig.add_hline(
            y=level, line_dash="dash", line_color=PEAK_COLOR, line_width=1, opacity=0.8,
            annotation_text=f"€{level}", annotation_position="right",
            annotation_font_color=PEAK_COLOR,
        )

    fig.update_layout(**_base_layout(
        f"Price Duration Curve — {date_str}",
        "48 half-hourly periods ranked high to low  |  €/MWh",
    ))
    fig.update_xaxes(title="Periods ranked high → low")
    _save(fig, outpath)


# ── Chart 5 — Peak / Off-Peak Spread ──────────────────────────────────────

def chart_spread_tracker(day_df: pd.DataFrame, date_str: str, outpath: Path):
    if "StartTime" not in day_df.columns:
        print("  Skipped interactive spread-tracker (no StartTime column)")
        return

    st = day_df["StartTime"]
    hours = st.dt.hour if pd.api.types.is_datetime64_any_dtype(st) else st.str[:2].astype(int)

    peak_mask     = (hours >= 7) & (hours < 22)
    peak_prices   = day_df.loc[peak_mask,  "DAMPrice_EUR_MWh"].dropna()
    offpeak_prices = day_df.loc[~peak_mask, "DAMPrice_EUR_MWh"].dropna()

    if peak_prices.empty or offpeak_prices.empty:
        return

    peak_mean    = peak_prices.mean()
    offpeak_mean = offpeak_prices.mean()
    spread       = peak_mean - offpeak_mean

    fig = go.Figure(go.Bar(
        x=[offpeak_mean, peak_mean],
        y=["Off-peak avg", "Peak avg"],
        orientation="h",
        marker_color=[WIND_LINE, PEAK_COLOR],
        opacity=0.85,
        text=[f"€{offpeak_mean:.0f}/MWh", f"€{peak_mean:.0f}/MWh"],
        textposition="outside",
        hovertemplate="%{y}  €%{x:.1f}/MWh<extra></extra>",
    ))

    fig.update_layout(**_base_layout(
        f"Peak / Off-Peak Spread — {date_str}",
        f"Spread €{spread:.0f}/MWh  |  Peak 07:00–22:00  |  Off-peak 22:00–07:00",
    ))
    fig.update_xaxes(tickprefix="€")
    _save(fig, outpath)


# ── Chart 6 — BESS Dispatch ───────────────────────────────────────────────

def chart_bess_dispatch(day_df: pd.DataFrame, bess_result: dict, date_str: str, outpath: Path):
    prices = day_df["DAMPrice_EUR_MWh"].values.tolist()
    labels = _period_to_label(day_df["Period"].values)
    c_idx  = bess_result["charge_periods"]
    d_idx  = bess_result["discharge_periods"]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=labels, y=prices,
        mode="lines", line=dict(color=PRICE_LINE, width=2),
        fill="tozeroy", fillcolor=PRICE_FILL,
        name="DAM Price",
        hovertemplate="%{x}  €%{y:.1f}/MWh<extra></extra>",
    ))

    fig.add_vrect(
        x0=labels[c_idx[0]], x1=labels[c_idx[-1]],
        fillcolor=WIND_LINE, opacity=0.25, line_width=0,
        annotation_text="Charge window", annotation_position="top left",
        annotation_font_color=WIND_LINE,
    )
    fig.add_vrect(
        x0=labels[d_idx[0]], x1=labels[d_idx[-1]],
        fillcolor=PEAK_COLOR, opacity=0.25, line_width=0,
        annotation_text="Discharge window", annotation_position="top right",
        annotation_font_color=PEAK_COLOR,
    )

    b = bess_result
    fig.update_layout(**_base_layout(
        f"BESS Dispatch Signal — {date_str}",
        f"Charge {b['charge_start']} €{b['charge_mean']:.0f}/MWh  ·  Discharge {b['discharge_start']} €{b['discharge_mean']:.0f}/MWh  ·  Gross profit €{b['gross_profit']:.0f}",
    ))
    fig.update_xaxes(categoryarray=_full_day_categoryarray(), categoryorder="array")
    _save(fig, outpath)


# ── Master function ────────────────────────────────────────────────────────

def generate_interactive_charts(day_df: pd.DataFrame, combined_df: pd.DataFrame,
                                 summary: dict, bess_result, target_date: date,
                                 chart_day_dir: Path):
    """Generate all interactive Plotly HTML charts into chart_day_dir."""
    date_str = target_date.isoformat()
    print(f"\nGenerating interactive charts for {date_str}...")

    chart_dam_price_profile(day_df, summary, chart_day_dir / f"dam-{date_str}.html")
    chart_price_vs_wind(day_df, summary,     chart_day_dir / f"price-wind-{date_str}.html")
    chart_week_comparison(combined_df if not combined_df.empty else day_df,
                          target_date, chart_day_dir / f"week-compare-{date_str}.html")
    chart_price_duration(day_df, date_str,   chart_day_dir / f"pdc-{date_str}.html")
    chart_spread_tracker(day_df, date_str,   chart_day_dir / f"spread-{date_str}.html")

    if bess_result is not None:
        chart_bess_dispatch(day_df, bess_result, date_str, chart_day_dir / f"bess-{date_str}.html")
