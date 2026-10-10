"""
scaffold.py — Generate a pre-filled markdown post for a given day.

Reads processed data, generates charts, and outputs a .md file
ready for you to add commentary and push to the repo.

Usage:
    python pipeline/scaffold.py                   # yesterday
    python pipeline/scaffold.py 2026-04-13        # specific date
    python pipeline/scaffold.py 2026-04-13 weekly  # weekly post template
"""

import re
import sys
from pathlib import Path
from datetime import date, timedelta

from process import load_dam_data, get_day_data, daily_summary
from trading_day import expected_periods
from charts import generate_daily_charts
from weekly_stats import MIN_N, ordinal

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
    has_wind = (eirgrid_df is not None and "WindGeneration_pct" in day_df.columns
                and day_df["WindGeneration_pct"].notna().any())

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


def classify_day_type(summary: dict) -> str:
    """Classify the day for the broker-takeaway section. Checked in priority order
    so an extreme day is never miscategorized as merely 'wide-spread'. wind-cheap
    is the only label that makes a causal claim (cheap *because of* wind), so it's
    the only one gated on wind data actually being present."""
    peak_offpeak_spread = summary.get("peak_offpeak_spread")
    wind_pct = summary.get("wind_pct_mean")

    if summary["peak_price"] >= 250 or summary["periods_above_200"] >= 4:
        return "spike"
    if summary["price_range"] >= 150 or (peak_offpeak_spread is not None and peak_offpeak_spread >= 100):
        return "wide-spread"
    if wind_pct is not None and wind_pct >= 55 and summary["mean_price"] <= 55:
        return "wind-cheap"
    return "flat"


def build_broker_section(renewing: str = "", on_variable: str = "", already_fixed: str = "") -> str:
    """The Broker Takeaway section, or "" unless at least one label has real text. The daily
    scaffold has no source for this text (it is written by hand), so it never emits the section:
    an empty heading with three bare labels renders as a blank block on the live page."""
    parts = [("Renewing", renewing), ("On variable", on_variable), ("Already fixed", already_fixed)]
    if not any(text.strip() for _, text in parts):
        return ""
    body = "\n\n".join(f"**{label}:** {text.strip()}".rstrip() for label, text in parts)
    return f"\n## Broker Takeaway\n\n{body}\n"


class PostExistsError(FileExistsError):
    """An existing post would be overwritten and --force was not given."""


def _front_matter_and_body(text: str) -> tuple[str, str]:
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return (m.group(1), text[m.end():]) if m else ("", text)


def check_post_overwrite(outpath: Path, new_md: str, force: bool = False) -> None:
    """Raise PostExistsError unless outpath can be (re)written without losing anything.

    An existing post may be rewritten only when it is still a draft (draft: true) and its body
    is exactly what the scaffold would write now. A published post (draft: false) or one whose
    body differs from the scaffold output has been edited or released, so only force=True
    overwrites it. A missing file is always fine."""
    if force or not outpath.exists():
        return
    old_fm, old_body = _front_matter_and_body(outpath.read_text())
    _, new_body = _front_matter_and_body(new_md)
    is_draft = re.search(r"^draft:\s*true\s*$", old_fm, re.M) is not None
    if is_draft and old_body == new_body:
        return
    why = "it is published (draft is not true)" if not is_draft else "its body differs from the scaffold output"
    raise PostExistsError(f"{outpath} exists and {why}; refusing to overwrite it. Pass --force to replace it.")


