---
title: "I-SEM Daily Briefing — 30 June 2026"
date: 2026-06-30
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €148.19/MWh, peaking at €215.5/MWh at 18:30."
images: ["charts/2026-06-30/card-2026-06-30.png"]
draft: false
---

{{< statbar mean="€148.19" peak="€215.5" min="€109.9" spread="€105.6" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €148.19/MWh    |
| Median Price         | €126.86/MWh    |
| Std Dev              | €38.03/MWh    |
| Peak Price           | €215.5/MWh (18:30) |
| Min Price            | €109.9/MWh (14:30)   |
| Price Range          | €105.6/MWh   |
| Periods above €150   | 20 of 48 (42%) |
| Periods above €200   | 8 of 48 (17%) |
| Peak Avg (07–22)     | €162.63/MWh    |
| Off-peak Avg (22–07) | €124.12/MWh    |
| Peak/Off-Peak Spread | €38.51/MWh   |
| Wind % of Demand     | 33.7%          |
| Wind Range           | 13.2%–58.1% |
| Mean Demand          | 3817 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-06-30/dam-2026-06-30.png)

**Std dev** €38.03/MWh  ·  **Median** €126.86/MWh  ·  **Periods above €150:** 20 of 48 (42%)

The cleanest wind arc of the week. Overnight wind held near 55-58%, sinking price to a €110 floor, then wind fell steadily through the day into a 38% evening plateau — right as demand peaked. €215.50 at 18:30.

## Price vs Wind

![Price vs Wind Generation](/charts/2026-06-30/price-wind-2026-06-30.png)

**Mean wind:** 33.7%  ·  **Range:** 13.2%–58.1%

The clearest cause-effect chart of the week. Wind at 55-58% through the small hours capped price near €110-115; from 07:00 it fell in a straight line to 37% by evening, and price rose in lockstep to €215. Textbook.

## Week in Context

![7-Day Price Comparison](/charts/2026-06-30/week-compare-2026-06-30.png)

Back to Thursday/Friday territory — the week ends almost exactly where it started.

## Price Duration Curve

![Price Duration Curve](/charts/2026-06-30/pdc-2026-06-30.png)

**Periods above €150:** 20 (42% of day)  ·  **Above €200:** 8 (17% of day)

A real ceiling this time, the sharpest since Thursday.

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-06-30/spread-2026-06-30.png)

**Peak avg (07:00–22:00):** €162.63/MWh  ·  **Off-peak avg:** €124.12/MWh  ·  **Spread:** €38.51/MWh

Widest positive spread of the week. A genuine cheap overnight window this time, not just a flat floor.

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €111/MWh | 13:30 | 2 MWh | −€221 |
| **Discharge** | €207/MWh | 18:00 | 1.7 MWh (85% RTE) | +€352 |
| **Gross profit** | | | | **€131** |
| **Price spread** | €97/MWh | | | **ROI: 59.2%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-06-30/bess-2026-06-30.png)

€131 gross, ROI 59%. Charge at the €110 overnight floor while wind held above 55%, discharge into the €207 evening ramp. A clean, repeatable wind-arc trade — the best-defined BESS setup all week.

## Commentary

Tuesday closed the week on the cleanest structure yet. High overnight wind (near 58%) built a real floor, then a steady decline through the day handed the evening ramp straight through to €215.50 — no oversupply, no scarcity extreme, just wind leaving as demand arrived.

It's a useful bookend against Saturday and Sunday. Same ingredient — plenty of wind — produced a completely different market depending on when it showed up. High wind overnight with a clean withdrawal by evening is healthy market behaviour; high wind sitting flat through a collapsed weekend demand is a giveaway. Same wind, opposite outcome — it's all about timing against demand.


<details>
<summary>Half-hourly data — 2026-06-30</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 121.65 | 29.3% |
| 2 | 23:30 | 113.20 | 29.7% |
| 3 | 00:00 | 116.07 | 53.3% |
| 4 | 00:30 | 116.07 | 55.4% |
| 5 | 01:00 | 114.06 | 56.5% |
| 6 | 01:30 | 111.00 | 57.5% |
| 7 | 02:00 | 115.00 | 56.8% |
| 8 | 02:30 | 110.54 | 57.6% |
| 9 | 03:00 | 113.53 | 56.7% |
| 10 | 03:30 | 113.29 | 58.1% |
| 11 | 04:00 | 113.83 | 52.4% |
| 12 | 04:30 | 111.65 | 49.5% |
| 13 | 05:00 | 114.80 | 46.1% |
| 14 | 05:30 | 113.00 | 42.6% |
| 15 | 06:00 | 124.07 | 34.8% |
| 16 | 06:30 | 135.89 | 29.1% |
| 17 | 07:00 | 147.66 | 24.6% |
| 18 | 07:30 | 181.18 | 20.8% |
| 19 | 08:00 | 180.01 | 18.4% |
| 20 | 08:30 | 195.93 | 16.3% |
| 21 | 09:00 | 203.00 | 16.3% |
| 22 | 09:30 | 181.97 | 14.3% |
| 23 | 10:00 | 174.87 | 13.7% |
| 24 | 10:30 | 165.80 | 13.9% |
| 25 | 11:00 | 158.60 | 13.2% |
| 26 | 11:30 | 134.51 | 13.6% |
| 27 | 12:00 | 125.13 | 14.2% |
| 28 | 12:30 | 122.70 | 15.8% |
| 29 | 13:00 | 112.00 | 16.8% |
| 30 | 13:30 | 110.08 | 18.0% |
| 31 | 14:00 | 110.36 | 20.3% |
| 32 | 14:30 | 109.90 | 23.2% |
| 33 | 15:00 | 111.92 | 26.4% |
| 34 | 15:30 | 112.60 | 32.4% |
| 35 | 16:00 | 125.00 | 36.8% |
| 36 | 16:30 | 128.60 | 37.6% |
| 37 | 17:00 | 167.81 | 39.4% |
| 38 | 17:30 | 176.45 | 37.9% |
| 39 | 18:00 | 208.34 | 37.7% |
| 40 | 18:30 | 215.50 | 38.9% |
| 41 | 19:00 | 199.57 | 37.6% |
| 42 | 19:30 | 204.90 | 35.9% |
| 43 | 20:00 | 204.00 | 36.5% |
| 44 | 20:30 | 205.00 | 36.2% |
| 45 | 21:00 | 204.49 | 36.8% |
| 46 | 21:30 | 201.10 | 37.9% |
| 47 | 22:00 | 191.15 | 35.4% |
| 48 | 22:30 | 185.30 | 34.2% |

</details>

