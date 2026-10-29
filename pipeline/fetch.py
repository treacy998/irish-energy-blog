"""
fetch.py — EirGrid Smart Grid Dashboard data fetcher + SEMOpx DAM fetcher

Fetches wind generation and system demand for a given delivery date.
Returns a DataFrame aligned to SEMO's 30-minute half-hourly periods.

No authentication required. Fails gracefully — if the fetch fails,
the pipeline continues without wind data (wind chart is skipped).
"""

import contextlib
import io
import json
import os
import random
import requests
import time
import pandas as pd
from datetime import datetime, date, timedelta
from pathlib import Path

from trading_day import DUBLIN_TZ, eirgrid_local_to_utc, placeable_halfhours, trading_day_start_utc

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"


EIRGRID_BASE  = "https://www.smartgriddashboard.com/api/chart/"
SEMOPX_BASE   = "https://reports.semopx.com"
TIMEOUT       = 15  # seconds: connect timeout for every request, and the whole-request timeout for SEMOpx
TIMEOUT_DL    = 60  # seconds — download

# ── EirGrid retry ────────────────────────────────────────────────────────────
# EirGrid's chart endpoints intermittently answer 200 with {"Rows":[]} (or time out) for minutes at a
# time, from every client. A fetch whose area has fewer non-null half-hours than the day can supply
# (trading_day.placeable_halfhours) is retried, all incomplete areas in the same round so the waits
# are shared. Settings come from the environment:
#   EIRGRID_ATTEMPTS        attempts per fetch (>=1). Default 10 when CI is set, else 1 (no retry).
#   EIRGRID_RETRY_MIN_S     shortest wait between rounds, default 60
#   EIRGRID_RETRY_MAX_S     longest wait between rounds, default 90 (each wait is uniform in [min, max])
#   EIRGRID_READ_TIMEOUT_S  per-request read timeout, default 30 (connect timeout stays TIMEOUT)
# Worst case per fetch (every request times out): attempts x 2 areas x (TIMEOUT + READ) + (attempts-1) x MAX.
_sleep = time.sleep           # tests replace these two
_jitter = random.uniform
ATTEMPT_LOG: list[dict] = []  # one entry per request, in order; also printed and summarised


def _env_num(name: str, default: float, cast=float):
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return cast(raw)
    except ValueError:
        print(f"  [fetch] ignoring {name}={raw!r}: not a number")
        return default


def configured_attempts(ci: bool | None = None) -> int:
    """Attempts per EirGrid fetch: EIRGRID_ATTEMPTS if set, else 10 in CI and 1 elsewhere.
    ci=True forces the CI default (ci_daily's own fetches); None reads the CI environment variable."""
    in_ci = bool(os.environ.get("CI")) if ci is None else ci
    return max(1, int(_env_num("EIRGRID_ATTEMPTS", 10 if in_ci else 1, int)))


def read_timeout_s() -> float:
    return _env_num("EIRGRID_READ_TIMEOUT_S", 30.0)


