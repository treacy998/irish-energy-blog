---
title: "I-SEM Daily Briefing — 11 August 2026"
date: 2026-08-11
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €150.73/MWh, peaking at €190.64/MWh at 19:30."
images: ["charts/2026-08-11/card-2026-08-11.png"]
draft: false
---

{{< statbar mean="€150.73" peak="€190.64" min="€119.52" spread="€71.12" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €150.73/MWh    |
| Median Price         | €151.95/MWh    |
| Std Dev              | €20.91/MWh    |
| Peak Price           | €190.64/MWh (19:30) |
| Min Price            | €119.52/MWh (15:00)   |
| Price Range          | €71.12/MWh   |
| Periods above €150   | 25 of 48 (52%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €150.73/MWh    |
| Off-peak Avg (22–07) | €150.73/MWh    |
| Peak/Off-Peak Spread | €0.0/MWh   |
| Wind % of Demand     | 20.6%          |
| Wind Range           | 13.5%–32.1% |
| Mean Demand          | 3781 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-11/dam-2026-08-11.png)

**Std dev** €20.91/MWh  ·  **Median** €151.95/MWh  ·  **Periods above €150:** 25 of 48 (52%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-11/price-wind-2026-08-11.png)

**Mean wind:** 20.6%  ·  **Range:** 13.5%–32.1%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-11/week-compare-2026-08-11.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-11/pdc-2026-08-11.png)

**Periods above €150:** 25 (52% of day)  ·  **Above €200:** 0 (0% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-11/spread-2026-08-11.png)

**Peak avg (07:00–22:00):** €150.73/MWh  ·  **Off-peak avg:** €150.73/MWh  ·  **Spread:** €0.0/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €120/MWh | 14:00 | 2 MWh | −€240 |
| **Discharge** | €189/MWh | 19:00 | 1.7 MWh (85% RTE) | +€322 |
| **Gross profit** | | | | **€81** |
| **Price spread** | €69/MWh | | | **ROI: 33.9%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-11/bess-2026-08-11.png)

<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->

## Commentary

Tuesday eased off Monday's scarcity pricing — no period cleared €200, and std dev fell to €20.91, the week's second-flattest day behind only the 4th. Wind sat in a familiar moderate band (20.6%, 13.5–32.1%), and the shape followed the same gentle single-cycle pattern as most of the week: a mild overnight rise to €160-ish by 06:00–08:00, a soft afternoon trough of €119.52 at 15:00, then a clean build into a €190.64 evening peak at 19:30.

The stand-out number is the peak/off-peak spread: exactly €0.00. Peak avg and off-peak avg both came out to €150.73/MWh to two decimal places — a coincidence worth noting, not a pattern, but a tidy reminder that the split can land flat even on a day with a clear €71 trough-to-peak range, when the volatility sits mostly within the 07:00–22:00 window rather than across its boundary.

Storage closed the run with a modest €81 gross off a €120 charge and €189 discharge, 33.9% ROI — unremarkable, in keeping with the day. Over the week: one wind-driven collapse (the 5th), one weekend demand trough (the 8th), and six ordinary gas-set days either side. The lesson holds — storage gets paid for volatility, and this week there wasn't much of it outside two days.


<details>
<summary>Half-hourly data — 2026-08-11</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 166.12 | 28.8% |
| 2 | 23:30 | 159.99 | 32.1% |
| 3 | 00:00 | 156.30 | 22.2% |
| 4 | 00:30 | 152.10 | 22.2% |
| 5 | 01:00 | 144.81 | 22.6% |
| 6 | 01:30 | 142.69 | 23.2% |
| 7 | 02:00 | 140.83 | 22.5% |
| 8 | 02:30 | 138.03 | 21.3% |
| 9 | 03:00 | 137.66 | 21.3% |
| 10 | 03:30 | 136.63 | 22.4% |
| 11 | 04:00 | 143.71 | 20.9% |
| 12 | 04:30 | 143.49 | 22.0% |
| 13 | 05:00 | 152.98 | 23.5% |
| 14 | 05:30 | 154.69 | 23.4% |
| 15 | 06:00 | 157.85 | 23.4% |
| 16 | 06:30 | 160.80 | 22.9% |
| 17 | 07:00 | 162.00 | 21.7% |
| 18 | 07:30 | 164.48 | 20.7% |
| 19 | 08:00 | 161.74 | 19.9% |
| 20 | 08:30 | 160.10 | 18.9% |
| 21 | 09:00 | 159.80 | 18.2% |
| 22 | 09:30 | 153.58 | 18.6% |
| 23 | 10:00 | 146.20 | 21.1% |
| 24 | 10:30 | 142.10 | 23.6% |
| 25 | 11:00 | 132.04 | 22.7% |
| 26 | 11:30 | 129.18 | 23.3% |
| 27 | 12:00 | 126.10 | 22.6% |
| 28 | 12:30 | 125.00 | 19.5% |
| 29 | 13:00 | 122.36 | 18.4% |
| 30 | 13:30 | 121.00 | 17.3% |
| 31 | 14:00 | 120.89 | 17.4% |
| 32 | 14:30 | 119.79 | 17.9% |
| 33 | 15:00 | 119.52 | 17.5% |
| 34 | 15:30 | 120.11 | 18.5% |
| 35 | 16:00 | 129.02 | 20.3% |
| 36 | 16:30 | 129.87 | 21.0% |
| 37 | 17:00 | 143.60 | 20.1% |
| 38 | 17:30 | 151.81 | 17.8% |
| 39 | 18:00 | 175.90 | 16.6% |
| 40 | 18:30 | 180.88 | 15.5% |
| 41 | 19:00 | 190.00 | 13.5% |
| 42 | 19:30 | 190.64 | 14.1% |
| 43 | 20:00 | 188.00 | 15.2% |
| 44 | 20:30 | 188.00 | 16.9% |
| 45 | 21:00 | 185.84 | 18.3% |
| 46 | 21:30 | 182.40 | 21.3% |
| 47 | 22:00 | 166.39 | 22.1% |
| 48 | 22:30 | 158.10 | 24.6% |

</details>

