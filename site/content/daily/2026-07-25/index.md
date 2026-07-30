---
title: "I-SEM Daily Briefing — 25 July 2026"
date: 2026-07-25
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €126.89/MWh, peaking at €201.24/MWh at 23:00."
images: ["charts/2026-07-25/card-2026-07-25.png"]
draft: false
---

{{< statbar mean="€126.89" peak="€201.24" min="€20.86" spread="€180.38" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €126.89/MWh    |
| Median Price         | €127.7/MWh    |
| Std Dev              | €48.21/MWh    |
| Peak Price           | €201.24/MWh (23:00) |
| Min Price            | €20.86/MWh (09:00)   |
| Price Range          | €180.38/MWh   |
| Periods above €150   | 18 of 48 (38%) |
| Periods above €200   | 1 of 48 (2%) |
| Peak Avg (07–22)     | €111.82/MWh    |
| Off-peak Avg (22–07) | €152.01/MWh    |
| Peak/Off-Peak Spread | €-40.19/MWh   |
| Wind % of Demand     | 37.5%          |
| Wind Range           | 25.8%–60.6% |
| Mean Demand          | 3576 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-07-25/dam-2026-07-25.png)

**Std dev** €48.21/MWh  ·  **Median** €127.7/MWh  ·  **Periods above €150:** 18 of 48 (38%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-07-25/price-wind-2026-07-25.png)

**Mean wind:** 37.5%  ·  **Range:** 25.8%–60.6%

## Week in Context

![7-Day Price Comparison](/charts/2026-07-25/week-compare-2026-07-25.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-07-25/pdc-2026-07-25.png)

**Periods above €150:** 18 (38% of day)  ·  **Above €200:** 1 (2% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-07-25/spread-2026-07-25.png)

**Peak avg (07:00–22:00):** €111.82/MWh  ·  **Off-peak avg:** €152.01/MWh  ·  **Spread:** €-40.19/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €33/MWh | 08:00 | 2 MWh | −€65 |
| **Discharge** | €190/MWh | 21:00 | 1.7 MWh (85% RTE) | +€323 |
| **Gross profit** | | | | **€258** |
| **Price spread** | €158/MWh | | | **ROI: 395.0%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-07-25/bess-2026-07-25.png)

<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->

## Commentary

Wind stepped up again — 37.5% average, peaking at 60.6% overnight — and the price curve caved in the middle of the day. From 07:00 through 09:30, wind held in the 26–44% band and price fell through the floor, bottoming at €20.86 at 09:00. Three consecutive hours under €40/MWh in the middle of a weekday morning is not something low-wind days ever produce.

Peak/off-peak spread flipped further negative than Friday, to -€40.19, confirming the pattern: the more wind in the system, the more the cheap hours migrate into daylight and the more the "peak" label on 07:00–22:00 stops meaning anything. The evening still carried a premium — wind eased back into the 30s by 20:00 and price climbed back to €201.24 at 23:00 — but the story of the day was that midday trough.

Storage loved it. €258 gross profit and a 395% ROI, the best day so far this week, on a €158/MWh spread between an €33/MWh charge and a €190/MWh discharge. This is what the theory predicts: give the battery a proper trough to buy into and a real evening peak to sell into, and the returns follow.


<details>
<summary>Half-hourly data — 2026-07-25</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 201.24 | 60.6% |
| 2 | 23:30 | 184.63 | 58.3% |
| 3 | 00:00 | 172.60 | 32.5% |
| 4 | 00:30 | 165.70 | 38.4% |
| 5 | 01:00 | 159.10 | 37.8% |
| 6 | 01:30 | 154.97 | 38.3% |
| 7 | 02:00 | 151.07 | 40.3% |
| 8 | 02:30 | 148.43 | 40.5% |
| 9 | 03:00 | 140.68 | 41.9% |
| 10 | 03:30 | 137.00 | 41.1% |
| 11 | 04:00 | 132.62 | 40.8% |
| 12 | 04:30 | 129.97 | 41.0% |
| 13 | 05:00 | 125.44 | 43.3% |
| 14 | 05:30 | 122.01 | 46.8% |
| 15 | 06:00 | 116.42 | 50.8% |
| 16 | 06:30 | 114.87 | 47.5% |
| 17 | 07:00 | 93.01 | 44.2% |
| 18 | 07:30 | 93.01 | 42.1% |
| 19 | 08:00 | 37.59 | 39.7% |
| 20 | 08:30 | 37.38 | 29.1% |
| 21 | 09:00 | 20.86 | 25.8% |
| 22 | 09:30 | 34.78 | 25.9% |
| 23 | 10:00 | 40.00 | 28.3% |
| 24 | 10:30 | 55.97 | 33.5% |
| 25 | 11:00 | 70.07 | 33.6% |
| 26 | 11:30 | 75.37 | 32.6% |
| 27 | 12:00 | 91.50 | 31.6% |
| 28 | 12:30 | 95.00 | 29.2% |
| 29 | 13:00 | 108.68 | 30.5% |
| 30 | 13:30 | 109.91 | 27.4% |
| 31 | 14:00 | 110.76 | 27.5% |
| 32 | 14:30 | 110.71 | 26.9% |
| 33 | 15:00 | 109.44 | 27.4% |
| 34 | 15:30 | 111.67 | 28.2% |
| 35 | 16:00 | 101.17 | 28.2% |
| 36 | 16:30 | 114.89 | 27.4% |
| 37 | 17:00 | 136.37 | 31.9% |
| 38 | 17:30 | 156.21 | 33.0% |
| 39 | 18:00 | 163.95 | 33.4% |
| 40 | 18:30 | 170.00 | 33.6% |
| 41 | 19:00 | 178.44 | 35.9% |
| 42 | 19:30 | 178.44 | 37.5% |
| 43 | 20:00 | 185.00 | 37.7% |
| 44 | 20:30 | 183.11 | 39.1% |
| 45 | 21:00 | 192.24 | 41.9% |
| 46 | 21:30 | 188.99 | 47.0% |
| 47 | 22:00 | 191.13 | 50.9% |
| 48 | 22:30 | 188.33 | 59.0% |

</details>