def retry_gap_s() -> float:
    lo, hi = _env_num("EIRGRID_RETRY_MIN_S", 60.0), _env_num("EIRGRID_RETRY_MAX_S", 90.0)
    return _jitter(min(lo, hi), max(lo, hi))


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
    delivery_date: date, out_dir: Path | str = DEFAULT_DATA_DIR, overwrite_raw: bool = True,
    prefer_archive: bool = False, attempts: int | None = None,
) -> pd.DataFrame | None:
    """
    Fetch wind generation and demand for delivery_date from EirGrid.

    The frame covers the SEM trading day (local 23:00 the evening before to
    23:00), not EirGrid's calendar day: the evening-before half-hours come from
    the previous date's raw archive (no extra request; NaN if it is missing),
    and the calendar day's final 23:00-24:00 belongs to the next trading day
    and is dropped. See combine_for_trading_day.

    Returns a DataFrame with columns:
        StartTime            datetime (Irish local time, 30-min intervals; display only —
                             repeats 01:00–02:00 on the autumn change day)
        StartUTC             datetime64[UTC] — the key to join on, unique per half-hour
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
    row, and writes a response only if it has rows and the archive is missing
    or empty. Backfills and heals use it so a re-fetch never replaces the raw
    JSON a published post was written from, and never writes an empty one; a
    zero-row file is a failed fetch, not a record worth protecting.

    prefer_archive=True uses an area's archived response (no request) when that archive is complete
    for the date (placeable_halfhours), and fetches live for an area whose archive is missing, empty
    or incomplete: an incomplete file is not evidence of what EirGrid published. CI uses it so a
    retry after a run that archived the raw files but died before publishing is generated from
    the archived bytes, not from a fresh response that may differ.

    attempts (default configured_attempts(): 10 in CI, 1 elsewhere) is how many times an area that is
    still incomplete is requested; both areas share the rounds and the waits between them. The most
    complete response is the one archived and used. See the retry notes at the top of this module.

    Note: EirGrid's demand endpoint does not return a forecast field for this
    region/chart combination (only SYSTEM_DEMAND) — there is no DemandForecastMW.
    """
    areas = ("wind", "demand")
    need = placeable_halfhours(delivery_date)
    resolved: dict[str, pd.DataFrame | None] = {}
    keep: dict[str, tuple[int, bytes]] = {}     # area -> (archived half-hours, archived bytes), to compare after a live try
    live: list[str] = []
    for name in areas:
        if not prefer_archive:
            live.append(name)
            continue
        have = archived_halfhours(delivery_date, name, out_dir)
        if have >= need:
            archived = load_archived_area(delivery_date, name, out_dir)
            if archived is not None:
                resolved[name] = archived
                continue
        live.append(name)
        if have > 0:
            # An archive with some rows but fewer than the day has is not evidence of what EirGrid
            # published (it was saved before the feed was complete): fetch live. If that is no better,
            # keep the archived bytes, so the day is never generated from a worse file than we had.
            print(f"  [fetch] archived {name} for {delivery_date} holds {have} of {need} half-hours; "
                  f"treating it as absent and fetching live")
            keep[name] = (have, archive_path(delivery_date, name, out_dir).read_bytes())
    if live:
        fetched = fetch_areas(delivery_date, live, out_dir=out_dir, overwrite_raw=overwrite_raw, attempts=attempts)
        for name in live:
            frame = fetched[name]
            if name in keep:
                have, old = keep[name]
                if frame is None or archived_halfhours(delivery_date, name, out_dir) < have:
                    archive_path(delivery_date, name, out_dir).write_bytes(old)
                    print(f"  [fetch] live {name} for {delivery_date} is no better; keeping the archived file")
                    frame = load_archived_area(delivery_date, name, out_dir)
            resolved[name] = frame

    wind, demand = resolved["wind"], resolved["demand"]
    prev_wind, prev_demand = load_archived_previous_day(delivery_date, out_dir)
    return combine_for_trading_day(delivery_date, wind, demand, prev_wind, prev_demand)


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

    # Merge on StartUTC (a local clock label repeats on the autumn change day) —
    # demand and forecast are left-joined since either may be absent
    if demand_30 is not None:
        df = pd.merge(wind_actual, demand_30[["StartUTC", "DemandMW"]], on="StartUTC", how="left")
    else:
        df = wind_actual.copy()
        df["DemandMW"] = float("nan")
    if wind_forecast is not None:
        df = pd.merge(df, wind_forecast[["StartUTC", "WindForecastMW"]], on="StartUTC", how="left")
    else:
        df["WindForecastMW"] = pd.NA

    df["WindGeneration_pct"] = compute_wind_pct(df["WindMW"], df["DemandMW"])

    return df


def load_archived_previous_day(delivery_date: date, out_dir: Path | str = DEFAULT_DATA_DIR):
    """(wind, demand) area rows from the archive of delivery_date - 1, offline.
    Either is None if that archive is missing or empty."""
    prev = delivery_date - timedelta(days=1)
    return load_archived_area(prev, "wind", out_dir), load_archived_area(prev, "demand", out_dir)


