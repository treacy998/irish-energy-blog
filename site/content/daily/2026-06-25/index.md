---
title: "I-SEM Daily Briefing — 25 June 2026"
date: 2026-06-25
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €149.31/MWh, peaking at €240.43/MWh at 20:30."
images: ["charts/2026-06-25/card-2026-06-25.png"]
draft: false
---

{{< statbar mean="€149.31" peak="€240.43" min="€104.0" spread="€136.43" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €149.31/MWh    |
| Median Price         | €133.85/MWh    |
| Std Dev              | €46.13/MWh    |
| Peak Price           | €240.43/MWh (20:30) |
| Min Price            | €104.0/MWh (13:30)   |
| Price Range          | €136.43/MWh   |
| Periods above €150   | 15 of 48 (31%) |
| Periods above €200   | 11 of 48 (23%) |
| Peak Avg (07–22)     | €147.08/MWh    |
| Off-peak Avg (22–07) | €153.02/MWh    |
| Peak/Off-Peak Spread | €-5.94/MWh   |
| Wind % of Demand     | 26.8%          |
| Wind Range           | 6.7%–49.4% |
| Mean Demand          | 3889 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-06-25/dam-2026-06-25.png)

**Std dev** €46.13/MWh  ·  **Median** €133.85/MWh  ·  **Periods above €150:** 15 of 48 (31%)

Wind is back, and the mean dropped €64 on Wednesday — from €213.03 to €149.31. The median (€133.85) well below the mean reflects the shape: a large block of genuinely cheap daytime periods (€104–141 from 03:00–16:30) suppressed by wind, and a smaller block of expensive evening periods pulling the average back up. The floor at €104.00 is the lowest since Saturday — wind actually moved the market this time.

## Price vs Wind

![Price vs Wind Generation](/charts/2026-06-25/price-wind-2026-06-25.png)

**Mean wind:** 26.8%  ·  **Range:** 6.7%–49.4%

A full wind arc, written perfectly into the price profile. Wind built overnight (10% at 23:00 → 49.4% at 05:00) and prices fell with it (€201 at 23:00 → €104 by 10:30). Then wind declined through the afternoon (49% at 05:00 → 6.7% at 20:30) and prices rose back in lock-step (€104 at 13:30 → €240 at 20:30). Cause and effect over a 24-hour arc — every half-hour the wind dropped, the price rose in mirror image.

## Week in Context

![7-Day Price Comparison](/charts/2026-06-25/week-compare-2026-06-25.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-06-25/pdc-2026-06-25.png)

**Periods above €150:** 15 (31% of day)  ·  **Above €200:** 11 (23% of day)

Two distinct populations. 33 periods below €150 — the wind-suppressed daytime, with a flat floor around €104–107. Then 15 expensive periods as wind withdrew, including 11 clearing above €200. The curve has a long flat cheap section at the bottom and a steep spike at the top. Wind created both ends: surplus kept the floor down; withdrawal sent the ceiling up.

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-06-25/spread-2026-06-25.png)

**Peak avg (07:00–22:00):** €147.08/MWh  ·  **Off-peak avg:** €153.02/MWh  ·  **Spread:** €-5.94/MWh

Barely negative at €-5.94. Off-peak (€153.02) is hauled up by the 23:00 tail from Wednesday's scarcity (€201.00) and the late-evening prices staying elevated (€206-226 from 22:00-22:30). The peak window contains both the wind-cheap morning and the expensive evening — they cancel in the average. The label says negative; the intraday range of €136.43 says the day had real structure.

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €104/MWh | 12:30 | 2 MWh | −€209 |
| **Discharge** | €240/MWh | 19:30 | 1.7 MWh (85% RTE) | +€408 |
| **Gross profit** | | | | **€199** |
| **Price spread** | €136/MWh | | | **ROI: 95.4%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-06-25/bess-2026-06-25.png)

Charge at €104 at 12:30 — wind at 37.6%, prices flatlined at €104-105 for six hours. Discharge at €240 at 19:30 — wind at 11.2%, evening demand at its peak. €199 gross, ROI 95.4%. Second best BESS day of the week. Unlike Wednesday's record — which was pure scarcity premium — today's spread came from wind architecture: charge in the surplus, discharge as wind withdrew. Cleaner and more repeatable.

