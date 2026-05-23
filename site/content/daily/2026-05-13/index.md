---
title: "I-SEM Daily Briefing — 13 May 2026"
date: 2026-05-13
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €109.94/MWh, peaking at €145.0/MWh at 19:30."
draft: false
---

{{< statbar mean="€109.94" peak="€145.0" min="€90.5" spread="€54.5" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €109.94/MWh    |
| Median Price         | €103.81/MWh    |
| Std Dev              | €17.33/MWh    |
| Peak Price           | €145.0/MWh (19:30) |
| Min Price            | €90.5/MWh (14:30)   |
| Price Range          | €54.5/MWh   |
| Periods above €150   | 0 of 48 (0%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €113.26/MWh    |
| Off-peak Avg (22–07) | €104.4/MWh    |
| Peak/Off-Peak Spread | €8.86/MWh   |
| Wind % of Demand     | 60.1%          |
| Wind Range           | 50.4%–71.9% |
| Mean Demand          | 3792 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-05-13/dam-2026-05-13.png)

**Std dev** €17.33/MWh  ·  **Median** €103.81/MWh  ·  **Periods above €150:** 0 of 48 (0%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-05-13/price-wind-2026-05-13.png)

**Mean wind:** 60.1%  ·  **Range:** 50.4%–71.9%

## Week in Context

![7-Day Price Comparison](/charts/2026-05-13/week-compare-2026-05-13.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-05-13/pdc-2026-05-13.png)

**Periods above €150:** 0 (0% of day)  ·  **Above €200:** 0 (0% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-05-13/spread-2026-05-13.png)

**Peak avg (07:00–22:00):** €113.26/MWh  ·  **Off-peak avg:** €104.4/MWh  ·  **Spread:** €8.86/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €91/MWh | 13:00 | 2 MWh | −€182 |
| **Discharge** | €143/MWh | 19:00 | 1.7 MWh (85% RTE) | +€244 |
| **Gross profit** | | | | **€61** |
| **Price spread** | €52/MWh | | | **ROI: 33.7%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-05-13/bess-2026-05-13.png)

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
<summary>Half-hourly data — 2026-05-13</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 108.23 | 63.4% |
| 2 | 23:30 | 103.00 | 65.4% |
| 3 | 00:00 | 99.03 | 64.8% |
| 4 | 00:30 | 95.80 | 65.6% |
| 5 | 01:00 | 93.26 | 67.2% |
| 6 | 01:30 | 93.00 | 69.1% |
| 7 | 02:00 | 96.07 | 69.1% |
| 8 | 02:30 | 96.00 | 68.7% |
| 9 | 03:00 | 96.38 | 69.4% |
| 10 | 03:30 | 95.15 | 69.5% |
| 11 | 04:00 | 99.03 | 71.9% |
| 12 | 04:30 | 99.03 | 71.0% |
| 13 | 05:00 | 105.15 | 68.3% |
| 14 | 05:30 | 107.10 | 65.0% |
| 15 | 06:00 | 116.00 | 66.3% |
| 16 | 06:30 | 121.52 | 64.6% |
| 17 | 07:00 | 123.00 | 63.2% |
| 18 | 07:30 | 128.07 | 61.2% |
| 19 | 08:00 | 117.18 | 57.6% |
| 20 | 08:30 | 114.07 | 57.9% |
| 21 | 09:00 | 105.08 | 58.3% |
| 22 | 09:30 | 104.63 | 57.1% |
| 23 | 10:00 | 99.03 | 56.7% |
| 24 | 10:30 | 99.03 | 56.0% |
| 25 | 11:00 | 98.33 | 55.8% |
| 26 | 11:30 | 96.70 | 57.3% |
| 27 | 12:00 | 96.72 | 57.3% |
| 28 | 12:30 | 94.51 | 57.2% |
| 29 | 13:00 | 92.00 | 55.9% |
| 30 | 13:30 | 91.40 | 57.6% |
| 31 | 14:00 | 91.00 | 56.5% |
| 32 | 14:30 | 90.50 | 55.5% |
| 33 | 15:00 | 95.00 | 56.2% |
| 34 | 15:30 | 96.00 | 54.9% |
| 35 | 16:00 | 99.03 | 53.2% |
| 36 | 16:30 | 105.50 | 53.9% |
| 37 | 17:00 | 115.00 | 52.6% |
| 38 | 17:30 | 121.14 | 51.3% |
| 39 | 18:00 | 135.00 | 50.4% |
| 40 | 18:30 | 138.07 | 54.5% |
| 41 | 19:00 | 143.10 | 57.5% |
| 42 | 19:30 | 145.00 | 57.8% |
| 43 | 20:00 | 142.77 | 56.0% |
| 44 | 20:30 | 143.00 | 56.7% |
| 45 | 21:00 | 140.36 | 56.4% |
| 46 | 21:30 | 137.68 | 57.3% |
| 47 | 22:00 | 129.26 | 56.3% |
| 48 | 22:30 | 126.22 | 61.0% |

</details>

