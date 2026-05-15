"""
run_daily.py — One-command daily workflow.

Finds the most recent SEMO data file, generates charts, and scaffolds the post.

Usage:
    python pipeline/run_daily.py
    python pipeline/run_daily.py data/MarketResult_SEM-DA_PWR-MRC-D+1_20260513100000.csv
"""

import sys
from pathlib import Path

from process import load_dam_data
from scaffold import scaffold_daily

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
        print("Warning: no real data found, falling back to sample data")
        return sample

    raise FileNotFoundError(
        "No data file found in data/.\n"
        "Download ETS Market Results from sem-o.com/market-data/dynamic-reports "
        "and drop the CSV into data/"
    )


def main():
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
        filepath = find_latest_data_file()
    print(f"Data file:  {filepath.name}")

    df = load_dam_data(filepath)
    delivery_date = df["DeliveryDate"].dt.date.iloc[0]
    date_str = delivery_date.isoformat()
    print(f"Delivery:   {date_str}\n")

    default_title = f"I-SEM Daily Briefing — {delivery_date.strftime('%-d %B %Y')}"
    user_input = input(f"Post title [{default_title}]: ").strip()
    title = user_input if user_input else default_title

    scaffold_daily(delivery_date, explicit_file=filepath, title=title)

    post_path = CONTENT_DIR / "daily" / f"{date_str}.md"
    chart_names = [
        f"dam-{date_str}.png",
        f"price-wind-{date_str}.png",
        f"week-compare-{date_str}.png",
    ]

    print(f"\n{'='*50}")
    print(f"  Done — {date_str}")
    print(f"{'='*50}")
    print(f"  Post:   site/content/daily/{date_str}.md")
    print(f"  Charts:")
    for name in chart_names:
        if (CHART_DIR / name).exists():
            print(f"    site/static/charts/{name}")
    print(f"""
  Next steps:
    1. Open site/content/daily/{date_str}.md — write commentary
    2. cd site && hugo server -D        (preview at localhost:1313)
    3. git add . && git commit -m "Daily briefing {date_str}" && git push
""")


if __name__ == "__main__":
    main()
