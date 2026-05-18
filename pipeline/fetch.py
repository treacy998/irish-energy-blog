"""
fetch.py — EirGrid Smart Grid Dashboard data fetcher

Fetches wind generation and system demand for a given delivery date.
Returns a DataFrame aligned to SEMO's 30-minute half-hourly periods.

No authentication required. Fails gracefully — if the fetch fails,
the pipeline continues without wind data (wind chart is skipped).
"""

import requests
import pandas as pd
from datetime import datetime, date
from pathlib import Path


EIRGRID_BASE = "https://www.smartgriddashboard.com/api/chart/"
TIMEOUT      = 15  # seconds


def fetch_wind_and_demand(delivery_date: date) -> pd.DataFrame | None:
    """
    Fetch wind generation and demand for delivery_date from EirGrid.

    Returns a DataFrame with columns:
        StartTime           datetime (Irish local time, 30-min intervals)
        WindMW              float — wind generation in MW
        DemandMW            float — system demand in MW
        WindGeneration_pct  float — wind as % of demand

    Returns None if the fetch fails for any reason.
    The pipeline continues without wind data if None is returned.
    """
    date_str = delivery_date.strftime("%d-%b-%Y")   # e.g. "17-May-2026"

    wind   = _fetch_area("wind",   date_str)
    demand = _fetch_area("demand", date_str)

    if wind is None or demand is None:
        return None

    # Resample both to 30-minute intervals (EirGrid is 15-min)
    wind   = _resample_30min(wind,   "WindMW")
    demand = _resample_30min(demand, "DemandMW")

    if wind is None or demand is None:
        return None

    # Merge on StartTime
    df = pd.merge(wind, demand, on="StartTime", how="inner")

    # Calculate wind penetration %
    df["WindGeneration_pct"] = (
        (df["WindMW"] / df["DemandMW"].replace(0, pd.NA)) * 100
    ).clip(0, 100).round(1)

    return df


def _fetch_area(area: str, date_str: str) -> pd.DataFrame | None:
    """Fetch a single area (wind or demand) from EirGrid API."""
    try:
        resp = requests.get(
            EIRGRID_BASE,
            params={
                "region":    "ROI",
                "chartType": area,
                "dateRange": "day",
                "dateFrom":  date_str,
                "dateTo":    date_str,
                "areas":     "windactual,windforecast" if area == "wind" else "demandactual,demandforecast",
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        rows = data.get("Rows") or data.get("rows") or []
        if not rows:
            print(f"  [fetch] EirGrid returned no rows for area={area}")
            return None

        records = []
        for row in rows:
            ts_raw = (
                row.get("EffectiveTime")
                or row.get("effectivetime")
                or row.get("DateTime")
            )
            value = row.get("Value") or row.get("value")

            field = row.get("FieldName", "")
            if area == "wind" and field != "WIND_ACTUAL":
                continue
            if area == "demand" and field != "SYSTEM_DEMAND":
                continue

            if ts_raw is None or value is None:
                continue

            for fmt in ("%d-%b-%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M"):
                try:
                    ts = datetime.strptime(ts_raw, fmt)
                    break
                except ValueError:
                    continue
            else:
                continue

            records.append({"StartTime": ts, "value": float(value)})

        if not records:
            print(f"  [fetch] Could not parse any rows for area={area}")
            return None

        return pd.DataFrame(records)

    except requests.RequestException as e:
        print(f"  [fetch] EirGrid request failed for area={area}: {e}")
        return None
    except Exception as e:
        print(f"  [fetch] Unexpected error fetching area={area}: {e}")
        return None


def _resample_30min(df: pd.DataFrame, col_name: str) -> pd.DataFrame | None:
    """Resample 15-minute EirGrid data to 30-minute SEMO periods."""
    try:
        df = df.set_index("StartTime").sort_index()
        df = df["value"].resample("30min").mean()
        df = df.reset_index()
        df.columns = ["StartTime", col_name]
        df = df.dropna()
        return df
    except Exception as e:
        print(f"  [fetch] Resample failed: {e}")
        return None
