---
title: "I-SEM Daily Briefing — 11 May 2026"
date: 2026-05-11
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €137.93/MWh, peaking at €195.39/MWh at 21:00."
draft: false
---

{{< statbar mean="€137.93" peak="€195.39" min="€112.0" spread="€83.39" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €137.93/MWh    |
| Median Price         | €125.84/MWh    |
| Std Dev              | €27.7/MWh    |
| Peak Price           | €195.39/MWh (21:00) |
| Min Price            | €112.0/MWh (03:30)   |
| Price Range          | €83.39/MWh   |
| Periods above €150   | 12 of 48 (25%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €146.79/MWh    |
| Off-peak Avg (22–07) | €123.17/MWh    |
| Peak/Off-Peak Spread | €23.62/MWh   |
| Wind % of Demand     | 23.2%          |
| Wind Range           | 17.4%–32.1% |
| Mean Demand          | 3810 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-05-11/dam-2026-05-11.png)

**Std dev** €27.7/MWh  ·  **Median** €125.84/MWh  ·  **Periods above €150:** 12 of 48 (25%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-05-11/price-wind-2026-05-11.png)

**Mean wind:** 23.2%  ·  **Range:** 17.4%–32.1%

## Week in Context

![7-Day Price Comparison](/charts/2026-05-11/week-compare-2026-05-11.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-05-11/pdc-2026-05-11.png)

**Periods above €150:** 12 (25% of day)  ·  **Above €200:** 0 (0% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-05-11/spread-2026-05-11.png)

**Peak avg (07:00–22:00):** €146.79/MWh  ·  **Off-peak avg:** €123.17/MWh  ·  **Spread:** €23.62/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €112/MWh | 03:00 | 2 MWh | −€224 |
| **Discharge** | €195/MWh | 20:00 | 1.7 MWh (85% RTE) | +€331 |
| **Gross profit** | | | | **€107** |
| **Price spread** | €83/MWh | | | **ROI: 47.6%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-05-11/bess-2026-05-11.png)

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
<summary>Half-hourly data — 2026-05-11</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 125.00 | 21.9% |
| 2 | 23:30 | 120.01 | 22.7% |
| 3 | 00:00 | 118.29 | 30.1% |
| 4 | 00:30 | 115.37 | 28.4% |
| 5 | 01:00 | 115.51 | 27.7% |
| 6 | 01:30 | 114.01 | 27.6% |
| 7 | 02:00 | 116.00 | 29.1% |
| 8 | 02:30 | 113.24 | 26.5% |
| 9 | 03:00 | 112.87 | 27.5% |
| 10 | 03:30 | 112.00 | 29.3% |
| 11 | 04:00 | 112.01 | 32.1% |
| 12 | 04:30 | 112.01 | 29.8% |
| 13 | 05:00 | 117.33 | 29.4% |
| 14 | 05:30 | 118.01 | 29.3% |
| 15 | 06:00 | 129.32 | 27.2% |
| 16 | 06:30 | 136.01 | 25.6% |
| 17 | 07:00 | 146.01 | 23.4% |
| 18 | 07:30 | 155.00 | 22.1% |
| 19 | 08:00 | 154.52 | 23.0% |
| 20 | 08:30 | 148.00 | 22.0% |
| 21 | 09:00 | 141.00 | 21.5% |
| 22 | 09:30 | 139.00 | 21.5% |
| 23 | 10:00 | 129.55 | 21.3% |
| 24 | 10:30 | 128.00 | 21.3% |
| 25 | 11:00 | 126.67 | 19.4% |
| 26 | 11:30 | 125.00 | 18.9% |
| 27 | 12:00 | 124.00 | 17.4% |
| 28 | 12:30 | 121.67 | 19.2% |
| 29 | 13:00 | 117.37 | 17.8% |
| 30 | 13:30 | 116.00 | 18.8% |
| 31 | 14:00 | 117.00 | 19.5% |
| 32 | 14:30 | 116.00 | 21.2% |
| 33 | 15:00 | 115.00 | 22.5% |
| 34 | 15:30 | 117.00 | 23.3% |
| 35 | 16:00 | 121.40 | 23.6% |
| 36 | 16:30 | 127.10 | 23.8% |
| 37 | 17:00 | 141.70 | 24.4% |
| 38 | 17:30 | 159.00 | 24.0% |
| 39 | 18:00 | 180.27 | 23.1% |
| 40 | 18:30 | 180.28 | 22.1% |
| 41 | 19:00 | 187.40 | 20.5% |
| 42 | 19:30 | 190.64 | 19.3% |
| 43 | 20:00 | 194.24 | 18.4% |
| 44 | 20:30 | 194.24 | 18.5% |
| 45 | 21:00 | 195.39 | 18.2% |
| 46 | 21:30 | 195.38 | 18.5% |
| 47 | 22:00 | 180.00 | 21.1% |
| 48 | 22:30 | 150.00 | 21.0% |

</details>