## Commentary

Wind returned and the market felt it immediately. Mean €149.31 — down €64 on Wednesday's record. The day has a satisfying symmetry: wind built through the night (10% → 49% by 05:00), suppressed prices through the daytime (€104-141 from 03:00-16:30), then declined through the afternoon (49% → 6.7% by 20:30) as demand peaked, driving the evening to €240.

Wednesday's scarcity still cast a shadow — the 23:00 open (€201.00) was the tail of the previous day's extreme, and overnight prices didn't fully clear until wind hit 30%+ after 03:00. From there, the wind did what it's supposed to: suppress the merit order, bring the floor down to €104, give consumers cheap electricity through the working day.

The evening spike is wind leaving at the wrong time, again. But at €240 versus Wednesday's €414, it's orderly. Two consecutive days of wide BESS swings — €388 gross on Wednesday, €199 on Thursday. The system rewards storage when wind is volatile. The system needs wind to stay through the evening.


<details>
<summary>Half-hourly data — 2026-06-25</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 201.00 | 10.2% |
| 2 | 23:30 | 181.00 | 11.8% |
| 3 | 00:00 | 170.76 | 18.4% |
| 4 | 00:30 | 155.00 | 19.6% |
| 5 | 01:00 | 146.01 | 21.4% |
| 6 | 01:30 | 142.18 | 23.2% |
| 7 | 02:00 | 139.00 | 24.6% |
| 8 | 02:30 | 135.20 | 28.7% |
| 9 | 03:00 | 130.10 | 33.2% |
| 10 | 03:30 | 126.57 | 38.4% |
| 11 | 04:00 | 126.99 | 42.7% |
| 12 | 04:30 | 126.99 | 46.6% |
| 13 | 05:00 | 130.11 | 49.4% |
| 14 | 05:30 | 132.50 | 47.9% |
| 15 | 06:00 | 136.09 | 44.1% |
| 16 | 06:30 | 141.40 | 42.7% |
| 17 | 07:00 | 136.16 | 39.7% |
| 18 | 07:30 | 138.81 | 35.9% |
| 19 | 08:00 | 125.14 | 32.0% |
| 20 | 08:30 | 122.08 | 29.5% |
| 21 | 09:00 | 116.04 | 29.2% |
| 22 | 09:30 | 112.44 | 33.5% |
| 23 | 10:00 | 107.00 | 34.2% |
| 24 | 10:30 | 104.86 | 33.6% |
| 25 | 11:00 | 104.86 | 36.3% |
| 26 | 11:30 | 104.86 | 39.0% |
| 27 | 12:00 | 104.85 | 39.7% |
| 28 | 12:30 | 104.85 | 37.6% |
| 29 | 13:00 | 104.88 | 37.4% |
| 30 | 13:30 | 104.00 | 34.9% |
| 31 | 14:00 | 104.00 | 34.9% |
| 32 | 14:30 | 104.85 | 32.5% |
| 33 | 15:00 | 105.00 | 30.1% |
| 34 | 15:30 | 107.20 | 26.1% |
| 35 | 16:00 | 115.44 | 22.5% |
| 36 | 16:30 | 126.85 | 19.3% |
| 37 | 17:00 | 148.10 | 14.1% |
| 38 | 17:30 | 167.74 | 11.6% |
| 39 | 18:00 | 202.82 | 10.3% |
| 40 | 18:30 | 215.00 | 11.8% |
| 41 | 19:00 | 228.10 | 10.2% |
| 42 | 19:30 | 240.00 | 11.2% |
| 43 | 20:00 | 240.02 | 9.0% |
| 44 | 20:30 | 240.43 | 6.7% |
| 45 | 21:00 | 240.01 | 6.7% |
| 46 | 21:30 | 236.04 | 10.9% |
| 47 | 22:00 | 226.56 | 11.3% |
| 48 | 22:30 | 206.90 | 10.9% |

</details>

