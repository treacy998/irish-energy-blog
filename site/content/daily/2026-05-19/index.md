---
title: "I-SEM Daily Briefing — 19 May 2026"
date: 2026-05-19
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €120.05/MWh, peaking at €161.09/MWh at 21:00."
draft: false
---

{{< statbar mean="€120.05" peak="€161.09" min="€90.63" spread="€70.46" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €120.05/MWh    |
| Median Price         | €118.04/MWh    |
| Std Dev              | €22.14/MWh    |
| Peak Price           | €161.09/MWh (21:00) |
| Min Price            | €90.63/MWh (14:00)   |
| Price Range          | €70.46/MWh   |
| Periods above €150   | 8 of 48 (17%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €123.92/MWh    |
| Off-peak Avg (22–07) | €113.61/MWh    |
| Peak/Off-Peak Spread | €10.31/MWh   |
| Wind % of Demand     | 45.4%          |
| Wind Range           | 36.6%–52.1% |
| Mean Demand          | 4028 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-05-19/dam-2026-05-19.png)

**Std dev** €22.14/MWh  ·  **Median** €118.04/MWh  ·  **Periods above €150:** 8 of 48 (17%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-05-19/price-wind-2026-05-19.png)

**Mean wind:** 45.4%  ·  **Range:** 36.6%–52.1%

## Week in Context

![7-Day Price Comparison](/charts/2026-05-19/week-compare-2026-05-19.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-05-19/pdc-2026-05-19.png)

**Periods above €150:** 8 (17% of day)  ·  **Above €200:** 0 (0% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-05-19/spread-2026-05-19.png)

**Peak avg (07:00–22:00):** €123.92/MWh  ·  **Off-peak avg:** €113.61/MWh  ·  **Spread:** €10.31/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €91/MWh | 13:00 | 2 MWh | −€181 |
| **Discharge** | €157/MWh | 19:30 | 1.7 MWh (85% RTE) | +€267 |
| **Gross profit** | | | | **€86** |
| **Price spread** | €67/MWh | | | **ROI: 47.4%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-05-19/bess-2026-05-19.png)

<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->

## Commentary

<!--
Write 2-3 paragraphs here:
- What drove the price shape today?
- How does wind/demand explain the peak and trough?
- Anything unusual compared to the week?
- Market context: outages, interconnector, weather forecast?
-->


<details>
<summary>Half-hourly data — 2026-05-19</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 131.50 | 47.7% |
| 2 | 23:30 | 126.00 | 51.3% |
| 3 | 00:00 | 125.00 | 45.5% |
| 4 | 00:30 | 122.74 | 46.9% |
| 5 | 01:00 | 118.60 | 47.1% |
| 6 | 01:30 | 117.48 | 50.3% |
| 7 | 02:00 | 113.00 | 46.9% |
| 8 | 02:30 | 110.58 | 45.7% |
| 9 | 03:00 | 102.03 | 44.9% |
| 10 | 03:30 | 100.01 | 45.9% |
| 11 | 04:00 | 94.92 | 45.5% |
| 12 | 04:30 | 95.02 | 45.6% |
| 13 | 05:00 | 91.82 | 52.1% |
| 14 | 05:30 | 95.00 | 51.7% |
| 15 | 06:00 | 110.00 | 50.0% |
| 16 | 06:30 | 120.00 | 46.2% |
| 17 | 07:00 | 134.37 | 45.8% |
| 18 | 07:30 | 140.73 | 39.9% |
| 19 | 08:00 | 141.52 | 37.6% |
| 20 | 08:30 | 135.58 | 36.6% |
| 21 | 09:00 | 127.63 | 36.6% |
| 22 | 09:30 | 121.00 | 38.2% |
| 23 | 10:00 | 112.79 | 38.9% |
| 24 | 10:30 | 110.00 | 39.8% |
| 25 | 11:00 | 101.99 | 43.6% |
| 26 | 11:30 | 97.48 | 47.0% |
| 27 | 12:00 | 98.83 | 46.6% |
| 28 | 12:30 | 95.67 | 48.6% |
| 29 | 13:00 | 91.00 | 49.5% |
| 30 | 13:30 | 90.65 | 49.6% |
| 31 | 14:00 | 90.63 | 51.3% |
| 32 | 14:30 | 90.63 | 51.8% |
| 33 | 15:00 | 96.00 | 51.0% |
| 34 | 15:30 | 97.23 | 51.9% |
| 35 | 16:00 | 113.40 | 47.9% |
| 36 | 16:30 | 117.00 | 44.2% |
| 37 | 17:00 | 132.01 | 43.2% |
| 38 | 17:30 | 137.99 | 43.6% |
| 39 | 18:00 | 150.01 | 42.0% |
| 40 | 18:30 | 150.01 | 41.7% |
| 41 | 19:00 | 160.01 | 39.0% |
| 42 | 19:30 | 160.01 | 38.1% |
| 43 | 20:00 | 153.19 | 39.4% |
| 44 | 20:30 | 154.90 | 42.9% |
| 45 | 21:00 | 161.09 | 46.7% |
| 46 | 21:30 | 154.26 | 47.1% |
| 47 | 22:00 | 140.74 | 47.2% |
| 48 | 22:30 | 130.56 | 49.3% |

</details>

