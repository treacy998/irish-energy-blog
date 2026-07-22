"""
weekly.py — Aggregate an ISO week of daily DAM/wind data into a populated
weekly-analysis draft.

Turns "write a weekly roundup" from a blank page into a review: pulls the
week's 7 days of price data (already on disk from the daily pipeline) and
wind/demand (re-fetched from EirGrid per day, same call the daily pipeline
uses), computes week-level stats, generates a chart, and writes a pre-filled
draft to site/content/weekly/<week-ending-date>.md — still gated behind
draft: true, still needs a human read before publishing.

Usage:
    python pipeline/weekly.py                 # most recently completed ISO week
    python pipeline/weekly.py 2026-07-12       # week containing this date (Mon-Sun)
"""

import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from bess import simulate_bess
from charts import _load_all_dam_data, chart_weekly_overview
from fetch import fetch_wind_and_demand
from process import daily_summary

CONTENT_DIR = Path(__file__).parent.parent / "site" / "content"
CHART_DIR = Path(__file__).parent.parent / "site" / "static" / "charts" / "weekly"


def iso_week_bounds(d: date) -> tuple[date, date]:
    """Return (Monday, Sunday) of the ISO week containing d."""
    monday = d - timedelta(days=d.weekday())
    return monday, monday + timedelta(days=6)


def load_week(monday: date, sunday: date) -> list[dict]:
    """Per-day summary (price + wind + BESS) for each day of the week found on disk."""
    all_df = _load_all_dam_data()
    days = []

    d = monday
    while d <= sunday:
        day_df = all_df[all_df["DeliveryDate"] == pd.Timestamp(d)].sort_values("Period")
        if day_df.empty:
            d += timedelta(days=1)
            continue

        summary = daily_summary(all_df, d)
        summary["date"] = d.isoformat()
        summary["weekday"] = d.strftime("%A")

        eirgrid_df = fetch_wind_and_demand(d)
        if eirgrid_df is not None:
            eg = eirgrid_df.copy()
            eg["StartTime"] = eg["StartTime"].dt.strftime("%H:%M")
            merged = day_df.merge(eg[["StartTime", "WindGeneration_pct"]], on="StartTime", how="left")
            if merged["WindGeneration_pct"].notna().any():
                summary["wind_pct_mean"] = round(float(merged["WindGeneration_pct"].mean()), 1)

        bess_result = simulate_bess(day_df)
        if bess_result:
            summary["bess_profit"] = bess_result["gross_profit"]

        days.append(summary)
        d += timedelta(days=1)

    return days


def aggregate_week(days: list[dict], prev_days: list[dict] | None = None) -> dict:
    """Week-level stats + three templated commentary bullets from the daily summaries."""
    if not days:
        raise ValueError("No daily data found for this week")

    means = [d["mean_price"] for d in days]
    peak_day = max(days, key=lambda d: d["peak_price"])
    trough_day = min(days, key=lambda d: d["min_price"])

    agg = {
        "week_mean": round(sum(means) / len(means), 2),
        "week_peak_price": peak_day["peak_price"],
        "week_peak_day": peak_day["weekday"],
        "week_peak_time": peak_day["peak_time"],
        "week_min_price": trough_day["min_price"],
        "week_min_day": trough_day["weekday"],
        "week_min_time": trough_day["min_time"],
        "daily_mean_std": round(pd.Series(means).std(), 2) if len(means) > 1 else 0.0,
        "total_bess_profit": round(sum(d.get("bess_profit", 0) for d in days), 2),
        "days_covered": len(days),
    }

    wind_days = [d for d in days if "wind_pct_mean" in d]
    if wind_days:
        agg["week_wind_mean"] = round(sum(d["wind_pct_mean"] for d in wind_days) / len(wind_days), 1)
        highest_wind = max(wind_days, key=lambda d: d["wind_pct_mean"])
        lowest_wind = min(wind_days, key=lambda d: d["wind_pct_mean"])
        agg["highest_wind_day"] = highest_wind["weekday"]
        agg["highest_wind_pct"] = highest_wind["wind_pct_mean"]
        agg["lowest_wind_day"] = lowest_wind["weekday"]
        agg["lowest_wind_pct"] = lowest_wind["wind_pct_mean"]
        if len(wind_days) > 2:
            corr = pd.Series([d["wind_pct_mean"] for d in wind_days]).corr(
                pd.Series([d["mean_price"] for d in wind_days])
            )
            agg["wind_price_corr"] = round(float(corr), 2) if corr == corr else None

    if prev_days:
        prev_mean = sum(d["mean_price"] for d in prev_days) / len(prev_days)
        if prev_mean:
            agg["wow_pct_change"] = round((agg["week_mean"] - prev_mean) / prev_mean * 100, 1)

    agg["takeaways"] = _build_takeaways(agg)
    return agg


