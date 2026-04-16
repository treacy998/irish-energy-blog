"""
scaffold.py — Generate a pre-filled markdown post for a given day.

Reads processed data, generates charts, and outputs a .md file
ready for you to add commentary and push to the repo.

Usage:
    python pipeline/scaffold.py                   # yesterday
    python pipeline/scaffold.py 2026-04-13        # specific date
    python pipeline/scaffold.py 2026-04-13 weekly  # weekly post template
"""

import sys
from pathlib import Path
from datetime import date, timedelta

from process import load_dam_data, daily_summary
from charts import generate_daily_charts

DATA_DIR = Path(__file__).parent.parent / "data"
CONTENT_DIR = Path(__file__).parent.parent / "site" / "content"


def find_data_file(target_date: date) -> Path:
    """Locate the data file for the target date."""
    # Check for date-specific file first, then fall back to sample
    specific = DATA_DIR / f"semo_dam_{target_date.isoformat()}.csv"
    sample = DATA_DIR / "semo_dam_sample.csv"

    if specific.exists():
        return specific
    elif sample.exists():
        print(f"  Using sample data (no file for {target_date})")
        return sample
    else:
        raise FileNotFoundError(f"No data file found for {target_date}")


def scaffold_daily(target_date: date):
    """Generate a daily briefing post with charts and pre-filled metrics."""
    data_file = find_data_file(target_date)
    date_str = target_date.isoformat()

    # Generate charts and get summary stats
    summary = generate_daily_charts(data_file, target_date)

    # Build wind row if data available
    wind_row = ""
    if "wind_pct_mean" in summary:
        wind_row = f"| Wind % of Demand     | {summary['wind_pct_mean']}%          |"

    demand_row = ""
    if "demand_mean_mw" in summary:
        demand_row = f"\n| Mean Demand          | {summary['demand_mean_mw']:.0f} MW       |"

    # Generate markdown
    md = f"""---
title: "I-SEM Daily Briefing — {target_date.strftime('%-d %B %Y')}"
date: {date_str}
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €{summary['mean_price']}/MWh, peaking at €{summary['peak_price']}/MWh at {summary['peak_time']}."
draft: false
---

## Market Snapshot

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €{summary['mean_price']}/MWh    |
| Peak Price           | €{summary['peak_price']}/MWh ({summary['peak_time']}) |
| Min Price            | €{summary['min_price']}/MWh ({summary['min_time']})   |
| Price Range          | €{summary['price_range']}/MWh   |
{wind_row}{demand_row}

## Price Profile

![DAM Price Profile](/charts/dam-{date_str}.png)

## Price vs Wind

![Price vs Wind Generation](/charts/price-wind-{date_str}.png)

## Week in Context

![7-Day Price Comparison](/charts/week-compare-{date_str}.png)

## Commentary

<!-- 
Write 2-3 paragraphs here:
- What drove the price shape today?
- How does wind/demand explain the peak and trough?
- Anything unusual compared to the week?
- Market context: outages, interconnector, weather forecast?
-->


"""

    # Write post
    outdir = CONTENT_DIR / "daily"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"{date_str}.md"
    outpath.write_text(md)
    print(f"\nPost scaffolded: {outpath}")
    print(f"Next: open the file, write your commentary, push to git.")


def scaffold_weekly(target_date: date):
    """Generate a weekly deep-dive post template."""
    date_str = target_date.isoformat()
    week_start = target_date - timedelta(days=6)

    md = f"""---
title: "Weekly Analysis — {week_start.strftime('%-d')}–{target_date.strftime('%-d %B %Y')}"
date: {date_str}
authors: ["Eoin"]
tags: ["weekly-analysis", "I-SEM"]
summary: ""
draft: true
ShowToc: true
---

## Key Takeaways

-
-
-

## Weekly Price Overview

<!-- Embed weekly charts here -->

## Analysis

<!-- 800-1200 words of data-driven analysis -->

## Methodology

Data sourced from SEMO Day-Ahead Market results and EirGrid generation reports.
Analysis performed in Python using pandas and matplotlib.
Code available at [GitHub](https://github.com/YOURUSERNAME/irish-energy-blog).

"""

    outdir = CONTENT_DIR / "weekly"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"{date_str}.md"
    outpath.write_text(md)
    print(f"\nWeekly post scaffolded: {outpath}")


if __name__ == "__main__":
    # Parse arguments
    if len(sys.argv) >= 2:
        target = date.fromisoformat(sys.argv[1])
    else:
        target = date.today() - timedelta(days=1)

    post_type = sys.argv[2] if len(sys.argv) >= 3 else "daily"

    if post_type == "weekly":
        scaffold_weekly(target)
    else:
        scaffold_daily(target)
