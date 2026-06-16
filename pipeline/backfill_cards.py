#!/usr/bin/env python3
"""
backfill_cards.py — Generate missing card-{date}.png social cards for existing daily posts.

For each site/content/daily/<date>/ post, finds the cached SEM-DA CSV in data/
whose delivery date matches, computes the daily summary, and calls
chart_social_card(). Skips dates whose card already exists.
"""

from pathlib import Path

from process import load_dam_data, daily_summary
from charts import chart_social_card, CHART_DIR, DATA_DIR

CONTENT_DIR = Path(__file__).parent.parent / "site" / "content" / "daily"


def build_date_to_file_map() -> dict:
    """Map delivery date (ISO string) -> CSV path for every cached SEM-DA file."""
    mapping = {}
    for p in sorted(DATA_DIR.glob("MarketResult_SEM-DA_*.csv")):
        try:
            df = load_dam_data(p)
        except Exception as e:
            print(f"  Warning: skipped {p.name} ({e})")
            continue
        delivery_date = df["DeliveryDate"].dt.date.iloc[0].isoformat()
        mapping[delivery_date] = p
    return mapping


def main():
    date_to_file = build_date_to_file_map()

    post_dates = sorted(
        p.name for p in CONTENT_DIR.iterdir()
        if p.is_dir() and p.name != "_index.md"
    )

    missing_csv = []
    generated = []
    skipped = []

    for date_str in post_dates:
        card_path = CHART_DIR / date_str / f"card-{date_str}.png"
        if card_path.exists():
            skipped.append(date_str)
            continue

        filepath = date_to_file.get(date_str)
        if filepath is None:
            missing_csv.append(date_str)
            continue

        from datetime import date as date_cls
        target_date = date_cls.fromisoformat(date_str)
        df = load_dam_data(filepath)
        summary = daily_summary(df, target_date)

        card_path.parent.mkdir(parents=True, exist_ok=True)
        chart_social_card(summary, date_str, card_path)
        generated.append(date_str)

    print(f"\nGenerated: {len(generated)}")
    print(f"Already existed: {len(skipped)}")
    if missing_csv:
        print(f"Missing CSV for: {', '.join(missing_csv)}")


if __name__ == "__main__":
    main()