def _build_takeaways(agg: dict) -> list[str]:
    """Three templated (not free-form) commentary bullets from the aggregate stats."""
    bullets = []

    spread = agg["week_peak_price"] - agg["week_min_price"]
    bullets.append(
        f"Price ranged from a €{agg['week_min_price']}/MWh low on {agg['week_min_day']} "
        f"({agg['week_min_time']}) to a €{agg['week_peak_price']}/MWh peak on "
        f"{agg['week_peak_day']} ({agg['week_peak_time']}) — a €{spread:.2f}/MWh spread across the week, "
        f"averaging €{agg['week_mean']}/MWh overall."
    )

    if "week_wind_mean" in agg:
        corr = agg.get("wind_price_corr")
        if corr is not None and corr <= -0.3:
            relationship = (
                f"the usual inverse relationship held — {agg['highest_wind_day']}'s "
                f"{agg['highest_wind_pct']}% wind coincided with cheaper power, while "
                f"{agg['lowest_wind_day']}'s {agg['lowest_wind_pct']}% wind ran the tightest"
            )
        elif corr is not None and corr >= 0.3:
            relationship = (
                f"wind didn't track price as cleanly as usual — {agg['highest_wind_day']} had the week's "
                f"highest wind ({agg['highest_wind_pct']}%) without the cheapest prices, "
                f"while {agg['lowest_wind_day']} saw the least wind ({agg['lowest_wind_pct']}%)"
            )
        else:
            relationship = (
                f"wind ranged from {agg['lowest_wind_pct']}% on {agg['lowest_wind_day']} to "
                f"{agg['highest_wind_pct']}% on {agg['highest_wind_day']}, without a clean read-through to price"
            )
        bullets.append(f"Average wind for the week was {agg['week_wind_mean']}% of demand — {relationship}.")

    if "wow_pct_change" in agg:
        direction = "up" if agg["wow_pct_change"] > 0 else "down"
        bullets.append(
            f"Mean price moved {direction} {abs(agg['wow_pct_change'])}% week-on-week."
        )
    elif agg["total_bess_profit"]:
        bullets.append(
            f"A simulated 1MW/2MWh battery would have cleared €{agg['total_bess_profit']:.0f} gross "
            f"across the week's best daily cycles."
        )

    return bullets


def build_weekly_draft(any_date_in_week: date) -> Path:
    """Compute the ISO week containing any_date_in_week, aggregate it, and write the draft post."""
    monday, sunday = iso_week_bounds(any_date_in_week)
    days = load_week(monday, sunday)
    if not days:
        raise FileNotFoundError(f"No daily DAM data found for week {monday}–{sunday}")

    prev_monday, prev_sunday = iso_week_bounds(monday - timedelta(days=1))
    prev_days = load_week(prev_monday, prev_sunday) or None

    agg = aggregate_week(days, prev_days)

    chart_dir = CHART_DIR / sunday.isoformat()
    chart_dir.mkdir(parents=True, exist_ok=True)
    chart_path = chart_dir / f"weekly-overview-{sunday.isoformat()}.png"
    chart_weekly_overview(days, monday, sunday, chart_path)

    daily_rows = "\n".join(
        f"| {d['weekday']} {pd.Timestamp(d['date']).strftime('%d %b')} "
        f"| €{d['mean_price']} | €{d['peak_price']} | €{d['min_price']} "
        f"| {d.get('wind_pct_mean', '—')}{'%' if 'wind_pct_mean' in d else ''} |"
        for d in days
    )

    takeaway_lines = "\n".join(f"- {t}" for t in agg["takeaways"])

    summary_line = (
        f"DAM prices averaged €{agg['week_mean']}/MWh this week"
        + (f", {'up' if agg.get('wow_pct_change', 0) > 0 else 'down'} "
           f"{abs(agg['wow_pct_change'])}% week-on-week" if "wow_pct_change" in agg else "")
        + f", ranging from €{agg['week_min_price']} to €{agg['week_peak_price']}/MWh."
    )

    md = f"""---
title: "Weekly Analysis — {monday.strftime('%-d')}–{sunday.strftime('%-d %B %Y')}"
slug: "{sunday.isoformat()}"
date: {sunday.isoformat()}
authors: ["Eoin"]
tags: ["weekly-analysis", "I-SEM"]
summary: "{summary_line}"
images: ["charts/weekly/{sunday.isoformat()}/weekly-overview-{sunday.isoformat()}.png"]
draft: true
ShowToc: true
---

## Key Takeaways

{takeaway_lines}

## Weekly Price Overview

![Week in Review](/charts/weekly/{sunday.isoformat()}/weekly-overview-{sunday.isoformat()}.png)

| Day | Mean | Peak | Min | Wind % |
|-----|------|------|-----|--------|
{daily_rows}
{"" if agg['days_covered'] == 7 else f'''
<!--
Only {agg['days_covered']} of 7 days had data — note the gap in the analysis below.
-->
'''}
## Analysis

<!--
Write 800-1200 words here. The Key Takeaways above are templated from the
numbers, not real analysis — use them as a starting point, not a substitute:
- What actually drove the week's price shape? Outages, interconnector flows,
  demand patterns, weather that the wind % alone doesn't capture?
- How does this week compare to the broader monthly/seasonal trend?
- Anything worth flagging for businesses on variable-rate contracts?
-->

## Methodology

Data sourced from SEMO Day-Ahead Market results and EirGrid generation reports.
Analysis performed in Python using pandas and matplotlib.
"""

    outdir = CONTENT_DIR / "weekly"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"{sunday.isoformat()}.md"
    outpath.write_text(md)
    print(f"\nWeekly draft scaffolded: {outpath}")
    print(f"Covered {agg['days_covered']}/7 days. Chart: {chart_path}")
    return outpath


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        target = date.fromisoformat(sys.argv[1])
    else:
        # Most recently completed ISO week (last Sunday, or today if today is Sunday)
        today = date.today()
        target = today - timedelta(days=today.weekday() + 1) if today.weekday() != 6 else today

    build_weekly_draft(target)
