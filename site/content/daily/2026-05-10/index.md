---
title: "I-SEM Daily Briefing — 10 May 2026"
date: 2026-05-10
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €111.62/MWh, peaking at €172.18/MWh at 21:00."
draft: false
---

{{< statbar mean="€111.62" peak="€172.18" min="€81.09" spread="€91.09" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €111.62/MWh    |
| Median Price         | €108.58/MWh    |
| Std Dev              | €23.63/MWh    |
| Peak Price           | €172.18/MWh (21:00) |
| Min Price            | €81.09/MWh (14:30)   |
| Price Range          | €91.09/MWh   |
| Periods above €150   | 3 of 48 (6%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €107.94/MWh    |
| Off-peak Avg (22–07) | €117.75/MWh    |
| Peak/Off-Peak Spread | €-9.81/MWh   |
| Wind % of Demand     | 42.6%          |
| Wind Range           | 24.0%–73.9% |
| Mean Demand          | 3444 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-05-10/dam-2026-05-10.png)

**Std dev** €23.63/MWh  ·  **Median** €108.58/MWh  ·  **Periods above €150:** 3 of 48 (6%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-05-10/price-wind-2026-05-10.png)

**Mean wind:** 42.6%  ·  **Range:** 24.0%–73.9%

## Week in Context

![7-Day Price Comparison](/charts/2026-05-10/week-compare-2026-05-10.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-05-10/pdc-2026-05-10.png)

**Periods above €150:** 3 (6% of day)  ·  **Above €200:** 0 (0% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-05-10/spread-2026-05-10.png)

**Peak avg (07:00–22:00):** €107.94/MWh  ·  **Off-peak avg:** €117.75/MWh  ·  **Spread:** €-9.81/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €83/MWh | 13:30 | 2 MWh | −€165 |
| **Discharge** | €162/MWh | 20:30 | 1.7 MWh (85% RTE) | +€275 |
| **Gross profit** | | | | **€110** |
| **Price spread** | €79/MWh | | | **ROI: 66.9%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-05-10/bess-2026-05-10.png)

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
<summary>Half-hourly data — 2026-05-10</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 124.71 | 26.8% |
| 2 | 23:30 | 122.52 | 28.3% |
| 3 | 00:00 | 117.96 | 67.9% |
| 4 | 00:30 | 117.77 | 69.8% |
| 5 | 01:00 | 116.58 | 73.1% |
| 6 | 01:30 | 115.39 | 73.9% |
| 7 | 02:00 | 115.97 | 68.1% |
| 8 | 02:30 | 115.67 | 62.5% |
| 9 | 03:00 | 118.00 | 61.3% |
| 10 | 03:30 | 117.85 | 59.7% |
| 11 | 04:00 | 111.87 | 58.7% |
| 12 | 04:30 | 110.89 | 56.4% |
| 13 | 05:00 | 106.27 | 55.3% |
| 14 | 05:30 | 104.97 | 54.5% |
| 15 | 06:00 | 99.48 | 53.2% |
| 16 | 06:30 | 99.48 | 53.2% |
| 17 | 07:00 | 97.92 | 48.4% |
| 18 | 07:30 | 96.91 | 44.1% |
| 19 | 08:00 | 100.31 | 41.2% |
| 20 | 08:30 | 102.27 | 39.2% |
| 21 | 09:00 | 99.00 | 39.9% |
| 22 | 09:30 | 97.05 | 39.9% |
| 23 | 10:00 | 92.16 | 41.5% |
| 24 | 10:30 | 92.02 | 40.8% |
| 25 | 11:00 | 86.97 | 37.5% |
| 26 | 11:30 | 86.05 | 35.1% |
| 27 | 12:00 | 84.00 | 33.1% |
| 28 | 12:30 | 83.49 | 33.3% |
| 29 | 13:00 | 84.02 | 31.4% |
| 30 | 13:30 | 84.02 | 30.2% |
| 31 | 14:00 | 81.96 | 27.6% |
| 32 | 14:30 | 81.09 | 27.9% |
| 33 | 15:00 | 83.11 | 30.0% |
| 34 | 15:30 | 85.02 | 31.7% |
| 35 | 16:00 | 97.80 | 34.5% |
| 36 | 16:30 | 101.53 | 37.8% |
| 37 | 17:00 | 115.00 | 41.0% |
| 38 | 17:30 | 123.00 | 44.2% |
| 39 | 18:00 | 130.02 | 42.6% |
| 40 | 18:30 | 135.00 | 38.8% |
| 41 | 19:00 | 139.00 | 36.2% |
| 42 | 19:30 | 143.35 | 34.1% |
| 43 | 20:00 | 148.00 | 32.4% |
| 44 | 20:30 | 149.06 | 28.4% |
| 45 | 21:00 | 172.18 | 25.2% |
| 46 | 21:30 | 167.00 | 24.0% |
| 47 | 22:00 | 159.89 | 24.3% |
| 48 | 22:30 | 144.17 | 25.8% |

</details>

