"""
bess.py — Simple BESS dispatch simulation

Models a 1MW / 2MWh battery making one optimal cycle per SEM day
using DAM prices (perfect foresight).

Assumptions:
  - 1 cycle per day (charge once, discharge once)
  - 2 MWh usable capacity
  - Charge window: 4 consecutive half-hours at lowest prices
  - Discharge window: 4 consecutive half-hours at highest prices
  - No constraint that discharge must follow charge (DAM arbitrage model)
  - Round-trip efficiency: 85%
  - Result is gross — before network charges, capacity costs, degradation

Returns dict with keys:
  charge_mean      float  avg charge price €/MWh
  charge_start     str    HH:MM
  discharge_mean   float  avg discharge price €/MWh
  discharge_start  str    HH:MM
  gross_revenue    float  € (2 MWh × discharge price × 0.85)
  charge_cost      float  € (2 MWh × charge price)
  gross_profit     float  gross_revenue - charge_cost
  spread           float  discharge_mean - charge_mean
  charge_periods   list   period indices (0-based) for charting
  discharge_periods list  period indices (0-based) for charting
"""

import pandas as pd


def simulate_bess(df: pd.DataFrame) -> dict | None:
    prices = df["DAMPrice_EUR_MWh"].reset_index(drop=True)
    if len(prices) < 4 or prices.isna().all():
        return None

    rolling_sum = prices.rolling(4).sum()

    # Find the 4-consecutive-period window with lowest / highest sum
    charge_end_idx = int(rolling_sum.idxmin())
    discharge_end_idx = int(rolling_sum.idxmax())

    charge_idx = list(range(charge_end_idx - 3, charge_end_idx + 1))
    discharge_idx = list(range(discharge_end_idx - 3, discharge_end_idx + 1))

    charge_mean = prices.iloc[charge_idx].mean()
    discharge_mean = prices.iloc[discharge_idx].mean()

    charge_start = ""
    discharge_start = ""
    if "StartTime" in df.columns:
        times = df["StartTime"].reset_index(drop=True)
        charge_start = str(times.iloc[charge_idx[0]])[:5]
        discharge_start = str(times.iloc[discharge_idx[0]])[:5]

    gross_revenue = round(2 * discharge_mean * 0.85, 2)
    charge_cost = round(2 * charge_mean, 2)
    gross_profit = round(gross_revenue - charge_cost, 2)
    spread = round(float(discharge_mean - charge_mean), 2)

    return {
        "charge_mean": round(float(charge_mean), 2),
        "charge_start": charge_start,
        "discharge_mean": round(float(discharge_mean), 2),
        "discharge_start": discharge_start,
        "gross_revenue": gross_revenue,
        "charge_cost": charge_cost,
        "gross_profit": gross_profit,
        "spread": spread,
        "charge_periods": charge_idx,
        "discharge_periods": discharge_idx,
    }