def scaffold_daily(target_date: date, explicit_file: Path = None, title: str = None, eirgrid_df=None, bess_result=None, force: bool = False, include_bess: bool = False):
    """Generate a daily briefing post with charts and pre-filled metrics."""
    data_file = find_data_file(target_date, explicit=explicit_file)
    if title is None:
        title = f"I-SEM Daily Briefing — {target_date.strftime('%-d %B %Y')}"
    date_str = target_date.isoformat()

    # Generate charts and get summary stats
    # BESS charts (png + html) are only drawn when the section is included.
    summary = generate_daily_charts(data_file, target_date, eirgrid_df=eirgrid_df,
                                    bess_result=bess_result if include_bess else None, force=force)

    # Load day-level data for the table (same data used by charts)
    day_df = get_day_data(data_file, target_date)
    if eirgrid_df is not None:
        wind_cols = ["StartUTC", "WindMW", "DemandMW", "WindGeneration_pct"]
        day_df = day_df.merge(eirgrid_df[wind_cols], on="StartUTC", how="left")

    data_table = _build_data_table(day_df, eirgrid_df, date_str)

    CHART_DIR = Path(__file__).parent.parent / "site" / "static" / "charts"
    chart_day_dir = CHART_DIR / date_str

    # ── Snapshot table rows (conditional on data availability) ──────────────
    n_periods = expected_periods(target_date)   # 48; 50 or 46 on the clock-change days
    pct_48 = lambda n: f"{n/n_periods*100:.0f}%"

    median_row = f"\n| Median Price         | €{summary['median_price']}/MWh    |"
    std_row    = f"\n| Std Dev              | €{summary['std_dev']}/MWh    |"
    above_rows = (
        f"\n| Periods above €150   | {summary['periods_above_150']} of {n_periods} ({pct_48(summary['periods_above_150'])}) |"
        f"\n| Periods above €200   | {summary['periods_above_200']} of {n_periods} ({pct_48(summary['periods_above_200'])}) |"
    )

    spread_rows = ""
    if "peak_mean" in summary:
        spread_rows = (
            f"\n| Peak Avg (07–22)     | €{summary['peak_mean']}/MWh    |"
            f"\n| Off-peak Avg (22–07) | €{summary['offpeak_mean']}/MWh    |"
            f"\n| Peak/Off-Peak Spread | €{summary['peak_offpeak_spread']}/MWh   |"
        )

    arb_spread_row = ""
    if "arb_spread" in summary:
        arb_spread_row = f"\n| Cheap/Dear Spread    | €{summary['cheap_mean']}/MWh → €{summary['dear_mean']}/MWh (€{summary['arb_spread']}) |"

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
        f"  ·  **Periods above €150:** {summary['periods_above_150']} of {n_periods} ({pct_48(summary['periods_above_150'])})"
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
        if "arb_spread" in summary:
            spread_stats += (
                f"\n\n**Cheap window:** €{summary['cheap_mean']}/MWh"
                f"  ·  **Dear window:** €{summary['dear_mean']}/MWh"
                f"  ·  **Spread:** €{summary['arb_spread']}/MWh"
                f"  — the actual cheapest and dearest 2-hour blocks of the day, wherever they fall on the clock"
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
    if include_bess and bess_result is not None:
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
"""
    else:
        bess_section = ""

    storage_prompt_line = "- Was it a good day for storage?\n" if include_bess else ""

    broker_section = build_broker_section()

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
| Price Range          | €{summary['price_range']}/MWh   |{above_rows}{spread_rows}{arb_spread_row}{wind_row}{wind_range_row}{demand_row}

</details>

## Price Profile

![DAM Price Profile](/charts/{date_str}/dam-{date_str}.png)
{price_profile_stats}
{wind_chart_section}
## Week in Context

![7-Day Price Comparison](/charts/{date_str}/week-compare-{date_str}.png)
{pdc_section}{spread_section}{bess_section}{broker_section}
## Commentary

<!--
Write 2-3 paragraphs here:
- What drove the price shape today?
- How does wind/demand explain the peak and trough?
- Anything unusual compared to the week?
- Market context: outages, interconnector, weather forecast?
{storage_prompt_line}-->

{data_table}
"""

    # Write post as a Hugo leaf bundle so assets can co-locate in the same folder
    outdir = CONTENT_DIR / "daily" / date_str
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / "index.md"

    check_post_overwrite(outpath, md, force)
    outpath.write_text(md)
    print(f"\nPost scaffolded: {outpath}")
    print(f"Next: open the file, write your commentary, push to git.")


def _day_month(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%-d %b")


def weekly_verdict_text(summary: dict) -> str:
    """The post's opening sentence(s), generated from weekly_summary(): the rank first (it is a
    fact), the baseline label second (it is derived from the rank), then week-on-week if the
    previous week's mean is more than 10% away. With a suppressed baseline it says there is no
    verdict instead of inventing one."""
    t = summary["trailing"]
    if t["suppressed"]:
        parts = [f"No verdict this week: the store holds only {t['n']} complete earlier week{'' if t['n'] == 1 else 's'} and a "
                 f"comparison needs {MIN_N['trailing']}, so the week is not ranked or labelled."]
    else:
        head = (f"Dearest of the last {t['rank_of']} weeks" if t["rank"] == 1
                else f"{ordinal(t['rank'])} dearest of the last {t['rank_of']} weeks")
        tail = (f"last dearer: week of {_day_month(t['dearest_since'])}" if t["dearest_since"]
                else "no earlier week in the store was as dear")
        parts = [f"{head}; {tail}.", f"Against the previous {t['n']} weeks: {summary['verdict_price']}."]
    prev = summary["previous_week_mean"]
    if prev and abs(summary["week_mean"] / prev - 1) > 0.10:
        change = (summary["week_mean"] / prev - 1) * 100
        parts.append(f"Week on week: {'up' if change > 0 else 'down'} {abs(change):.0f}%.")
    return " ".join(parts)


WEEKLY_CAVEAT = (
    "> **This is the wholesale day-ahead price, not your bill.** Network charges, levies, supplier "
    "margin and VAT are on top, and they differ by contract. A cheap week is not a reason to fix "
    "your rate, and an expensive one is not a reason to panic."
)


def build_weekly_post(summary: dict, content_root: Path | None = None, force: bool = False) -> Path:
    """Write <content_root>/weekly/<week_start>/index.md (draft: true) from weekly_summary().

    The audit keys on the week_start front matter and reads the labelled table rows, so the
    row labels here are the ones audit_posts.WEEKLY_ROWS expects. Refuses to overwrite an
    existing post unless force=True (it may have hand-written commentary)."""
    content_root = Path(content_root) if content_root else CONTENT_DIR
    ws, we = date.fromisoformat(summary["week_start"]), date.fromisoformat(summary["week_end"])
    outpath = content_root / "weekly" / summary["week_start"] / "index.md"
    if outpath.exists() and not force:
        raise FileExistsError(f"{outpath} exists; pass force=True to overwrite")

    t, sea = summary["trailing"], summary["seasonal"]
    verdict = weekly_verdict_text(summary)
    chart_url = f"/charts/weekly/{summary['week_start']}.png"
    title = (f"Weekly Analysis — {ws.strftime('%-d')}–{we.strftime('%-d %B %Y')}" if ws.month == we.month
             else f"Weekly Analysis — {ws.strftime('%-d %B')}–{we.strftime('%-d %B %Y')}")

    # (c) exactly two numbers: the week mean and the volatility verdict with its spread
    if summary["verdict_volatility"] is not None:
        vol_row = (f"| Volatility verdict (trailing) | {summary['verdict_volatility']} "
                   f"(median daily spread €{summary['median_arb_spread']}/MWh) |")
    else:
        vol_row = (f"| Median daily spread | €{summary['median_arb_spread']}/MWh "
                   f"(no volatility verdict: baseline too short) |")
    key_table = "\n".join([
        "| Measure | Value |", "|---|---|",
        f"| Week mean (c/kWh) | {summary['week_mean_c_per_kwh']} |",
        vol_row,
    ])

    compare_rows = []
    if not t["suppressed"]:
        compare_rows += [
            f"| Rank vs trailing {t['n']} weeks (1 = dearest) | {t['rank']} of {t['rank_of']} |",
            f"| Dearest since (trailing) | {t['dearest_since'] or 'none in the store'} |",
            f"| Cheapest since (trailing) | {t['cheapest_since'] or 'none in the store'} |",
            f"| Price verdict (trailing) | {t['verdict_price']} |",
        ]
    if sea and not sea["suppressed"]:
        compare_rows += [
            f"| Rank vs seasonal {sea['n']} weeks (1 = dearest) | {sea['rank']} of {sea['rank_of']} |",
            f"| Dearest since (seasonal) | {sea['dearest_since'] or 'none in the seasonal weeks'} |",
            f"| Cheapest since (seasonal) | {sea['cheapest_since'] or 'none in the seasonal weeks'} |",
            f"| Price verdict (seasonal) | {sea['verdict_price']} |",
        ]
    compare_table = ("\n".join(["| Comparison | Value |", "|---|---|"] + compare_rows)
                     if compare_rows else "")
    seasonal_note = "" if sea else (
        f"Same week last year: not available. {summary['seasonal_reason'].capitalize()}.")

    day_rows = "\n".join(
        f"| {date.fromisoformat(d).strftime('%a %-d %b')} | {m / 10:.2f} | {m:.2f} |"
        for d, m in zip(summary["daily_dates"], summary["daily_means"]))
    clock_note = ("" if summary["n_periods"] == 48 * len(summary["daily_dates"]) else
                  f"\nThis week has {summary['n_periods']} half-hour periods rather than "
                  f"{48 * len(summary['daily_dates'])}: it contains a clock-change day.\n")

    if summary["wind_mw_mean"] is None:
        wind_rows = "| Mean wind (MW) | n/a: no wind data in the store for this week |"
    else:
        wind_rows = f"| Mean wind (MW) | {summary['wind_mw_mean']} |"
    if summary["wind_mw_trailing_median"] is None:
        wind_rows += (f"\n| Trailing median wind (MW) | n/a: needs {MIN_N['trailing']} earlier weeks with "
                      f"75% wind coverage, have {summary['wind_mw_trailing_n']} |")
    else:
        wind_rows += f"\n| Trailing median wind (MW) | {summary['wind_mw_trailing_median']} |"
    wind_rows += f"\n| Wind coverage | {summary['wind_coverage'] * 100:.0f}% of periods have wind data |"

    def above(level: str, n: int, med) -> str:
        extra = f" (trailing median {med:g})" if med is not None else ""
        return f"| Periods above €{level} | {n} of {summary['n_periods']}{extra} |"

    md = f"""---
title: "{title}"
slug: "{summary['week_start']}"
date: {we.isoformat()}
week_start: {summary['week_start']}
authors: ["Eoin"]
tags: ["weekly-analysis", "I-SEM"]
summary: "{verdict}"
images: ["{chart_url.lstrip('/')}"]
draft: true
ShowToc: true
---

{verdict}

![Weekly mean day-ahead price against the previous weeks]({chart_url})

{key_table}

{seasonal_note}

## How this week compares

{compare_table}

## Daily means

| Day | Mean (c/kWh) | Mean (€/MWh) |
|-----|--------------|--------------|
{day_rows}
{clock_note}
## Wind and price spikes

| Measure | Value |
|---|---|
{wind_rows}
{above('150', summary['periods_above_150'], summary['periods_above_150_trailing_median'])}
{above('200', summary['periods_above_200'], summary['periods_above_200_trailing_median'])}

{WEEKLY_CAVEAT}

## Commentary

<!--
Write 2-3 paragraphs here:
- What does the rank say, and what does the chart show about the direction of weekly prices?
- What did wind (MW) and the daily spread add this week?
- Did anything this week change what a business on a variable-rate contract would pay?
-->

## Methodology

Day-ahead prices are SEMOpx market results; wind is EirGrid's reported wind generation in MW.
The comparison uses the previous {t['n']} complete weeks, ranked by mean price, and is
reproducible from the stored data.
"""
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(md)
    print(f"  Weekly draft scaffolded: {outpath}")
    return outpath


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
