---
title: "I-SEM Daily Briefing — 18 May 2026"
date: 2026-05-18
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €162.73/MWh, peaking at €255.0/MWh at 07:30."
draft: false
---

{{< statbar mean="€162.73" peak="€255.0" min="€121.51" spread="€133.49" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €162.73/MWh    |
| Median Price         | €150.39/MWh    |
| Std Dev              | €35.29/MWh    |
| Peak Price           | €255.0/MWh (07:30) |
| Min Price            | €121.51/MWh (15:30)   |
| Price Range          | €133.49/MWh   |
| Periods above €150   | 25 of 48 (52%) |
| Periods above €200   | 8 of 48 (17%) |
| Peak Avg (07–22)     | €169.8/MWh    |
| Off-peak Avg (22–07) | €150.95/MWh    |
| Peak/Off-Peak Spread | €18.85/MWh   |
| Wind % of Demand     | 25.0%          |
| Wind Range           | 1.0%–55.7% |
| Mean Demand          | 4036 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-05-18/dam-2026-05-18.png)

**Std dev** €35.29/MWh  ·  **Median** €150.39/MWh  ·  **Periods above €150:** 25 of 48 (52%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-05-18/price-wind-2026-05-18.png)

**Mean wind:** 25.0%  ·  **Range:** 1.0%–55.7%

## Week in Context

![7-Day Price Comparison](/charts/2026-05-18/week-compare-2026-05-18.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-05-18/pdc-2026-05-18.png)

**Periods above €150:** 25 (52% of day)  ·  **Above €200:** 8 (17% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-05-18/spread-2026-05-18.png)

**Peak avg (07:00–22:00):** €169.8/MWh  ·  **Off-peak avg:** €150.95/MWh  ·  **Spread:** €18.85/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €124/MWh | 14:00 | 2 MWh | −€248 |
| **Discharge** | €245/MWh | 07:00 | 1.7 MWh (85% RTE) | +€416 |
| **Gross profit** | | | | **€168** |
| **Price spread** | €121/MWh | | | **ROI: 67.7%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-05-18/bess-2026-05-18.png)

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
<summary>Half-hourly data — 2026-05-18</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 150.29 | 48.0% |
| 2 | 23:30 | 144.00 | 47.8% |
| 3 | 00:00 | 150.50 | 15.4% |
| 4 | 00:30 | 149.85 | 12.8% |
| 5 | 01:00 | 148.52 | 10.7% |
| 6 | 01:30 | 143.92 | 9.4% |
| 7 | 02:00 | 149.85 | 8.0% |
| 8 | 02:30 | 149.85 | 7.5% |
| 9 | 03:00 | 144.74 | 7.0% |
| 10 | 03:30 | 148.00 | 5.6% |
| 11 | 04:00 | 147.88 | 4.0% |
| 12 | 04:30 | 151.64 | 3.5% |
| 13 | 05:00 | 152.06 | 3.0% |
| 14 | 05:30 | 155.62 | 2.4% |
| 15 | 06:00 | 168.96 | 2.2% |
| 16 | 06:30 | 200.09 | 1.6% |
| 17 | 07:00 | 240.39 | 1.2% |
| 18 | 07:30 | 255.00 | 1.1% |
| 19 | 08:00 | 239.70 | 1.0% |
| 20 | 08:30 | 243.24 | 1.3% |
| 21 | 09:00 | 231.19 | 2.0% |
| 22 | 09:30 | 231.70 | 3.0% |
| 23 | 10:00 | 222.10 | 4.7% |
| 24 | 10:30 | 188.51 | 7.0% |
| 25 | 11:00 | 184.69 | 9.0% |
| 26 | 11:30 | 172.00 | 12.8% |
| 27 | 12:00 | 161.00 | 17.6% |
| 28 | 12:30 | 152.50 | 21.8% |
| 29 | 13:00 | 140.40 | 27.7% |
| 30 | 13:30 | 134.11 | 32.5% |
| 31 | 14:00 | 126.05 | 35.4% |
| 32 | 14:30 | 125.77 | 39.4% |
| 33 | 15:00 | 122.57 | 43.0% |
| 34 | 15:30 | 121.51 | 48.8% |
| 35 | 16:00 | 128.17 | 51.3% |
| 36 | 16:30 | 129.85 | 52.7% |
| 37 | 17:00 | 141.36 | 54.9% |
| 38 | 17:30 | 144.39 | 55.2% |
| 39 | 18:00 | 162.77 | 55.7% |
| 40 | 18:30 | 161.00 | 54.2% |
| 41 | 19:00 | 163.55 | 51.8% |
| 42 | 19:30 | 162.18 | 50.5% |
| 43 | 20:00 | 159.14 | 48.7% |
| 44 | 20:30 | 156.05 | 46.3% |
| 45 | 21:00 | 149.04 | 44.4% |
| 46 | 21:30 | 144.00 | 43.4% |
| 47 | 22:00 | 133.34 | 45.3% |
| 48 | 22:30 | 128.00 | 46.9% |

</details>

