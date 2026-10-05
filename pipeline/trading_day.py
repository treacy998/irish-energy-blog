"""
trading_day.py — the one place that maps SEM trading-day periods to instants.

The SEM trading day runs 23:00 to 23:00 Irish local time, so it is 24 hours
long except on the two clock-change days: 25 hours (50 periods) when the
clocks go back, 23 hours (46 periods) when they go forward. The 22:00Z–21:30Z
window of a summer-time file is a summer fact, not a rule; the invariant is
local 23:00 on the previous calendar day.

All arithmetic here is done on aware UTC datetimes. Local time is produced
only for display (labels), never added to or subtracted from.
"""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

DUBLIN_TZ = ZoneInfo("Europe/Dublin")
UTC = timezone.utc
PERIOD = timedelta(minutes=30)


def trading_day_start_utc(delivery_date: date) -> datetime:
    """UTC instant of period 1: local 23:00 on the calendar day before delivery_date."""
    prev = delivery_date - timedelta(days=1)
    # 23:00 is never ambiguous or skipped (clocks change at 01:00/02:00).
    return datetime(prev.year, prev.month, prev.day, 23, 0, tzinfo=DUBLIN_TZ).astimezone(UTC)


def expected_periods(delivery_date: date) -> int:
    """Half-hour periods in the trading day: 50 (clocks back), 46 (clocks forward), else 48."""
    span = trading_day_start_utc(delivery_date + timedelta(days=1)) - trading_day_start_utc(delivery_date)
    return span // PERIOD


def period_start_utc(delivery_date: date, period: int) -> datetime:
    """UTC start of 1-based `period`; ValueError if it is outside that day's period range."""
    n = expected_periods(delivery_date)
    if not 1 <= period <= n:
        raise ValueError(f"period {period} outside 1..{n} for {delivery_date}")
    return trading_day_start_utc(delivery_date) + PERIOD * (period - 1)


def period_starts_utc(delivery_date: date) -> list[datetime]:
    return [period_start_utc(delivery_date, n) for n in range(1, expected_periods(delivery_date) + 1)]


def local_label(instant_utc: datetime) -> str:
    """Display only: Irish local HH:MM. Repeats 01:00–02:00 on the long day."""
    return instant_utc.astimezone(DUBLIN_TZ).strftime("%H:%M")


def period_labels(delivery_date: date) -> list[str]:
    return [local_label(t) for t in period_starts_utc(delivery_date)]


def iso_z(instant_utc) -> str:
    """Stable text form for storage: 2025-10-25T22:00:00Z."""
    return pd.Timestamp(instant_utc).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def period_label_indices(delivery_date: date, label: str) -> list[int]:
    """0-based period indices whose local label is `label` (two on the repeated hour)."""
    return [i for i, lab in enumerate(period_labels(delivery_date)) if lab == label]


def eirgrid_local_to_utc(local_times: pd.Series) -> pd.Series:
    """Convert EirGrid's naive Irish-local timestamps to aware UTC.

    The dashboard reports local clock time over the calendar day, so on the
    long day the 01:00–02:00 labels are ambiguous. A label that appears twice
    in a series is the repeated hour (first listed = first pass). A label that
    appears once inside the ambiguous hour cannot be placed, so it becomes NaT
    rather than a guess. Labels that don't exist (spring gap) are NaT too.
    """
    s = pd.to_datetime(local_times).reset_index(drop=True)
    occurrence = s.groupby(s).cumcount()
    repeated = s.duplicated(keep=False)
    plain = s.dt.tz_localize(DUBLIN_TZ, ambiguous="NaT", nonexistent="NaT")
    ambiguous = plain.isna() & s.notna()
    placed = s.dt.tz_localize(DUBLIN_TZ, ambiguous=(occurrence == 0).to_numpy(), nonexistent="NaT")
    out = plain.where(~(ambiguous & repeated), placed)
    return out.dt.tz_convert("UTC").set_axis(local_times.index)


def calendar_label_to_utc(calendar_date: date, label: str):
    """UTC instant of local `label` ("HH:MM") on `calendar_date`, or None if that
    wall-clock time is ambiguous or doesn't exist (clock-change hours)."""
    naive = pd.Timestamp(f"{calendar_date.isoformat()} {label}")
    try:
        return naive.tz_localize(DUBLIN_TZ).tz_convert("UTC")
    except Exception:       # AmbiguousTimeError / NonExistentTimeError
        return None
