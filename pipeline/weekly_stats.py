"""
weekly_stats.py — weekly_summary(week_start, conn): the numbers behind a weekly post.

A pure function over data/history.db's market_prices (every price figure) and
system_conditions (wind_mw only). It returns plain numbers, strings and lists,
no formatting, and never reads anything dated after the target week, so a
regenerated result is reproducible however much newer data the store holds.

Definitions (stated once, here):

  Week      Monday to Sunday of delivery dates. week_start must be a Monday. All
            7 days must be in the store with expected_periods(day) rows (48; 50
            or 46 on the clock-change days) or the function raises ValueError:
            it never computes on partial data. A baseline week that is incomplete
            is not counted, and n says how many were.

  Means     week_mean is the mean over every price row in the week, so a 50-period
            day counts 50 times. daily_means are per-day means. week_mean_c_per_kwh
            is the unrounded week_mean / 10, rounded to 2 dp.

  Baselines Both exclude the target week and anything later.
    trailing  the 13 calendar weeks immediately before the target, counting only
              complete ones (n <= 13).
    seasonal  weeks starting 364 days before the target, +/- 14 days (5 weekday-
              aligned weeks), complete ones only. Fewer than 4 complete weeks:
              "seasonal" is None and "seasonal_reason" says why. Prices only; the
              store has no wind or demand before May 2026.
    n is always returned. Below 8 (trailing) or 4 (seasonal) complete weeks every
    rank, "since" and verdict for that baseline is None, with a reason.

  Rank      1 + the number of baseline weeks strictly dearer (higher mean, or
            higher median arb spread), so 1 = dearest and ties share a rank.
            "rank_of" is n + 1: the baseline weeks plus this one.

  Since     "dearest_since" is the start of the most recent earlier week that was
            at least as dear as this one (its week_mean >= this week_mean);
            "cheapest_since" is the most recent earlier week at least as cheap
            (week_mean <= this one). None if there is no such week. For the
            trailing baseline the search covers every complete earlier week in the
            store; for the seasonal baseline it covers only the seasonal weeks.

  Percentile  100 * (baseline weeks strictly below this value + half the baseline
            weeks equal to it) / n. One method, used for every verdict.

  Verdicts  price: "normal" for percentile 20..80 inclusive; "dearer" above 80,
            "cheaper" below 20; "unusually dearer" above 95, "unusually cheaper"
            below 5. volatility (from the median daily arb_spread) uses the same
            thresholds with "more volatile" / "calmer". arb_spread is
            process.daily_summary()'s condition-based spread: the dearest 4-period
            block minus the cheapest, wherever they fall, so it is a measure of
            shape and says nothing about whether the spread could be traded.

  Chart/text inputs  each baseline also returns "means", its weeks' means in the
            order of "weeks" (most recent first), even when its rank and verdict are
            suppressed: they are facts, not claims. "previous_week_mean" is the mean of
            the week before the target (None if that week is incomplete) and
            "same_week_last_year" is {"week_start", "mean"} for the week starting 364
            days earlier (None if that week is not complete in the store).

  Wind      wind_mw_mean is the mean of the week's non-NULL wind_mw; wind_coverage
            is the share of the week's periods that have a wind_mw (nothing is
            imputed). wind_mw_trailing_median is the median of trailing weeks whose
            own coverage is at least 75%, None unless at least 8 such weeks.
"""

import sqlite3
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from process import daily_summary
from trading_day import expected_periods

TRAILING_WEEKS = 13
SEASONAL_CENTRE_DAYS = 364
SEASONAL_SPAN_WEEKS = 2          # +/- 2 weeks around the centre = 5 weeks
MIN_N = {"trailing": 8, "seasonal": 4}
MIN_WIND_COVERAGE = 0.75


class _Week:
    """One complete week of price rows, loaded once."""

    def __init__(self, start: date, days: dict):
        self.start = start
        self.days = days                                   # date -> [(period, start_time, price)]
        prices = [p for rows in days.values() for _, _, p in rows]
        self.mean = sum(prices) / len(prices)
        self.daily_means = [sum(p for _, _, p in rows) / len(rows) for rows in days.values()]
        self.above_150 = sum(p > 150 for p in prices)
        self.above_200 = sum(p > 200 for p in prices)
        self._arb = None

    @property
    def median_arb_spread(self) -> float:
        if self._arb is None:
            spreads = []
            for d, rows in self.days.items():
                df = pd.DataFrame(rows, columns=["Period", "StartTime", "DAMPrice_EUR_MWh"])
                df["DeliveryDate"] = pd.Timestamp(d)
                spreads.append(daily_summary(df, d)["arb_spread"])
            self._arb = statistics.median(spreads)
        return self._arb


