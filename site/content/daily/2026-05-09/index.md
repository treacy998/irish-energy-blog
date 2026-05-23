---
title: "I-SEM Daily Briefing — 9 May 2026"
date: 2026-05-09
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €113.41/MWh, peaking at €139.0/MWh at 19:30."
draft: false
---

{{< statbar mean="€113.41" peak="€139.0" min="€84.69" spread="€54.31" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €113.41/MWh    |
| Median Price         | €117.29/MWh    |
| Std Dev              | €16.77/MWh    |
| Peak Price           | €139.0/MWh (19:30) |
| Min Price            | €84.69/MWh (15:00)   |
| Price Range          | €54.31/MWh   |
| Periods above €150   | 0 of 48 (0%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €108.38/MWh    |
| Off-peak Avg (22–07) | €121.8/MWh    |
| Peak/Off-Peak Spread | €-13.42/MWh   |
| Wind % of Demand     | 56.7%          |
| Wind Range           | 39.1%–67.4% |
| Mean Demand          | 3503 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-05-09/dam-2026-05-09.png)

**Std dev** €16.77/MWh  ·  **Median** €117.29/MWh  ·  **Periods above €150:** 0 of 48 (0%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-05-09/price-wind-2026-05-09.png)

**Mean wind:** 56.7%  ·  **Range:** 39.1%–67.4%

## Week in Context

![7-Day Price Comparison](/charts/2026-05-09/week-compare-2026-05-09.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-05-09/pdc-2026-05-09.png)

**Periods above €150:** 0 (0% of day)  ·  **Above €200:** 0 (0% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-05-09/spread-2026-05-09.png)

**Peak avg (07:00–22:00):** €108.38/MWh  ·  **Off-peak avg:** €121.8/MWh  ·  **Spread:** €-13.42/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €85/MWh | 13:30 | 2 MWh | −€171 |
| **Discharge** | €138/MWh | 19:00 | 1.7 MWh (85% RTE) | +€234 |
| **Gross profit** | | | | **€63** |
| **Price spread** | €52/MWh | | | **ROI: 37.1%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-05-09/bess-2026-05-09.png)

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
<summary>Half-hourly data — 2026-05-09</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 133.07 | 67.4% |
| 2 | 23:30 | 128.95 | 67.2% |
| 3 | 00:00 | 125.23 | 39.1% |
| 4 | 00:30 | 123.36 | 42.0% |
| 5 | 01:00 | 122.23 | 43.7% |
| 6 | 01:30 | 117.88 | 44.9% |
| 7 | 02:00 | 121.64 | 46.1% |
| 8 | 02:30 | 119.15 | 48.0% |
| 9 | 03:00 | 123.00 | 48.3% |
| 10 | 03:30 | 121.69 | 51.4% |
| 11 | 04:00 | 121.30 | 55.5% |
| 12 | 04:30 | 120.54 | 59.7% |
| 13 | 05:00 | 118.62 | 58.1% |
| 14 | 05:30 | 116.71 | 61.0% |
| 15 | 06:00 | 113.62 | 60.8% |
| 16 | 06:30 | 112.71 | 61.3% |
| 17 | 07:00 | 106.32 | 63.6% |
| 18 | 07:30 | 107.00 | 63.7% |
| 19 | 08:00 | 111.11 | 59.5% |
| 20 | 08:30 | 110.00 | 58.1% |
| 21 | 09:00 | 114.00 | 57.3% |
| 22 | 09:30 | 110.00 | 57.9% |
| 23 | 10:00 | 102.74 | 55.1% |
| 24 | 10:30 | 99.00 | 55.9% |
| 25 | 11:00 | 93.92 | 56.8% |
| 26 | 11:30 | 93.75 | 55.0% |
| 27 | 12:00 | 89.00 | 56.0% |
| 28 | 12:30 | 88.00 | 56.0% |
| 29 | 13:00 | 87.61 | 57.8% |
| 30 | 13:30 | 85.00 | 57.1% |
| 31 | 14:00 | 86.31 | 55.2% |
| 32 | 14:30 | 85.06 | 55.8% |
| 33 | 15:00 | 84.69 | 55.5% |
| 34 | 15:30 | 87.70 | 55.1% |
| 35 | 16:00 | 93.75 | 56.1% |
| 36 | 16:30 | 99.00 | 54.2% |
| 37 | 17:00 | 114.64 | 56.5% |
| 38 | 17:30 | 120.05 | 58.5% |
| 39 | 18:00 | 130.72 | 59.2% |
| 40 | 18:30 | 132.53 | 59.7% |
| 41 | 19:00 | 138.72 | 60.2% |
| 42 | 19:30 | 139.00 | 61.8% |
| 43 | 20:00 | 137.47 | 58.5% |
| 44 | 20:30 | 135.03 | 59.1% |
| 45 | 21:00 | 134.35 | 59.2% |
| 46 | 21:30 | 135.00 | 61.3% |
| 47 | 22:00 | 128.00 | 65.0% |
| 48 | 22:30 | 124.71 | 66.9% |

</details>

