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

from process import load_dam_data, get_day_data, daily_summary
from charts import generate_daily_charts

DATA_DIR = Path(__file__).parent.parent / "data"
CONTENT_DIR = Path(__file__).parent.parent / "site" / "content"


def find_data_file(target_date: date, explicit: Path = None) -> Path:
    """Locate the data file for the target date."""
    if explicit is not None:
        if not explicit.exists():
            raise FileNotFoundError(f"File not found: {explicit}")
        return explicit

    specific = DATA_DIR / f"semo_dam_{target_date.isoformat()}.csv"
    if specific.exists():
        return specific

    market_results = sorted(
        DATA_DIR.glob("MarketResult_SEM-DA_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if market_results:
        print(f"  Using {market_results[0].name} (most recent MarketResult file)")
        return market_results[0]

    sample = DATA_DIR / "semo_dam_sample.csv"
    if sample.exists():
        print(f"  Using sample data (no real data file found)")
        return sample

    raise FileNotFoundError(f"No data file found for {target_date}")


def _build_data_table(day_df, eirgrid_df, date_str: str) -> str:
    """Return a collapsed markdown table of half-hourly data for the day."""
    cols = ["Period", "StartTime", "DAMPrice_EUR_MWh"]
    has_wind = eirgrid_df is not None and "WindGeneration_pct" in day_df.columns

    header = "| Period | Time | Price (€/MWh) |"
    sep    = "|--------|------|--------------|"
    if has_wind:
        header += " Wind % |"
        sep    += "--------|"

    rows = [header, sep]
    for _, row in day_df.iterrows():
        period = int(row["Period"])
        time   = row.get("StartTime", "")
        if hasattr(time, "strftime"):
            time = time.strftime("%H:%M")
        price  = f"{row['DAMPrice_EUR_MWh']:.2f}"
        line   = f"| {period} | {time} | {price} |"
        if has_wind:
            wind = row.get("WindGeneration_pct", float("nan"))
            line += f" {wind:.1f}% |" if wind == wind else " — |"
        rows.append(line)

    table = "\n".join(rows)
    return f"""
<details>
<summary>Half-hourly data — {date_str}</summary>

{table}

</details>
"""


def scaffold_daily(target_date: date, explicit_file: Path = None, title: str = None, eirgrid_df=None, bess_result=None, force: bool = False):
    """Generate a daily briefing post with charts and pre-filled metrics."""
    data_file = find_data_file(target_date, explicit=explicit_file)
    if title is None:
        title = f"I-SEM Daily Briefing — {target_date.strftime('%-d %B %Y')}"
    date_str = target_date.isoformat()

    # Generate charts and get summary stats
    summary = generate_daily_charts(data_file, target_date, eirgrid_df=eirgrid_df, bess_result=bess_result, force=force)

    # Load day-level data for the table (same data used by charts)
    day_df = get_day_data(data_file, target_date)
    if eirgrid_df is not None:
        eg = eirgrid_df.copy()
        eg["StartTime"] = eg["StartTime"].dt.strftime("%H:%M")
        wind_cols = ["StartTime", "WindMW", "DemandMW", "WindGeneration_pct"]
        day_df = day_df.merge(eg[wind_cols], on="StartTime", how="left")

    data_table = _build_data_table(day_df, eirgrid_df, date_str)

    CHART_DIR = Path(__file__).parent.parent / "site" / "static" / "charts"
    chart_day_dir = CHART_DIR / date_str

    # ── Snapshot table rows (conditional on data availability) ──────────────
    pct_48 = lambda n: f"{n/48*100:.0f}%"

    median_row = f"\n| Median Price         | €{summary['median_price']}/MWh    |"
    std_row    = f"\n| Std Dev              | €{summary['std_dev']}/MWh    |"
    above_rows = (
        f"\n| Periods above €150   | {summary['periods_above_150']} of 48 ({pct_48(summary['periods_above_150'])}) |"
        f"\n| Periods above €200   | {summary['periods_above_200']} of 48 ({pct_48(summary['periods_above_200'])}) |"
    )

    spread_rows = ""
    if "peak_mean" in summary:
        spread_rows = (
            f"\n| Peak Avg (07–22)     | €{summary['peak_mean']}/MWh    |"
            f"\n| Off-peak Avg (22–07) | €{summary['offpeak_mean']}/MWh    |"
            f"\n| Peak/Off-Peak Spread | €{summary['peak_offpeak_spread']}/MWh   |"
        )

    wind_row = ""
    if "wind_pct_mean" in summary:
        wind_row = f"\n| Wind % of Demand     | {summary['wind_pct_mean']}%          |"

    wind_range_row = ""
    if "wind_pct_min" in summary and "wind_pct_max" in summary:
        wind_range_row = f"\n| Wind Range           | {summary['wind_pct_min']}%–{summary['wind_pct_max']}% |"

    demand_row = ""
    if "demand_mean_mw" in summary:
        demand_row = f"\n| Mean Demand          | {summary['demand_mean_mw']:.0f} MW       |"

    # ── Per-section stat callouts ─────────────────────────────────────────────
    price_profile_stats = (
        f"\n**Std dev** €{summary['std_dev']}/MWh"
        f"  ·  **Median** €{summary['median_price']}/MWh"
        f"  ·  **Periods above €150:** {summary['periods_above_150']} of 48 ({pct_48(summary['periods_above_150'])})"
    )

    has_wind_chart = (chart_day_dir / f"price-wind-{date_str}.png").exists()
    if has_wind_chart and "wind_pct_mean" in summary:
        wind_stats = (
            f"\n**Mean wind:** {summary['wind_pct_mean']}%"
            + (f"  ·  **Range:** {summary['wind_pct_min']}%–{summary['wind_pct_max']}%" if "wind_pct_min" in summary else "")
        )
        wind_chart_section = (
            f"\n## Price vs Wind\n\n"
            f"![Price vs Wind Generation](/charts/{date_str}/price-wind-{date_str}.png)\n"
            f"{wind_stats}\n"
        )
    elif has_wind_chart:
        wind_chart_section = f"\n## Price vs Wind\n\n![Price vs Wind Generation](/charts/{date_str}/price-wind-{date_str}.png)\n"
    else:
        wind_chart_section = ""

    has_pdc_chart = (chart_day_dir / f"pdc-{date_str}.png").exists()
    if has_pdc_chart:
        pdc_stats = (
            f"\n**Periods above €150:** {summary['periods_above_150']} ({pct_48(summary['periods_above_150'])} of day)"
            f"  ·  **Above €200:** {summary['periods_above_200']} ({pct_48(summary['periods_above_200'])} of day)"
        )
        pdc_section = (
            f"\n## Price Duration Curve\n\n"
            f"![Price Duration Curve](/charts/{date_str}/pdc-{date_str}.png)\n"
            f"{pdc_stats}\n"
        )
    else:
        pdc_section = ""

    has_spread_chart = (chart_day_dir / f"spread-{date_str}.png").exists()
    if has_spread_chart and "peak_mean" in summary:
        spread_stats = (
            f"\n**Peak avg (07:00–22:00):** €{summary['peak_mean']}/MWh"
            f"  ·  **Off-peak avg:** €{summary['offpeak_mean']}/MWh"
            f"  ·  **Spread:** €{summary['peak_offpeak_spread']}/MWh"
        )
        spread_section = (
            f"\n## Peak / Off-Peak Spread\n\n"
            f"![Peak / Off-Peak Spread](/charts/{date_str}/spread-{date_str}.png)\n"
            f"{spread_stats}\n"
        )
    elif has_spread_chart:
        spread_section = f"\n## Peak / Off-Peak Spread\n\n![Peak / Off-Peak Spread](/charts/{date_str}/spread-{date_str}.png)\n"
    else:
        spread_section = ""

    has_bess_chart = (chart_day_dir / f"bess-{date_str}.png").exists()
    if bess_result is not None:
        b = bess_result
        bess_roi = round((b['gross_profit'] / b['charge_cost']) * 100, 1) if b['charge_cost'] > 0 else 0
        bess_section = f"""
## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €{b['charge_mean']:.0f}/MWh | {b['charge_start']} | 2 MWh | −€{b['charge_cost']:.0f} |
| **Discharge** | €{b['discharge_mean']:.0f}/MWh | {b['discharge_start']} | 1.7 MWh (85% RTE) | +€{b['gross_revenue']:.0f} |
| **Gross profit** | | | | **€{b['gross_profit']:.0f}** |
| **Price spread** | €{b['spread']:.0f}/MWh | | | **ROI: {bess_roi}%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*
{"" if not has_bess_chart else f"""
![BESS Dispatch](/charts/{date_str}/bess-{date_str}.png)
"""}
<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->
"""
    else:
        bess_section = ""

    # Generate markdown
    md = f"""---
title: "{title}"
date: {date_str}
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €{summary['mean_price']}/MWh, peaking at €{summary['peak_price']}/MWh at {summary['peak_time']}."
images: ["charts/{date_str}/card-{date_str}.png"]
draft: false
---

{{{{< statbar mean="€{summary['mean_price']}" peak="€{summary['peak_price']}" min="€{summary['min_price']}" spread="€{summary['price_range']}" >}}}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €{summary['mean_price']}/MWh    |{median_row}{std_row}
| Peak Price           | €{summary['peak_price']}/MWh ({summary['peak_time']}) |
| Min Price            | €{summary['min_price']}/MWh ({summary['min_time']})   |
| Price Range          | €{summary['price_range']}/MWh   |{above_rows}{spread_rows}{wind_row}{wind_range_row}{demand_row}

</details>

## Price Profile

![DAM Price Profile](/charts/{date_str}/dam-{date_str}.png)
{price_profile_stats}
{wind_chart_section}
## Week in Context

![7-Day Price Comparison](/charts/{date_str}/week-compare-{date_str}.png)
{pdc_section}{spread_section}{bess_section}
## Commentary

<!--
Write 2-3 paragraphs here:
- What drove the price shape today?
- How does wind/demand explain the peak and trough?
- Anything unusual compared to the week?
- Market context: outages, interconnector, weather forecast?
-->

{data_table}
"""

    # Write post as a Hugo leaf bundle so assets can co-locate in the same folder
    outdir = CONTENT_DIR / "daily" / date_str
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / "index.md"

    if outpath.exists() and not force:
        print(f"\nPost already exists — skipping scaffold to preserve your edits: {outpath}")
        print(f"Charts were regenerated. Use --force to overwrite the post.")
        return

    outpath.write_text(md)
    print(f"\nPost scaffolded: {outpath}")
    print(f"Next: open the file, write your commentary, push to git.")


def scaffold_weekly(target_date: date):
    """Generate a weekly deep-dive post, pre-filled from the ISO week's daily data.

    Delegates to weekly.py, which aggregates the 7 days of DAM/wind data
    (Mon-Sun containing target_date) into stats, a chart, and templated
    takeaway bullets — still draft: true, still needs the Analysis section
    written by hand.
    """
    from weekly import build_weekly_draft
    build_weekly_draft(target_date)


if __name__ == "__main__":
    # Usage:
    #   python scaffold.py                                        # yesterday, auto-detect file
    #   python scaffold.py 2026-05-12                            # specific date, auto-detect file
    #   python scaffold.py 2026-05-12 data/MarketResult_...csv  # specific date + specific file
    #   python scaffold.py 2026-05-12 weekly                    # weekly post template
    if len(sys.argv) >= 2:
        target = date.fromisoformat(sys.argv[1])
    else:
        target = date.today() - timedelta(days=1)

    arg2 = sys.argv[2] if len(sys.argv) >= 3 else None

    if arg2 == "weekly":
        scaffold_weekly(target)
    elif arg2 is not None:
        scaffold_daily(target, explicit_file=Path(arg2))
    else:
        scaffold_daily(target)