def _load_week(conn: sqlite3.Connection, start: date):
    """_Week, or (None, reason) if any of the 7 days is missing or short."""
    end = start + timedelta(days=6)
    days = {start + timedelta(days=i): [] for i in range(7)}
    for ds, period, st, price in conn.execute(
        "SELECT date, period, start_time, dam_price_eur_mwh FROM market_prices "
        "WHERE date BETWEEN ? AND ? ORDER BY date, period",
        (start.isoformat(), end.isoformat()),
    ):
        days[date.fromisoformat(ds)].append((period, st, price))
    bad = [f"{d.isoformat()} has {len(r)} of {expected_periods(d)}" for d, r in days.items()
           if len(r) != expected_periods(d)]
    if bad:
        return None, "incomplete week: " + "; ".join(bad)
    return _Week(start, days), None


def _percentile(value: float, base: list[float]) -> float:
    v = round(value, 6)
    below = sum(round(b, 6) < v for b in base)
    ties = sum(round(b, 6) == v for b in base)
    return 100.0 * (below + 0.5 * ties) / len(base)


def _verdict(pct: float, high: str, low: str) -> str:
    if pct > 95:
        return f"unusually {high}"
    if pct > 80:
        return high
    if pct < 5:
        return f"unusually {low}"
    if pct < 20:
        return low
    return "normal"


def _rank(value: float, base: list[float]) -> int:
    v = round(value, 6)
    return 1 + sum(round(b, 6) > v for b in base)


