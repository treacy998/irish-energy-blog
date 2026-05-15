"""
process.py — Clean raw SEMO/EirGrid data and produce analysis-ready summaries.

Reads from data/ and outputs processed summaries used by charts.py and scaffold.py.
"""

import pandas as pd
from pathlib import Path
from datetime import date

DATA_DIR = Path(__file__).parent.parent / "data"


def load_dam_data(filepath: Path) -> pd.DataFrame:
    """Load a SEMO DAM CSV (semicolon-delimited wide block format)."""
    with open(filepath, encoding="utf-8") as f:
        rows = [line.rstrip("\n").split(";") for line in f]

    # Delivery date = auction date + 1 day (file is always D+1)
    delivery_date = None
    for row in rows[:10]:
        if row[0].lower().startswith("auction date"):
            delivery_date = (pd.Timestamp(row[1]) + pd.Timedelta(days=1)).date()
            break
    if delivery_date is None:
        raise ValueError("Could not find auction date in file metadata")

    # Locate the EUR index prices block
    ts_row = val_row = None
    for i, row in enumerate(rows):
        if row[0] == "Index prices" and len(row) >= 3 and row[2] == "EUR":
            ts_row = rows[i + 1]
            val_row = rows[i + 2]
            break
    if ts_row is None:
        raise ValueError("Could not find 'Index prices' EUR block")

    records = []
    for period_num, (ts_str, val_str) in enumerate(zip(ts_row, val_row), start=1):
        if not ts_str.strip() or not val_str.strip():
            continue
        ts = pd.Timestamp(ts_str)
        # +1 hour: correct for BST (UTC+1, Apr–Oct). In GMT months (Nov–Mar) Irish time = UTC, so this over-corrects by 1h.
        ts_irish = ts + pd.Timedelta(hours=1)
        price = float(val_str.replace(",", "."))
        records.append({
            "DeliveryDate": pd.Timestamp(delivery_date),
            "Period": period_num,
            "StartTime": ts_irish.strftime("%H:%M"),
            "DAMPrice_EUR_MWh": price,
        })

    return pd.DataFrame(records)


def daily_summary(df: pd.DataFrame, target_date: date) -> dict:
    """
    Compute key daily metrics for a single day.
    Returns a dict used by scaffold.py to populate the post template.
    """
    day = df[df["DeliveryDate"] == pd.Timestamp(target_date)].copy()

    if day.empty:
        raise ValueError(f"No data for {target_date}")

    price = day["DAMPrice_EUR_MWh"]
    peak_idx = price.idxmax()
    min_idx = price.idxmin()

    summary = {
        "date": target_date.isoformat(),
        "mean_price": round(price.mean(), 2),
        "peak_price": round(price.max(), 2),
        "peak_period": int(day.loc[peak_idx, "Period"]),
        "peak_time": day.loc[peak_idx, "StartTime"],
        "min_price": round(price.min(), 2),
        "min_period": int(day.loc[min_idx, "Period"]),
        "min_time": day.loc[min_idx, "StartTime"],
        "price_range": round(price.max() - price.min(), 2),
        "std_dev": round(price.std(), 2),
    }

    # Wind data if available
    if "WindGeneration_pct" in day.columns:
        summary["wind_pct_mean"] = round(day["WindGeneration_pct"].mean(), 1)
    if "SystemDemand_MW" in day.columns:
        summary["demand_mean_mw"] = round(day["SystemDemand_MW"].mean(), 0)

    return summary


def get_day_data(filepath: Path, target_date: date) -> pd.DataFrame:
    """Extract a single day's half-hourly data for charting."""
    df = load_dam_data(filepath)
    day = df[df["DeliveryDate"] == pd.Timestamp(target_date)].copy()
    if day.empty:
        raise ValueError(f"No data for {target_date}")
    return day


if __name__ == "__main__":
    from datetime import date

    raw = DATA_DIR / "semo_dam_raw.csv"
    sample = DATA_DIR / "semo_dam_sample.csv"
    filepath = raw if raw.exists() else sample
    if not filepath.exists():
        print("No data file found — download semo_dam_raw.csv or run generate_sample_data.py")
        raise SystemExit(1)

    df = load_dam_data(filepath)
    target = df["DeliveryDate"].dt.date.iloc[0]
    summary = daily_summary(df, target)

    print(f"\n{'='*45}")
    print(f"  Daily Summary — {summary['date']}")
    print(f"{'='*45}")
    for k, v in summary.items():
        if k != "date":
            label = k.replace("_", " ").title()
            print(f"  {label:.<30} {v}")
