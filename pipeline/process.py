"""
process.py — Clean raw SEMO/EirGrid data and produce analysis-ready summaries.

Reads from data/ and outputs processed summaries used by charts.py and scaffold.py.
"""

import math

import pandas as pd
from pathlib import Path
from datetime import date
from zoneinfo import ZoneInfo

from trading_day import expected_periods, period_start_utc

DUBLIN_TZ = ZoneInfo("Europe/Dublin")

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
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        ts_utc = ts.tz_convert("UTC")
        # The file's own timestamps are checked against the trading-day mapping
        # (local 23:00 the evening before + 30 min x (n-1), in UTC), so a
        # clock-change day with the wrong number or order of periods fails here.
        if ts_utc != period_start_utc(delivery_date, period_num):
            raise ValueError(
                f"period {period_num} starts {ts_utc.isoformat()}, expected "
                f"{period_start_utc(delivery_date, period_num).isoformat()} for {delivery_date}"
            )
        price = float(val_str.replace(",", "."))
        records.append({
            "DeliveryDate": pd.Timestamp(delivery_date),
            "Period": period_num,
            "StartTime": ts_utc.tz_convert(DUBLIN_TZ).strftime("%H:%M"),   # display label; repeats on the long day
            "StartUTC": ts_utc,
            "DAMPrice_EUR_MWh": price,
        })

    expected = expected_periods(delivery_date)
    if len(records) != expected:
        raise ValueError(f"{len(records)} periods for {delivery_date}, expected {expected}")

    return pd.DataFrame(records)


# A wind mean needs most of the day behind it. EirGrid's demand feed is
# intermittently empty, which leaves wind_pct NULL for some or all rows; a mean
# over a handful of rows would read as a daily figure, so below this many
# non-NULL rows (75% of the day's half-hours) the wind stats are omitted rather
# than shown. The day is 48 half-hours, or 50 / 46 on the clock-change days.
MIN_WIND_FRACTION = 0.75


def min_wind_rows(delivery_date: date) -> int:
    """75% of expected_periods(delivery_date), rounded up: 36 of 48, 35 of 46, 38 of 50."""
    return math.ceil(expected_periods(delivery_date) * MIN_WIND_FRACTION)   # 0.75 is exact in binary


def wind_summary(wind_pct: pd.Series, demand_mw: pd.Series | None = None, *, delivery_date: date) -> dict:
    """wind_pct_mean/min/max (and demand_mean_mw) from the non-NULL rows only.

    Returns {} when fewer than min_wind_rows(delivery_date) rows have a wind_pct.
    NULL rows are skipped, never treated as zero and never filled.
    """
    pct = pd.to_numeric(wind_pct, errors="coerce").dropna()
    if len(pct) < min_wind_rows(delivery_date):
        return {}
    out = {
        "wind_pct_mean": round(float(pct.mean()), 1),
        "wind_pct_min": round(float(pct.min()), 1),
        "wind_pct_max": round(float(pct.max()), 1),
    }
    if demand_mw is not None:
        demand = pd.to_numeric(demand_mw, errors="coerce").dropna()
        if len(demand):
            out["demand_mean_mw"] = round(float(demand.mean()), 0)
    return out


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
        "median_price": round(float(price.median()), 2),
        "peak_price": round(price.max(), 2),
        "peak_period": int(day.loc[peak_idx, "Period"]),
        "peak_time": day.loc[peak_idx, "StartTime"],
        "min_price": round(price.min(), 2),
        "min_period": int(day.loc[min_idx, "Period"]),
        "min_time": day.loc[min_idx, "StartTime"],
        "price_range": round(price.max() - price.min(), 2),
        "std_dev": round(price.std(), 2),
        "periods_above_150": int((price > 150).sum()),
        "periods_above_200": int((price > 200).sum()),
    }

    # Peak vs off-peak breakdown (07:00–22:00 vs 22:00–07:00)
    try:
        hours = pd.to_numeric(day["StartTime"].str[:2], errors="coerce")
        peak_mask = (hours >= 7) & (hours < 22)
        if peak_mask.any() and (~peak_mask).any():
            summary["peak_mean"] = round(float(price[peak_mask].mean()), 2)
            summary["offpeak_mean"] = round(float(price[~peak_mask].mean()), 2)
            summary["peak_offpeak_spread"] = round(summary["peak_mean"] - summary["offpeak_mean"], 2)
    except Exception:
        pass

    # Condition-based spread: the actual cheapest vs actual dearest 4-period
    # (2h) window in the day, wherever they fall on the clock. Unlike the
    # peak/off-peak split above, this can't invert or get diluted by the SEM
    # day's 23:00 boundary — it just finds the two windows that were
    # genuinely cheap and genuinely dear. Added alongside peak/off-peak
    # rather than replacing it: past posts reference peak_mean/offpeak_mean
    # by name.
    prices_reset = price.reset_index(drop=True)
    if len(prices_reset) >= 4:
        rolling_sum = prices_reset.rolling(4).sum()
        cheap_idx = int(rolling_sum.idxmin())
        dear_idx = int(rolling_sum.idxmax())
        summary["cheap_mean"] = round(float(prices_reset.iloc[cheap_idx - 3:cheap_idx + 1].mean()), 2)
        summary["dear_mean"] = round(float(prices_reset.iloc[dear_idx - 3:dear_idx + 1].mean()), 2)
        summary["arb_spread"] = round(summary["dear_mean"] - summary["cheap_mean"], 2)

    # Wind data if available
    if "WindGeneration_pct" in day.columns:
        wind = wind_summary(day["WindGeneration_pct"], delivery_date=target_date)
        if "wind_pct_mean" in wind:
            summary["wind_pct_mean"] = wind["wind_pct_mean"]
    if "SystemDemand_MW" in day.columns:
        demand = day["SystemDemand_MW"].dropna()
        if len(demand):
            summary["demand_mean_mw"] = round(float(demand.mean()), 0)

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