def weekly_summary(week_start: date, conn: sqlite3.Connection) -> dict:
    """The summary dict for the Monday-to-Sunday week starting week_start. See the module docstring."""
    if week_start.weekday() != 0:
        raise ValueError(f"{week_start} is not a Monday")
    cache: dict = {}

    def week(start: date):
        if start not in cache:
            cache[start] = _load_week(conn, start)
        return cache[start][0]

    this, why = _load_week(conn, week_start)
    if this is None:
        raise ValueError(f"{week_start}: {why}")
    cache[week_start] = (this, None)

    trailing = [w for w in (week(week_start - timedelta(days=7 * k)) for k in range(1, TRAILING_WEEKS + 1)) if w]
    seasonal_starts = [week_start - timedelta(days=SEASONAL_CENTRE_DAYS) + timedelta(days=7 * j)
                       for j in range(-SEASONAL_SPAN_WEEKS, SEASONAL_SPAN_WEEKS + 1)]
    seasonal = [w for w in (week(s) for s in seasonal_starts if s < week_start) if w]

    first = conn.execute("SELECT MIN(date) FROM market_prices").fetchone()[0]
    earlier_all = []
    s = week_start - timedelta(days=7)
    while first and s >= date.fromisoformat(first) - timedelta(days=6):
        w = week(s)
        if w:
            earlier_all.append(w)
        s -= timedelta(days=7)                              # most recent first

    def compare(kind: str, base: list[_Week], since_pool: list[_Week]) -> dict:
        n = len(base)
        out = {"n": n, "weeks": [w.start.isoformat() for w in base], "means": [round(w.mean, 2) for w in base],
               "suppressed": n < MIN_N[kind],
               "reason": None, "median_week_mean": round(statistics.median(w.mean for w in base), 2) if base else None,
               "rank": None, "rank_of": None, "percentile": None, "verdict_price": None,
               "dearest_since": None, "cheapest_since": None,
               "arb_rank": None, "arb_percentile": None, "verdict_volatility": None}
        if out["suppressed"]:
            out["reason"] = f"only {n} complete {kind} baseline week{'' if n == 1 else 's'}, need {MIN_N[kind]}"
            return out
        means = [w.mean for w in base]
        out["rank"], out["rank_of"] = _rank(this.mean, means), n + 1
        out["percentile"] = round(_percentile(this.mean, means), 1)
        out["verdict_price"] = _verdict(_percentile(this.mean, means), "dearer", "cheaper")
        out["dearest_since"] = next((w.start.isoformat() for w in since_pool if round(w.mean, 6) >= round(this.mean, 6)), None)
        out["cheapest_since"] = next((w.start.isoformat() for w in since_pool if round(w.mean, 6) <= round(this.mean, 6)), None)
        arbs = [w.median_arb_spread for w in base]
        out["arb_rank"] = _rank(this.median_arb_spread, arbs)
        out["arb_percentile"] = round(_percentile(this.median_arb_spread, arbs), 1)
        out["verdict_volatility"] = _verdict(_percentile(this.median_arb_spread, arbs), "more volatile", "calmer")
        return out

    # wind: this week and the trailing weeks, wind_mw only, nothing imputed
    def wind(w: _Week):
        rows = conn.execute(
            "SELECT wind_mw FROM system_conditions WHERE date BETWEEN ? AND ?",
            (w.start.isoformat(), (w.start + timedelta(days=6)).isoformat()),
        ).fetchall()
        vals = [r[0] for r in rows if r[0] is not None]
        total = sum(expected_periods(d) for d in w.days)
        return (sum(vals) / len(vals) if vals else None), len(vals) / total

    wind_mean, wind_cov = wind(this)
    centre = week_start - timedelta(days=SEASONAL_CENTRE_DAYS)
    last_year = week(centre) if centre < week_start else None
    base_wind = [m for m, c in (wind(w) for w in trailing) if m is not None and c >= MIN_WIND_COVERAGE]
    daily = list(this.days)
    hi = max(range(7), key=lambda i: this.daily_means[i])
    lo = min(range(7), key=lambda i: this.daily_means[i])
    t150 = [w.above_150 for w in trailing]
    t200 = [w.above_200 for w in trailing]

    result = {
        "week_start": week_start.isoformat(),
        "week_end": (week_start + timedelta(days=6)).isoformat(),
        "n_periods": sum(len(r) for r in this.days.values()),
        "week_mean": round(this.mean, 2),
        "week_mean_c_per_kwh": round(this.mean / 10, 2),
        "daily_dates": [d.isoformat() for d in daily],
        "daily_means": [round(m, 2) for m in this.daily_means],
        "highest_day": {"date": daily[hi].isoformat(), "mean": round(this.daily_means[hi], 2)},
        "lowest_day": {"date": daily[lo].isoformat(), "mean": round(this.daily_means[lo], 2)},
        "periods_above_150": this.above_150,
        "periods_above_200": this.above_200,
        "periods_above_150_trailing_median": statistics.median(t150) if t150 else None,
        "periods_above_200_trailing_median": statistics.median(t200) if t200 else None,
        "median_arb_spread": round(this.median_arb_spread, 2),
        "wind_mw_mean": round(wind_mean, 1) if wind_mean is not None else None,
        "wind_coverage": round(wind_cov, 3),
        "wind_mw_trailing_median": round(statistics.median(base_wind), 1) if len(base_wind) >= MIN_N["trailing"] else None,
        "wind_mw_trailing_n": len(base_wind),
        "trailing": compare("trailing", trailing, earlier_all),
        "previous_week_mean": round(week(week_start - timedelta(days=7)).mean, 2) if week(week_start - timedelta(days=7)) else None,
        "same_week_last_year": ({"week_start": last_year.start.isoformat(), "mean": round(last_year.mean, 2)}
                                if last_year else None),
        "seasonal_n": len(seasonal),
        "seasonal": None,
        "seasonal_reason": None,
    }
    if len(seasonal) >= MIN_N["seasonal"]:
        result["seasonal"] = compare("seasonal", seasonal, sorted(seasonal, key=lambda w: w.start, reverse=True))
    else:
        result["seasonal_reason"] = (f"only {len(seasonal)} complete seasonal week{'' if len(seasonal) == 1 else 's'} in the store "
                                     f"(weeks starting {SEASONAL_CENTRE_DAYS} days earlier +/- "
                                     f"{SEASONAL_SPAN_WEEKS * 7} days), need {MIN_N['seasonal']}")
    # verdict_price / verdict_volatility mirror the trailing baseline at the top level
    result["verdict_price"] = result["trailing"]["verdict_price"]
    result["verdict_volatility"] = result["trailing"]["verdict_volatility"]
    return result


def ordinal(n: int) -> str:
    """1st, 2nd, 3rd, 4th ... 11th, 12th, 13th, 21st."""
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def seasonal_baseline_starts(conn: sqlite3.Connection, week_start: date) -> tuple[list[date], str | None]:
    """Complete seasonal baseline weeks for week_start, without needing the target week
    itself to be in the store. Returns (starts, None) or ([], reason) below 4 weeks."""
    centre = week_start - timedelta(days=SEASONAL_CENTRE_DAYS)
    starts = [centre + timedelta(days=7 * j) for j in range(-SEASONAL_SPAN_WEEKS, SEASONAL_SPAN_WEEKS + 1)]
    ok = [s for s in starts if s < week_start and _load_week(conn, s)[0] is not None]
    if len(ok) < MIN_N["seasonal"]:
        return [], f"only {len(ok)} complete seasonal week{'' if len(ok) == 1 else 's'}, need {MIN_N['seasonal']}"
    return ok, None