def combine_for_trading_day(
    delivery_date: date,
    wind: pd.DataFrame | None, demand: pd.DataFrame | None,
    prev_wind: pd.DataFrame | None = None, prev_demand: pd.DataFrame | None = None,
) -> pd.DataFrame | None:
    """The shared join input: wind/demand half-hours for the SEM trading day of delivery_date.

    A price period gets the EirGrid reading at its own start_utc. EirGrid serves
    one calendar day per request, so the evening-before periods (periods 1-2 in
    summer: 23:00 and 23:30) live in the previous date's response; the same-day
    response's 23:00 is the NEXT trading day's period 1 and is excluded. With
    no previous-day frames those half-hours are simply absent (NaN once joined).
    Returns None if the day's own wind is unavailable, as combine_wind_and_demand does."""
    today = combine_wind_and_demand(wind, demand)
    if today is None:
        return None
    frames = [f for f in (combine_wind_and_demand(prev_wind, prev_demand), today) if f is not None]
    df = pd.concat(frames, ignore_index=True)
    start = pd.Timestamp(trading_day_start_utc(delivery_date))
    end = pd.Timestamp(trading_day_start_utc(delivery_date + timedelta(days=1)))
    df = df[(df["StartUTC"] >= start) & (df["StartUTC"] < end)]
    return df.drop_duplicates("StartUTC", keep="last").sort_values("StartUTC").reset_index(drop=True)


def compute_wind_pct(wind_mw: pd.Series, demand_mw: pd.Series) -> pd.Series:
    """Wind as % of demand, clipped to 0-100 and rounded to 1 dp. NaN demand stays
    NaN (never 0); zero demand is treated as missing rather than divided by."""
    demand_nonzero = demand_mw.where(demand_mw != 0)
    return ((wind_mw / demand_nonzero) * 100).clip(0, 100).round(1)


def resample_demand(demand: pd.DataFrame) -> pd.DataFrame | None:
    """30-minute StartTime/StartUTC/DemandMW rows from parsed demand area rows (None if unusable)."""
    return _resample_30min(demand, "DemandMW")


def archive_path(delivery_date: date, area: str, out_dir: Path | str = DEFAULT_DATA_DIR) -> Path:
    return Path(out_dir) / "eirgrid_raw" / delivery_date.isoformat() / f"{area}.json"


def archive_row_count(path: Path) -> int:
    """Data rows in an archived EirGrid response. 0 if missing, empty or unparseable."""
    try:
        data = json.loads(path.read_text())
        return len(data.get("Rows") or data.get("rows") or [])
    except (OSError, ValueError, AttributeError):
        return 0


PRIMARY_FIELD = {"wind": "WIND_ACTUAL", "demand": "SYSTEM_DEMAND"}


def data_halfhours(data, area: str) -> int:
    """Non-null half-hour readings of the area's main series (WIND_ACTUAL / SYSTEM_DEMAND) in a parsed
    EirGrid response, placed on UTC as the pipeline places them. 0 if it is empty or unparseable.
    Compare with trading_day.placeable_halfhours(date)."""
    if not isinstance(data, dict) or not (data.get("Rows") or data.get("rows")):
        return 0
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            df = _parse_area(data, area, [PRIMARY_FIELD[area]])
            out = _resample_30min(df, "v") if df is not None else None
    except Exception:
        return 0
    return 0 if out is None else len(out)


def path_halfhours(path: Path, area: str) -> int:
    """data_halfhours of an EirGrid response file. 0 if the file is missing, empty or unparseable."""
    if archive_row_count(path) == 0:
        return 0
    try:
        return data_halfhours(json.loads(path.read_text()), area)
    except (OSError, ValueError):
        return 0


def archived_halfhours(delivery_date: date, area: str, out_dir: Path | str = DEFAULT_DATA_DIR) -> int:
    return path_halfhours(archive_path(delivery_date, area, out_dir), area)


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


class _Job:
    """One area of one delivery date across the retry rounds: the best response seen so far."""
    def __init__(self, area: str, delivery_date: date, need: int):
        self.area, self.date, self.need = area, delivery_date, need
        self.text: str | None = None
        self.data = None
        self.halfhours = -1          # -1: no response at all yet
        self.last_exc: Exception | None = None

    @property
    def complete(self) -> bool:
        return self.halfhours >= self.need


def _query_params(area: str, date_str: str) -> dict:
    return {
        "region":    "ROI",
        "chartType": "generation" if area == "demand" else area,
        "dateRange": "day",
        "dateFrom":  date_str,
        "dateTo":    date_str,
        "areas":     "windactual,windforecast" if area == "wind" else "demandactual,demandforecast",
    }


