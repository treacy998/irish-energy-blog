"""
fetch.py — EirGrid Smart Grid Dashboard data fetcher + SEMOpx DAM fetcher

Fetches wind generation and system demand for a given delivery date.
Returns a DataFrame aligned to SEMO's 30-minute half-hourly periods.

No authentication required. Fails gracefully — if the fetch fails,
the pipeline continues without wind data (wind chart is skipped).
"""

import requests
import pandas as pd
from datetime import datetime, date, timedelta
from pathlib import Path


EIRGRID_BASE  = "https://www.smartgriddashboard.com/api/chart/"
SEMOPX_BASE   = "https://reports.semopx.com"
TIMEOUT       = 15  # seconds
TIMEOUT_DL    = 60  # seconds — download


def fetch_semo(delivery_date: date | str | None = None, out_dir: Path | str = "data") -> Path:
    """
    Fetch the EA-001 ETS Market Results CSV from SEMOpx.

    delivery_date is the market delivery date (the date in the blog post title).
    When omitted, the most recently published DA report is returned — useful for
    the daily automation where you just want the latest available file.

    If a matching file already exists in out_dir, it is returned immediately
    without re-downloading.

    Raises FileNotFoundError if the API returns no matching report.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if delivery_date is not None:
        if isinstance(delivery_date, str):
            delivery_date = date.fromisoformat(delivery_date)
        # DA reports use DateRetention = trading date = delivery_date - 1
        trade_date = delivery_date - timedelta(days=1)
        # Avoid re-downloading a file we already have for this trading date.
        stamp = trade_date.strftime("%Y%m%d")
        existing = list(out_dir.glob(f"MarketResult_SEM-DA_PWR-MRC-D+1_{stamp}*.csv"))
        if existing:
            return existing[0]
        params: dict = {
            "DPuG_ID":       "EA-001",
            "DateRetention": trade_date.isoformat(),
            "page_size":     10,
            "sort_by":       "PublishTime",
            "order_by":      "DESC",
        }
    else:
        params = {
            "DPuG_ID":  "EA-001",
            "page_size": 20,
            "sort_by":   "PublishTime",
            "order_by":  "DESC",
        }

    resp = requests.get(
        f"{SEMOPX_BASE}/api/v1/documents/static-reports",
        params=params,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])

    target = next(
        (i for i in items if i.get("ResourceName", "").startswith("MarketResult_SEM-DA_PWR-MRC-D+1_")),
        None,
    )
    if target is None:
        label = delivery_date.isoformat() if delivery_date else "latest"
        raise FileNotFoundError(f"No SEM-DA market result CSV found ({label})")

    resource_name = target["ResourceName"]
    out_path = out_dir / resource_name
    if out_path.exists():
        return out_path

    with requests.get(f"{SEMOPX_BASE}/documents/{resource_name}", timeout=TIMEOUT_DL, stream=True) as dl:
        dl.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in dl.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    return out_path


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
                "chartType": "generation" if area == "demand" else area,
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
