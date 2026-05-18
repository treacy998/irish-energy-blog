"""
run_daily.py — One-command daily workflow.

Fetches today's SEMO DAM data automatically, generates charts, and scaffolds the post.

Usage:
    python pipeline/run_daily.py                                        # auto-fetch yesterday's DAM report
    python pipeline/run_daily.py data/MarketResult_SEM-DA_PWR-MRC-D+1_20260513100000.csv
"""

import sys
from datetime import date
from pathlib import Path

from process import load_dam_data
from scaffold import scaffold_daily
from fetch import fetch_wind_and_demand, fetch_semo
from bess import simulate_bess

DATA_DIR = Path(__file__).parent.parent / "data"
CHART_DIR = Path(__file__).parent.parent / "site" / "static" / "charts"
CONTENT_DIR = Path(__file__).parent.parent / "site" / "content"


def find_latest_data_file() -> Path:
    market_results = sorted(
        DATA_DIR.glob("MarketResult_SEM-DA_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if market_results:
        return market_results[0]

    sample = DATA_DIR / "semo_dam_sample.csv"
    if sample.exists():
        print("  Warning: no real data found, falling back to sample data")
        return sample

    raise FileNotFoundError(
        "No data file found in data/.\n"
        "Run without arguments to auto-fetch, or download from semopx.com and drop the CSV into data/"
    )


def step(n: int, total: int, msg: str):
    print(f"\n[{n}/{total}] {msg}")


def main():
    TOTAL_STEPS = 3

    # ── Step 1: find / fetch data file ───────────────────────────────────────
    step(1, TOTAL_STEPS, "Finding data file...")

    if len(sys.argv) >= 2:
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        if "SEM-DA" not in filepath.name and filepath.name != "semo_dam_sample.csv":
            raise ValueError(
                f"{filepath.name} doesn't look like a DAM file.\n"
                "Expected a file containing 'SEM-DA' in the name (ETS Market Results)."
            )
    else:
        print("  Auto-fetching latest EA-001 report from SEMOpx…")
        try:
            filepath = fetch_semo(out_dir=DATA_DIR)
            print(f"  ✓ {filepath.name}")
        except Exception as e:
            print(f"  – SEMOpx fetch failed ({e}), falling back to cached files")
            filepath = find_latest_data_file()

    print(f"  File:  {filepath.name}")

    # ── Step 2: detect delivery date ─────────────────────────────────────────
    step(2, TOTAL_STEPS, "Reading data...")
    df = load_dam_data(filepath)
    delivery_date = df["DeliveryDate"].dt.date.iloc[0]
    date_str = delivery_date.isoformat()
    print(f"  Delivery date: {delivery_date.strftime('%-d %B %Y')} ({date_str})")
    print(f"  Periods loaded: {len(df)}")

    title = f"I-SEM Daily Briefing — {delivery_date.strftime('%-d %B %Y')}"

    # ── Step 3: generate charts + scaffold post ──────────────────────────────
    step(3, TOTAL_STEPS, "Generating charts and scaffolding post...")
    print("  Fetching EirGrid wind and demand data…")
    eirgrid_df = fetch_wind_and_demand(delivery_date)
    if eirgrid_df is not None:
        print(f"  ✓ EirGrid data fetched — {eirgrid_df['WindGeneration_pct'].mean():.1f}% avg wind")
    else:
        print("  – EirGrid fetch failed, continuing without wind data")

    bess_result = simulate_bess(df)
    if bess_result:
        print(f"  ✓ BESS simulation: €{bess_result['gross_profit']:.0f} gross profit")

    scaffold_daily(delivery_date, explicit_file=filepath, title=title, eirgrid_df=eirgrid_df, bess_result=bess_result)

    # ── Done ─────────────────────────────────────────────────────────────────
    post_path = CONTENT_DIR / "daily" / f"{date_str}.md"
    chart_names = [
        f"dam-{date_str}.png",
        f"price-wind-{date_str}.png",
        f"week-compare-{date_str}.png",
    ]
    charts_found = [n for n in chart_names if (CHART_DIR / n).exists()]

    print(f"\n{'─'*52}")
    print(f"  Done — {delivery_date.strftime('%-d %B %Y')}")
    print(f"{'─'*52}")
    print(f"  Post:   site/content/daily/{date_str}.md")
    if charts_found:
        print(f"  Charts: {len(charts_found)} generated")
        for name in charts_found:
            print(f"    site/static/charts/{name}")
    print(f"""
  Next steps:
    1. Open  site/content/daily/{date_str}.md
       Write 2–3 paragraphs in the Commentary section.

    2. Preview locally:
       cd site && ~/.local/bin/hugo server -D
       (open http://localhost:1313 — hot-reloads on save)

    3. Publish:
       git add . && git commit -m "Daily briefing {date_str}" && git push
""")


if __name__ == "__main__":
    main()
