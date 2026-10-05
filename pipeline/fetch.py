"""
fetch.py — EirGrid Smart Grid Dashboard data fetcher + SEMOpx DAM fetcher

Fetches wind generation and system demand for a given delivery date.
Returns a DataFrame aligned to SEMO's 30-minute half-hourly periods.

No authentication required. Fails gracefully — if the fetch fails,
the pipeline continues without wind data (wind chart is skipped).
"""

import json
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"


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


AREA_FIELDS = {
    "wind":   ["WIND_ACTUAL", "WIND_FCAST"],
    "demand": ["SYSTEM_DEMAND"],
}


def fetch_wind_and_demand(
    delivery_date: date, out_dir: Path | str = DEFAULT_DATA_DIR, overwrite_raw: bool = True
) -> pd.DataFrame | None:
    """
    Fetch wind generation and demand for delivery_date from EirGrid.

    Returns a DataFrame with columns:
        StartTime            datetime (Irish local time, 30-min intervals)
        WindMW               float — wind generation in MW
        WindForecastMW       float — day-ahead wind forecast in MW (NaN where unavailable)
        DemandMW             float — system demand in MW (NaN where the demand feed was empty)
        WindGeneration_pct   float — wind as % of demand (NaN where DemandMW is NaN)

    Returns None only if wind is unavailable. EirGrid's demand endpoint
    intermittently returns {"Rows":[]} for minutes at a time while wind is
    unaffected, so an empty demand feed yields the wind rows with DemandMW and
    WindGeneration_pct NaN (stored as NULL) — never 0, never filled. Callers
    that need a wind % must check WindGeneration_pct.notna().
    The pipeline continues without wind data if None is returned.

    The raw EirGrid JSON response for each area is archived to
    out_dir/eirgrid_raw/<delivery_date>/<area>.json before parsing, so the
    published figures stay reproducible from disk even if EirGrid's
    historical window later ages the live query out.

    overwrite_raw=False keeps any archive on disk that holds at least one data
    row and only writes missing or zero-row files. Backfills use it so a
    re-fetch never replaces the raw JSON a published post was written from;
    a zero-row file is a failed fetch, not a record worth protecting.

    Note: EirGrid's demand endpoint does not return a forecast field for this
    region/chart combination (only SYSTEM_DEMAND) — there is no DemandForecastMW.
    """
    wind   = fetch_area(delivery_date, "wind",   out_dir=out_dir, overwrite_raw=overwrite_raw)
    demand = fetch_area(delivery_date, "demand", out_dir=out_dir, overwrite_raw=overwrite_raw)
    return combine_wind_and_demand(wind, demand)


def combine_wind_and_demand(wind: pd.DataFrame | None, demand: pd.DataFrame | None) -> pd.DataFrame | None:
    """Build the 30-minute wind/demand frame from parsed wind and demand area rows
    (from fetch_area or load_archived_area).

    Wind is required: returns None if it is missing. Demand is optional — if it
    is None (feed empty) or has no usable rows, every wind row is kept with
    DemandMW and WindGeneration_pct NaN. Demand is left-joined for the same
    reason, so a wind row is never dropped for lack of a demand match."""
    if wind is None:
        return None

    wind_actual = _resample_30min(wind[wind["field"] == "WIND_ACTUAL"], "WindMW")
    if wind_actual is None:
        return None
    wind_forecast = _resample_30min(wind[wind["field"] == "WIND_FCAST"], "WindForecastMW")
    demand_30     = _resample_30min(demand, "DemandMW") if demand is not None else None

    # Merge on StartTime — demand and forecast are left-joined since either may be absent
    if demand_30 is not None:
        df = pd.merge(wind_actual, demand_30, on="StartTime", how="left")
    else:
        df = wind_actual.copy()
        df["DemandMW"] = float("nan")
    if wind_forecast is not None:
        df = pd.merge(df, wind_forecast, on="StartTime", how="left")
    else:
        df["WindForecastMW"] = pd.NA

    # Wind penetration %. NaN demand stays NaN (never 0); zero demand is treated as missing.
    demand_nonzero = df["DemandMW"].where(df["DemandMW"] != 0)
    df["WindGeneration_pct"] = ((df["WindMW"] / demand_nonzero) * 100).clip(0, 100).round(1)

    return df


def archive_path(delivery_date: date, area: str, out_dir: Path | str = DEFAULT_DATA_DIR) -> Path:
    return Path(out_dir) / "eirgrid_raw" / delivery_date.isoformat() / f"{area}.json"


def archive_row_count(path: Path) -> int:
    """Data rows in an archived EirGrid response. 0 if missing, empty or unparseable."""
    try:
        data = json.loads(path.read_text())
        return len(data.get("Rows") or data.get("rows") or [])
    except (OSError, ValueError, AttributeError):
        return 0


def load_archived_area(delivery_date: date, area: str, out_dir: Path | str = DEFAULT_DATA_DIR) -> pd.DataFrame | None:
    """Parse an archived area response with the same parser the live fetch uses.
    No network call. Returns None if the archive is missing, has no rows, or won't parse."""
    path = archive_path(delivery_date, area, out_dir)
    if archive_row_count(path) == 0:
        return None
    try:
        return _parse_area(json.loads(path.read_text()), area, AREA_FIELDS[area])
    except Exception as e:
        print(f"  [fetch] Could not parse archive {path}: {e}")
        return None


def fetch_area(delivery_date: date, area: str, out_dir: Path | str = DEFAULT_DATA_DIR,
               overwrite_raw: bool = True) -> pd.DataFrame | None:
    """Live-fetch one area (wind or demand) for delivery_date, archiving the raw response."""
    return _fetch_area(
        area, delivery_date.strftime("%d-%b-%Y"),   # e.g. "17-May-2026"
        raw_dir=archive_path(delivery_date, area, out_dir).parent,
        fields=AREA_FIELDS[area], overwrite_raw=overwrite_raw,
    )


def _fetch_area(area: str, date_str: str, raw_dir: Path | None = None, fields: list[str] | None = None,
                overwrite_raw: bool = True) -> pd.DataFrame | None:
    """Fetch a single area (wind or demand) from EirGrid API.

    fields restricts which FieldName values are kept (e.g. ["WIND_ACTUAL", "WIND_FCAST"]).
    Returned rows carry a 'field' column so callers can split multi-field areas like wind.
    """
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

        if raw_dir is not None:
            raw_path = raw_dir / f"{area}.json"
            if overwrite_raw or archive_row_count(raw_path) == 0:
                raw_dir.mkdir(parents=True, exist_ok=True)
                raw_path.write_text(resp.text)

        return _parse_area(resp.json(), area, fields)

    except requests.RequestException as e:
        print(f"  [fetch] EirGrid request failed for area={area}: {e}")
        return None
    except Exception as e:
        print(f"  [fetch] Unexpected error fetching area={area}: {e}")
        return None


def _parse_area(data: dict, area: str, fields: list[str] | None = None) -> pd.DataFrame | None:
    """Parse an EirGrid chart response (live or archived) into StartTime/value/field rows."""
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
        if fields is not None and field not in fields:
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

        records.append({"StartTime": ts, "value": float(value), "field": field})

    if not records:
        print(f"  [fetch] Could not parse any rows for area={area}")
        return None

    return pd.DataFrame(records)


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