def _request_once(job: _Job, k: int, n: int, raise_errors: bool) -> None:
    entry = {"date": job.date.isoformat(), "area": job.area, "attempt": k, "of": n, "need": job.need,
             "status": None, "bytes": 0, "rows": 0, "halfhours": 0, "elapsed": 0.0, "error": None}
    t0 = time.monotonic()
    try:
        resp = requests.get(EIRGRID_BASE, params=_query_params(job.area, job.date.strftime("%d-%b-%Y")),
                            timeout=(TIMEOUT, read_timeout_s()))
        entry["status"] = getattr(resp, "status_code", None)
        resp.raise_for_status()
        if raise_errors and resp.status_code != 200:
            raise requests.HTTPError(f"HTTP {resp.status_code} (expected 200)", response=resp)
        text = resp.text
        entry["bytes"] = len(text.encode("utf-8"))
        try:
            data = resp.json()
        except ValueError:
            data = None
        entry["rows"] = len(data.get("Rows") or data.get("rows") or []) if isinstance(data, dict) else 0
        entry["halfhours"] = data_halfhours(data, job.area)
        if entry["halfhours"] > job.halfhours:           # strictly: on a tie the earlier response is kept
            job.text, job.data, job.halfhours = text, data, entry["halfhours"]
    except Exception as e:                               # timeout, connection reset, HTTP error, anything
        job.last_exc = e
        entry["error"] = f"{type(e).__name__}: {e}"[:140]
        status = getattr(getattr(e, "response", None), "status_code", None)
        entry["status"] = entry["status"] or status
    entry["elapsed"] = round(time.monotonic() - t0, 1)
    ATTEMPT_LOG.append(entry)
    got = f"HTTP {entry['status']}, {entry['bytes']:,} B, {entry['rows']} rows, " \
          f"{entry['halfhours']}/{job.need} half-hours" if not entry["error"] else f"FAILED ({entry['error']})"
    print(f"  [eirgrid] {entry['date']} {job.area} attempt {k}/{n}: {got}, {entry['elapsed']} s")


def _append_step_summary(entries: list[dict]) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path or not entries:
        return
    lines = ["", "### EirGrid fetch attempts", "",
             "| date | area | attempt | HTTP | bytes | data rows | non-null half-hours | elapsed (s) | result |",
             "|---|---|---|---|---|---|---|---|---|"]
    for e in entries:
        result = e["error"] or ("complete" if e["halfhours"] >= e["need"] else "incomplete")
        lines.append(f"| {e['date']} | {e['area']} | {e['attempt']}/{e['of']} | {e['status'] or ''} | {e['bytes']} | "
                     f"{e['rows']} | {e['halfhours']}/{e['need']} | {e['elapsed']} | {result} |")
    try:
        with open(path, "a") as f:
            f.write("\n".join(lines) + "\n")
    except OSError:
        pass


