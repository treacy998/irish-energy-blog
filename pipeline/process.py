"""
process.py — Clean raw SEMO/EirGrid data and produce analysis-ready summaries.

Reads from data/ and outputs processed summaries used by charts.py and scaffold.py.
"""

import pandas as pd
from pathlib import Path
from datetime import date

DATA_DIR = Path(__file__).parent.parent / "data"


def load_dam_data(filepath: Path) -> pd.DataFrame:
    """Load and clean a SEMO DAM CSV."""
    df = pd.read_csv(filepath)

    # Standard cleaning — adapt column names if real SEMO format differs
    expected_cols = ["DeliveryDate", "Period", "StartTime", "DAMPrice_EUR_MWh"]
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Missing expected column: {col}")

    df["DeliveryDate"] = pd.to_datetime(df["DeliveryDate"])
    return df


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

    # Demo with sample data
    sample = DATA_DIR / "semo_dam_sample.csv"
    if not sample.exists():
        print("Run generate_sample_data.py first")
        raise SystemExit(1)

    target = date(2026, 4, 13)  # low-wind day in sample data
    summary = daily_summary(load_dam_data(sample), target)

    print(f"\n{'='*45}")
    print(f"  Daily Summary — {summary['date']}")
    print(f"{'='*45}")
    for k, v in summary.items():
        if k != "date":
            label = k.replace("_", " ").title()
            print(f"  {label:.<30} {v}")
