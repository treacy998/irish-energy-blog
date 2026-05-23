---
title: "I-SEM Daily Briefing — 12 May 2026"
date: 2026-05-12
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €112.48/MWh, peaking at €161.7/MWh at 23:00."
draft: false
---

{{< statbar mean="€112.48" peak="€161.7" min="€79.4" spread="€82.3" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €112.48/MWh    |
| Median Price         | €112.28/MWh    |
| Std Dev              | €20.34/MWh    |
| Peak Price           | €161.7/MWh (23:00) |
| Min Price            | €79.4/MWh (15:00)   |
| Price Range          | €82.3/MWh   |
| Periods above €150   | 1 of 48 (2%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €107.69/MWh    |
| Off-peak Avg (22–07) | €120.47/MWh    |
| Peak/Off-Peak Spread | €-12.78/MWh   |
| Wind % of Demand     | 47.4%          |
| Wind Range           | 22.9%–65.6% |
| Mean Demand          | 3767 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-05-12/dam-2026-05-12.png)

**Std dev** €20.34/MWh  ·  **Median** €112.28/MWh  ·  **Periods above €150:** 1 of 48 (2%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-05-12/price-wind-2026-05-12.png)

**Mean wind:** 47.4%  ·  **Range:** 22.9%–65.6%

## Week in Context

![7-Day Price Comparison](/charts/2026-05-12/week-compare-2026-05-12.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-05-12/pdc-2026-05-12.png)

**Periods above €150:** 1 (2% of day)  ·  **Above €200:** 0 (0% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-05-12/spread-2026-05-12.png)

**Peak avg (07:00–22:00):** €107.69/MWh  ·  **Off-peak avg:** €120.47/MWh  ·  **Spread:** €-12.78/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €81/MWh | 14:30 | 2 MWh | −€161 |
| **Discharge** | €140/MWh | 23:00 | 1.7 MWh (85% RTE) | +€238 |
| **Gross profit** | | | | **€77** |
| **Price spread** | €60/MWh | | | **ROI: 47.8%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-05-12/bess-2026-05-12.png)

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
<summary>Half-hourly data — 2026-05-12</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 161.70 | 62.9% |
| 2 | 23:30 | 136.30 | 65.6% |
| 3 | 00:00 | 136.01 | 22.9% |
| 4 | 00:30 | 127.07 | 24.0% |
| 5 | 01:00 | 121.86 | 25.5% |
| 6 | 01:30 | 121.06 | 27.5% |
| 7 | 02:00 | 116.31 | 33.5% |
| 8 | 02:30 | 112.27 | 36.9% |
| 9 | 03:00 | 107.40 | 39.3% |
| 10 | 03:30 | 106.05 | 42.6% |
| 11 | 04:00 | 106.05 | 43.7% |
| 12 | 04:30 | 105.77 | 44.6% |
| 13 | 05:00 | 112.30 | 44.6% |
| 14 | 05:30 | 114.35 | 42.9% |
| 15 | 06:00 | 125.67 | 44.5% |
| 16 | 06:30 | 131.68 | 40.9% |
| 17 | 07:00 | 134.28 | 39.1% |
| 18 | 07:30 | 137.62 | 34.8% |
| 19 | 08:00 | 134.35 | 38.0% |
| 20 | 08:30 | 125.65 | 41.7% |
| 21 | 09:00 | 111.93 | 40.8% |
| 22 | 09:30 | 106.06 | 43.7% |
| 23 | 10:00 | 97.38 | 46.4% |
| 24 | 10:30 | 95.00 | 43.6% |
| 25 | 11:00 | 92.82 | 42.9% |
| 26 | 11:30 | 90.88 | 45.4% |
| 27 | 12:00 | 87.21 | 47.8% |
| 28 | 12:30 | 85.59 | 50.6% |
| 29 | 13:00 | 83.28 | 53.9% |
| 30 | 13:30 | 82.16 | 55.9% |
| 31 | 14:00 | 84.38 | 55.0% |
| 32 | 14:30 | 82.00 | 55.1% |
| 33 | 15:00 | 79.40 | 54.6% |
| 34 | 15:30 | 80.00 | 54.4% |
| 35 | 16:00 | 81.32 | 55.2% |
| 36 | 16:30 | 90.33 | 55.9% |
| 37 | 17:00 | 105.78 | 56.0% |
| 38 | 17:30 | 112.05 | 57.1% |
| 39 | 18:00 | 123.90 | 56.9% |
| 40 | 18:30 | 125.00 | 56.9% |
| 41 | 19:00 | 135.00 | 56.9% |
| 42 | 19:30 | 137.00 | 56.6% |
| 43 | 20:00 | 136.05 | 55.6% |
| 44 | 20:30 | 136.05 | 55.1% |
| 45 | 21:00 | 130.06 | 54.5% |
| 46 | 21:30 | 128.10 | 54.3% |
| 47 | 22:00 | 118.61 | 59.1% |
| 48 | 22:30 | 108.00 | 59.7% |

</details>

