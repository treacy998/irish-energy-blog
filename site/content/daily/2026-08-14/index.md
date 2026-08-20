---
title: "I-SEM Daily Briefing — 14 August 2026"
date: 2026-08-14
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €182.7/MWh, peaking at €273.29/MWh at 19:00."
images: ["charts/2026-08-14/card-2026-08-14.png"]
draft: false
---

{{< statbar mean="€182.7" peak="€273.29" min="€138.7" spread="€134.59" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €182.7/MWh    |
| Median Price         | €172.45/MWh    |
| Std Dev              | €37.76/MWh    |
| Peak Price           | €273.29/MWh (19:00) |
| Min Price            | €138.7/MWh (14:00)   |
| Price Range          | €134.59/MWh   |
| Periods above €150   | 40 of 48 (83%) |
| Periods above €200   | 14 of 48 (29%) |
| Peak Avg (07–22)     | €188.69/MWh    |
| Off-peak Avg (22–07) | €172.72/MWh    |
| Peak/Off-Peak Spread | €15.97/MWh   |
| Wind % of Demand     | 11.1%          |
| Wind Range           | 8.0%–18.3% |
| Mean Demand          | 3961 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-14/dam-2026-08-14.png)

**Std dev** €37.76/MWh  ·  **Median** €172.45/MWh  ·  **Periods above €150:** 40 of 48 (83%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-14/price-wind-2026-08-14.png)

**Mean wind:** 11.1%  ·  **Range:** 8.0%–18.3%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-14/week-compare-2026-08-14.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-14/pdc-2026-08-14.png)

**Periods above €150:** 40 (83% of day)  ·  **Above €200:** 14 (29% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-14/spread-2026-08-14.png)

**Peak avg (07:00–22:00):** €188.69/MWh  ·  **Off-peak avg:** €172.72/MWh  ·  **Spread:** €15.97/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €139/MWh | 14:00 | 2 MWh | −€278 |
| **Discharge** | €266/MWh | 18:00 | 1.7 MWh (85% RTE) | +€452 |
| **Gross profit** | | | | **€174** |
| **Price spread** | €127/MWh | | | **ROI: 62.6%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-14/bess-2026-08-14.png)

<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->

## Commentary

Friday eased off Thursday's extreme without breaking the pattern. Wind nudged up only slightly to 11.1% (8.0–18.3%), still firmly in low-wind territory, and the price responded the same way in miniature: mean fell to €182.7, peak to €273.29 at 19:00, periods above €200 down to fourteen of forty-eight (29%, from Thursday's 40%). The share above €150 held exactly at 83% — the floor stayed elevated even as the ceiling came down.

Storage banked €174 gross at 62.6% ROI, charging into the 14:00 €139 trough and discharging the 18:00 €266 peak — a smaller spread than Thursday's record but still the week's second-best return. Two low-wind days back to back, two strong storage days. The pattern is becoming the headline.


<details>
<summary>Half-hourly data — 2026-08-14</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 212.77 | 8.5% |
| 2 | 23:30 | 186.58 | 8.2% |
| 3 | 00:00 | 176.00 | 9.9% |
| 4 | 00:30 | 171.95 | 10.7% |
| 5 | 01:00 | 162.00 | 11.8% |
| 6 | 01:30 | 158.58 | 11.9% |
| 7 | 02:00 | 160.28 | 11.9% |
| 8 | 02:30 | 156.74 | 13.6% |
| 9 | 03:00 | 155.32 | 14.7% |
| 10 | 03:30 | 154.40 | 15.5% |
| 11 | 04:00 | 159.69 | 16.2% |
| 12 | 04:30 | 159.69 | 15.8% |
| 13 | 05:00 | 171.05 | 17.5% |
| 14 | 05:30 | 172.96 | 18.3% |
| 15 | 06:00 | 177.10 | 17.8% |
| 16 | 06:30 | 184.23 | 16.2% |
| 17 | 07:00 | 194.99 | 13.7% |
| 18 | 07:30 | 201.00 | 10.8% |
| 19 | 08:00 | 212.39 | 8.7% |
| 20 | 08:30 | 218.03 | 8.7% |
| 21 | 09:00 | 201.00 | 8.1% |
| 22 | 09:30 | 184.92 | 8.1% |
| 23 | 10:00 | 164.11 | 8.5% |
| 24 | 10:30 | 152.50 | 8.0% |
| 25 | 11:00 | 153.35 | 8.0% |
| 26 | 11:30 | 148.00 | 8.8% |
| 27 | 12:00 | 150.68 | 8.8% |
| 28 | 12:30 | 145.77 | 8.0% |
| 29 | 13:00 | 143.99 | 8.8% |
| 30 | 13:30 | 140.29 | 9.1% |
| 31 | 14:00 | 138.70 | 9.8% |
| 32 | 14:30 | 138.70 | 11.5% |
| 33 | 15:00 | 138.70 | 12.8% |
| 34 | 15:30 | 140.00 | 12.4% |
| 35 | 16:00 | 151.31 | 13.1% |
| 36 | 16:30 | 155.00 | 13.4% |
| 37 | 17:00 | 193.67 | 12.8% |
| 38 | 17:30 | 201.80 | 12.0% |
| 39 | 18:00 | 258.33 | 11.0% |
| 40 | 18:30 | 263.85 | 9.1% |
| 41 | 19:00 | 273.29 | 8.3% |
| 42 | 19:30 | 268.38 | 8.4% |
| 43 | 20:00 | 251.03 | 8.8% |
| 44 | 20:30 | 246.35 | 8.7% |
| 45 | 21:00 | 217.06 | 9.3% |
| 46 | 21:30 | 213.39 | 9.1% |
| 47 | 22:00 | 199.15 | 8.8% |
| 48 | 22:30 | 190.49 | 8.6% |

</details>

