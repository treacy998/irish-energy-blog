---
title: "I-SEM Daily Briefing — 27 July 2026"
date: 2026-07-27
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €160.34/MWh, peaking at €214.54/MWh at 19:00."
images: ["charts/2026-07-27/card-2026-07-27.png"]
draft: false
---

{{< statbar mean="€160.34" peak="€214.54" min="€127.9" spread="€86.64" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €160.34/MWh    |
| Median Price         | €144.78/MWh    |
| Std Dev              | €29.75/MWh    |
| Peak Price           | €214.54/MWh (19:00) |
| Min Price            | €127.9/MWh (13:30)   |
| Price Range          | €86.64/MWh   |
| Periods above €150   | 23 of 48 (48%) |
| Periods above €200   | 8 of 48 (17%) |
| Peak Avg (07–22)     | €168.08/MWh    |
| Off-peak Avg (22–07) | €147.45/MWh    |
| Peak/Off-Peak Spread | €20.63/MWh   |
| Wind % of Demand     | 26.1%          |
| Wind Range           | 19.0%–36.1% |
| Mean Demand          | 3884 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-07-27/dam-2026-07-27.png)

**Std dev** €29.75/MWh  ·  **Median** €144.78/MWh  ·  **Periods above €150:** 23 of 48 (48%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-07-27/price-wind-2026-07-27.png)

**Mean wind:** 26.1%  ·  **Range:** 19.0%–36.1%

## Week in Context

![7-Day Price Comparison](/charts/2026-07-27/week-compare-2026-07-27.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-07-27/pdc-2026-07-27.png)

**Periods above €150:** 23 (48% of day)  ·  **Above €200:** 8 (17% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-07-27/spread-2026-07-27.png)

**Peak avg (07:00–22:00):** €168.08/MWh  ·  **Off-peak avg:** €147.45/MWh  ·  **Spread:** €20.63/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €128/MWh | 13:30 | 2 MWh | −€256 |
| **Discharge** | €207/MWh | 18:30 | 1.7 MWh (85% RTE) | +€353 |
| **Gross profit** | | | | **€97** |
| **Price spread** | €79/MWh | | | **ROI: 37.8%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-07-27/bess-2026-07-27.png)

## Commentary

Wind pulled back to 26.1% after the weekend's extremes, and the price shape snapped back to something more conventional: a positive peak/off-peak spread of €20.63, the first day this week where the traditional evening premium actually held. The morning ramp from 06:00 to 07:30 pushed price from €161.50 to €201.29 as wind eased into the mid-20s, and the evening peak at 19:00 (€214.54) came as wind dipped back toward 19%.

There was still a clear midday trough — wind held near 26–29% through the early afternoon and price sagged to €127.90, essentially flat for four consecutive periods — but nothing like Saturday or Sunday's collapse into single digits. This was a market operating in its normal range: wind moving in the high teens to high twenties produces a moderate trough and a real, if unspectacular, evening ceiling.

Storage cleared €97 gross on a 37.8% ROI, roughly the week's median outcome. A decent but unremarkable spread for a decent but unremarkable wind day — after two days of extremes, a reminder of what "normal" looks like in this market.


<details>
<summary>Half-hourly data — 2026-07-27</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 151.58 | 33.8% |
| 2 | 23:30 | 142.80 | 36.1% |
| 3 | 00:00 | 136.69 | 30.7% |
| 4 | 00:30 | 136.52 | 29.0% |
| 5 | 01:00 | 133.74 | 27.5% |
| 6 | 01:30 | 133.74 | 27.9% |
| 7 | 02:00 | 136.69 | 29.2% |
| 8 | 02:30 | 136.69 | 30.0% |
| 9 | 03:00 | 136.58 | 28.4% |
| 10 | 03:30 | 136.58 | 28.2% |
| 11 | 04:00 | 134.58 | 25.8% |
| 12 | 04:30 | 133.74 | 24.7% |
| 13 | 05:00 | 142.72 | 25.8% |
| 14 | 05:30 | 142.10 | 23.7% |
| 15 | 06:00 | 161.50 | 24.6% |
| 16 | 06:30 | 169.50 | 24.7% |
| 17 | 07:00 | 192.05 | 25.1% |
| 18 | 07:30 | 201.29 | 24.0% |
| 19 | 08:00 | 192.05 | 23.7% |
| 20 | 08:30 | 196.86 | 23.8% |
| 21 | 09:00 | 185.00 | 25.9% |
| 22 | 09:30 | 181.00 | 27.1% |
| 23 | 10:00 | 162.12 | 27.6% |
| 24 | 10:30 | 156.82 | 25.6% |
| 25 | 11:00 | 140.05 | 25.4% |
| 26 | 11:30 | 136.82 | 27.0% |
| 27 | 12:00 | 130.57 | 27.9% |
| 28 | 12:30 | 129.58 | 25.9% |
| 29 | 13:00 | 128.14 | 26.9% |
| 30 | 13:30 | 127.90 | 28.1% |
| 31 | 14:00 | 127.90 | 28.2% |
| 32 | 14:30 | 127.90 | 29.7% |
| 33 | 15:00 | 127.90 | 27.4% |
| 34 | 15:30 | 127.90 | 26.8% |
| 35 | 16:00 | 139.08 | 26.1% |
| 36 | 16:30 | 146.76 | 26.0% |
| 37 | 17:00 | 169.03 | 23.9% |
| 38 | 17:30 | 187.79 | 22.5% |
| 39 | 18:00 | 190.99 | 21.1% |
| 40 | 18:30 | 207.33 | 19.1% |
| 41 | 19:00 | 214.54 | 19.3% |
| 42 | 19:30 | 211.47 | 19.8% |
| 43 | 20:00 | 196.20 | 19.0% |
| 44 | 20:30 | 203.30 | 20.6% |
| 45 | 21:00 | 203.99 | 24.3% |
| 46 | 21:30 | 200.05 | 27.7% |
| 47 | 22:00 | 200.36 | 28.8% |
| 48 | 22:30 | 188.05 | 29.7% |

</details>