def fetch_areas(delivery_date: date, areas: list[str] | tuple[str, ...], out_dir: Path | str = DEFAULT_DATA_DIR,
                overwrite_raw: bool = True, raise_errors: bool = False,
                attempts: int | None = None) -> dict[str, pd.DataFrame | None]:
    """Live-fetch EirGrid areas (wind, demand) for delivery_date, retrying until each has the day's half-hours.

    Round k requests every area still short of placeable_halfhours(delivery_date); the rounds share one
    wait (EIRGRID_RETRY_MIN_S..MAX_S, jittered) and stop at the first round in which all are complete or
    after `attempts` rounds (default configured_attempts()). Each attempt is logged, and a table of them is
    appended to $GITHUB_STEP_SUMMARY. The most complete response per area (the earlier on a tie) is the
    one archived and parsed, under the archive rules below, which are unchanged:

    An archive that has rows is never replaced by a response that has none, in any mode: EirGrid's feeds
    go empty for minutes at a time, and an empty answer is not a better record than the data the store
    and the posts were built from. overwrite_raw=True (run_daily's default) otherwise archives the best
    response, including an empty one where there is no archive yet (a record of the failed fetch).
    overwrite_raw=False (backfill, heal) only archives a response that has rows, and only where the
    archive is missing or has none.

    raise_errors=True re-raises the last request error (or a non-200 status) for an area that never got
    any response, instead of printing it and returning None, so a caller can report why a fetch failed.
    An empty or unparseable 200 response still returns None either way."""
    n = max(1, attempts if attempts is not None else configured_attempts())
    need = placeable_halfhours(delivery_date)
    jobs = {a: _Job(a, delivery_date, need) for a in areas}
    first = len(ATTEMPT_LOG)
    for k in range(1, n + 1):
        pending = [j for j in jobs.values() if not j.complete]
        if not pending:
            break
        for j in pending:
            _request_once(j, k, n, raise_errors)
        if k < n and any(not j.complete for j in jobs.values()):
            gap = retry_gap_s()
            short = ", ".join(f"{j.area} {max(j.halfhours, 0)}/{need}" for j in jobs.values() if not j.complete)
            print(f"  [eirgrid] {delivery_date.isoformat()} incomplete after attempt {k}/{n} ({short}); retrying in {gap:.0f} s")
            _sleep(gap)
    _append_step_summary(ATTEMPT_LOG[first:])

    results, failure = {}, None
    for a, j in jobs.items():
        results[a] = _finish(j, archive_path(delivery_date, a, out_dir).parent, overwrite_raw)
        if j.text is None:
            failure = failure or j
    if failure is not None:
        if raise_errors and failure.last_exc is not None:
            raise failure.last_exc
        print(f"  [fetch] EirGrid request failed for area={failure.area}: {failure.last_exc}")
    return results


def _finish(job: _Job, raw_dir: Path, overwrite_raw: bool) -> pd.DataFrame | None:
    """Archive the job's best response (under the archive rules) and parse it."""
    if job.text is None:                      # every attempt failed: nothing to archive or parse
        return None
    has_rows = isinstance(job.data, dict) and bool(job.data.get("Rows") or job.data.get("rows"))
    raw_path = raw_dir / f"{job.area}.json"
    existing_rows = archive_row_count(raw_path)
    if has_rows and (overwrite_raw or existing_rows == 0):
        write_raw = True
    else:
        write_raw = overwrite_raw and existing_rows == 0
    if write_raw:
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(job.text)
    if job.data is None:
        print(f"  [fetch] EirGrid returned non-JSON for area={job.area}")
        return None
    try:
        return _parse_area(job.data, job.area, AREA_FIELDS[job.area])
    except Exception as e:
        print(f"  [fetch] Unexpected error parsing area={job.area}: {e}")
        return None


def fetch_area(delivery_date: date, area: str, out_dir: Path | str = DEFAULT_DATA_DIR,
               overwrite_raw: bool = True, raise_errors: bool = False,
               attempts: int | None = None) -> pd.DataFrame | None:
    """Live-fetch one area (wind or demand) for delivery_date, archiving the raw response. See fetch_areas."""
    return fetch_areas(delivery_date, [area], out_dir=out_dir, overwrite_raw=overwrite_raw,
                       raise_errors=raise_errors, attempts=attempts)[area]


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
        # `is None`, not truthiness: a genuine Value of 0 (no wind) is data, not a gap.
        value = row.get("Value")
        if value is None:
            value = row.get("value")

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
    """Resample 15-minute EirGrid data to 30-minute SEMO periods.

    EirGrid timestamps are Irish local clock time, so they are converted to UTC
    first (see eirgrid_local_to_utc) and binned there; local time is derived
    back from UTC for display only. Rows whose local label can't be placed
    (the single-listed hour on the long day) are dropped, never guessed."""
    try:
        utc = eirgrid_local_to_utc(df["StartTime"])
        unplaced = int(utc.isna().sum())
        if unplaced:
            print(f"  [fetch] {col_name}: {unplaced} row(s) in an ambiguous clock-change hour left unplaced")
        series = pd.Series(df["value"].to_numpy(), index=pd.DatetimeIndex(utc.to_numpy(), tz="UTC"))
        series = series[series.index.notna()].sort_index().resample("30min").mean().dropna()
        out = pd.DataFrame({
            "StartTime": series.index.tz_convert(DUBLIN_TZ).tz_localize(None),
            "StartUTC": series.index,
            col_name: series.to_numpy(),
        })
        return out
    except Exception as e:
        print(f"  [fetch] Resample failed: {e}")
        return None
