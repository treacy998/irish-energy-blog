---
title: "I-SEM Daily Briefing — 17 May 2026"
date: 2026-05-17
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €136.77/MWh, peaking at €227.28/MWh at 22:00."
draft: false
---

{{< statbar mean="€136.77" peak="€227.28" min="€108.35" spread="€118.93" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €136.77/MWh    |
| Median Price         | €120.17/MWh    |
| Std Dev              | €35.92/MWh    |
| Peak Price           | €227.28/MWh (22:00) |
| Min Price            | €108.35/MWh (13:30)   |
| Price Range          | €118.93/MWh   |
| Periods above €150   | 11 of 48 (23%) |
| Periods above €200   | 6 of 48 (12%) |
| Peak Avg (07–22)     | €137.7/MWh    |
| Off-peak Avg (22–07) | €135.22/MWh    |
| Peak/Off-Peak Spread | €2.48/MWh   |
| Wind % of Demand     | 36.1%          |
| Wind Range           | 15.6%–50.0% |
| Mean Demand          | 3634 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-05-17/dam-2026-05-17.png)

**Std dev** €35.92/MWh  ·  **Median** €120.17/MWh  ·  **Periods above €150:** 11 of 48 (23%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-05-17/price-wind-2026-05-17.png)

**Mean wind:** 36.1%  ·  **Range:** 15.6%–50.0%

## Week in Context

![7-Day Price Comparison](/charts/2026-05-17/week-compare-2026-05-17.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-05-17/pdc-2026-05-17.png)

**Periods above €150:** 11 (23% of day)  ·  **Above €200:** 6 (12% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-05-17/spread-2026-05-17.png)

**Peak avg (07:00–22:00):** €137.7/MWh  ·  **Off-peak avg:** €135.22/MWh  ·  **Spread:** €2.48/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €111/MWh | 10:00 | 2 MWh | −€221 |
| **Discharge** | €225/MWh | 21:00 | 1.7 MWh (85% RTE) | +€382 |
| **Gross profit** | | | | **€161** |
| **Price spread** | €114/MWh | | | **ROI: 72.8%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-05-17/bess-2026-05-17.png)

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
<summary>Half-hourly data — 2026-05-17</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 138.02 | 16.4% |
| 2 | 23:30 | 136.89 | 15.6% |
| 3 | 00:00 | 133.00 | 39.0% |
| 4 | 00:30 | 131.00 | 39.2% |
| 5 | 01:00 | 129.00 | 38.3% |
| 6 | 01:30 | 126.23 | 38.7% |
| 7 | 02:00 | 126.06 | 37.4% |
| 8 | 02:30 | 124.22 | 36.5% |
| 9 | 03:00 | 121.77 | 36.0% |
| 10 | 03:30 | 121.77 | 37.1% |
| 11 | 04:00 | 118.57 | 40.1% |
| 12 | 04:30 | 118.27 | 41.5% |
| 13 | 05:00 | 114.80 | 40.9% |
| 14 | 05:30 | 114.67 | 41.7% |
| 15 | 06:00 | 110.89 | 40.8% |
| 16 | 06:30 | 114.80 | 41.3% |
| 17 | 07:00 | 115.00 | 38.4% |
| 18 | 07:30 | 115.26 | 36.4% |
| 19 | 08:00 | 115.26 | 33.6% |
| 20 | 08:30 | 115.26 | 34.4% |
| 21 | 09:00 | 112.00 | 33.5% |
| 22 | 09:30 | 110.76 | 35.2% |
| 23 | 10:00 | 111.68 | 37.0% |
| 24 | 10:30 | 110.00 | 36.1% |
| 25 | 11:00 | 110.42 | 39.7% |
| 26 | 11:30 | 110.00 | 40.8% |
| 27 | 12:00 | 112.94 | 36.7% |
| 28 | 12:30 | 111.00 | 44.4% |
| 29 | 13:00 | 110.88 | 46.6% |
| 30 | 13:30 | 108.35 | 46.7% |
| 31 | 14:00 | 112.85 | 50.0% |
| 32 | 14:30 | 112.06 | 46.4% |
| 33 | 15:00 | 115.26 | 42.7% |
| 34 | 15:30 | 117.52 | 37.3% |
| 35 | 16:00 | 126.81 | 40.1% |
| 36 | 16:30 | 132.46 | 39.2% |
| 37 | 17:00 | 143.90 | 37.7% |
| 38 | 17:30 | 150.56 | 35.6% |
| 39 | 18:00 | 161.26 | 35.2% |
| 40 | 18:30 | 170.23 | 33.4% |
| 41 | 19:00 | 184.03 | 30.1% |
| 42 | 19:30 | 185.58 | 30.1% |
| 43 | 20:00 | 201.00 | 30.6% |
| 44 | 20:30 | 203.90 | 29.7% |
| 45 | 21:00 | 220.37 | 26.3% |
| 46 | 21:30 | 224.29 | 25.7% |
| 47 | 22:00 | 227.28 | 23.8% |
| 48 | 22:30 | 226.73 | 20.3% |

</details>

