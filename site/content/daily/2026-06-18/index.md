---
title: "I-SEM Daily Briefing — 18 June 2026"
date: 2026-06-18
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €138.77/MWh, peaking at €194.5/MWh at 19:30."
images: ["charts/2026-06-18/card-2026-06-18.png"]
draft: false
---

{{< statbar mean="€138.77" peak="€194.5" min="€111.55" spread="€82.95" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €138.77/MWh    |
| Median Price         | €127.81/MWh    |
| Std Dev              | €24.52/MWh    |
| Peak Price           | €194.5/MWh (19:30) |
| Min Price            | €111.55/MWh (15:00)   |
| Price Range          | €82.95/MWh   |
| Periods above €150   | 11 of 48 (23%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €142.96/MWh    |
| Off-peak Avg (22–07) | €131.77/MWh    |
| Peak/Off-Peak Spread | €11.19/MWh   |
| Wind % of Demand     | 31.5%          |
| Wind Range           | 24.5%–46.6% |
| Mean Demand          | 3957 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-06-18/dam-2026-06-18.png)

**Std dev** €24.52/MWh  ·  **Median** €127.81/MWh  ·  **Periods above €150:** 11 of 48 (23%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-06-18/price-wind-2026-06-18.png)

**Mean wind:** 31.5%  ·  **Range:** 24.5%–46.6%

## Week in Context

![7-Day Price Comparison](/charts/2026-06-18/week-compare-2026-06-18.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-06-18/pdc-2026-06-18.png)

**Periods above €150:** 11 (23% of day)  ·  **Above €200:** 0 (0% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-06-18/spread-2026-06-18.png)

**Peak avg (07:00–22:00):** €142.96/MWh  ·  **Off-peak avg:** €131.77/MWh  ·  **Spread:** €11.19/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €115/MWh | 13:30 | 2 MWh | −€230 |
| **Discharge** | €191/MWh | 19:00 | 1.7 MWh (85% RTE) | +€325 |
| **Gross profit** | | | | **€95** |
| **Price spread** | €76/MWh | | | **ROI: 41.3%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-06-18/bess-2026-06-18.png)

<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->

## Commentary

Today was the calmest day in a while — mean €138.77, and not a single half-hour broke €200. Wind running at 31.5% kept a lid on things across the board.

The overnight wind glut (40-46% through 03:00-06:00) held the floor flat around €120-130, and the midday trough went even lower as soft demand met still-decent wind, bottoming at €111.55 by 15:00. Then wind eased off into the evening (down to 24-26% from 17:00) just as residential demand woke up, and the whole day's volatility got crammed into one sharp ramp — €137 at 16:00 to €194.50 by 19:30.

That ramp is also why the peak/off-peak spread looks oddly thin (€11.19) on an €83 full-day range: the "peak" window swallows both the cheap midday hours and the expensive evening ones, so they cancel out. The battery still did well off the raw volatility — charged at €115 midday, discharged into the €191 evening spike, €95 gross. A good day for wind, a quiet one for everyone else.


<details>
<summary>Half-hourly data — 2026-06-18</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 146.64 | 33.5% |
| 2 | 23:30 | 138.71 | 37.4% |
| 3 | 00:00 | 134.90 | 26.4% |
| 4 | 00:30 | 129.29 | 28.9% |
| 5 | 01:00 | 126.01 | 30.4% |
| 6 | 01:30 | 124.00 | 32.3% |
| 7 | 02:00 | 124.85 | 33.4% |
| 8 | 02:30 | 122.01 | 34.5% |
| 9 | 03:00 | 121.00 | 39.2% |
| 10 | 03:30 | 121.00 | 42.1% |
| 11 | 04:00 | 124.00 | 44.0% |
| 12 | 04:30 | 122.59 | 45.0% |
| 13 | 05:00 | 126.00 | 46.6% |
| 14 | 05:30 | 128.95 | 45.3% |
| 15 | 06:00 | 127.28 | 44.7% |
| 16 | 06:30 | 131.53 | 41.2% |
| 17 | 07:00 | 131.00 | 38.3% |
| 18 | 07:30 | 136.01 | 34.0% |
| 19 | 08:00 | 132.67 | 31.4% |
| 20 | 08:30 | 128.34 | 29.9% |
| 21 | 09:00 | 127.00 | 29.4% |
| 22 | 09:30 | 124.88 | 28.9% |
| 23 | 10:00 | 118.03 | 27.7% |
| 24 | 10:30 | 115.00 | 27.9% |
| 25 | 11:00 | 123.69 | 27.9% |
| 26 | 11:30 | 121.00 | 25.8% |
| 27 | 12:00 | 126.38 | 27.2% |
| 28 | 12:30 | 121.00 | 29.0% |
| 29 | 13:00 | 121.53 | 28.6% |
| 30 | 13:30 | 114.80 | 27.1% |
| 31 | 14:00 | 121.00 | 27.8% |
| 32 | 14:30 | 112.77 | 26.4% |
| 33 | 15:00 | 111.55 | 25.4% |
| 34 | 15:30 | 121.00 | 25.1% |
| 35 | 16:00 | 137.18 | 24.5% |
| 36 | 16:30 | 144.14 | 25.1% |
| 37 | 17:00 | 144.60 | 25.1% |
| 38 | 17:30 | 165.42 | 25.4% |
| 39 | 18:00 | 175.40 | 26.0% |
| 40 | 18:30 | 180.91 | 24.7% |
| 41 | 19:00 | 192.87 | 26.2% |
| 42 | 19:30 | 194.50 | 26.0% |
| 43 | 20:00 | 190.15 | 27.8% |
| 44 | 20:30 | 187.44 | 29.2% |
| 45 | 21:00 | 188.00 | 30.4% |
| 46 | 21:30 | 180.60 | 31.8% |
| 47 | 22:00 | 166.41 | 33.4% |
| 48 | 22:30 | 156.77 | 33.5% |

</details>

