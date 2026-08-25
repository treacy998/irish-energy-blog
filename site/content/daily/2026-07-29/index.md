---
title: "I-SEM Daily Briefing — 29 July 2026"
date: 2026-07-29
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €174.75/MWh, peaking at €223.09/MWh at 20:00."
images: ["charts/2026-07-29/card-2026-07-29.png"]
draft: false
---

{{< statbar mean="€174.75" peak="€223.09" min="€141.56" spread="€81.53" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €174.75/MWh    |
| Median Price         | €163.22/MWh    |
| Std Dev              | €28.14/MWh    |
| Peak Price           | €223.09/MWh (20:00) |
| Min Price            | €141.56/MWh (14:00)   |
| Price Range          | €81.53/MWh   |
| Periods above €150   | 38 of 48 (79%) |
| Periods above €200   | 12 of 48 (25%) |
| Peak Avg (07–22)     | €183.52/MWh    |
| Off-peak Avg (22–07) | €160.13/MWh    |
| Peak/Off-Peak Spread | €23.39/MWh   |
| Wind % of Demand     | 14.5%          |
| Wind Range           | 9.3%–23.2% |
| Mean Demand          | 3942 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-07-29/dam-2026-07-29.png)

**Std dev** €28.14/MWh  ·  **Median** €163.22/MWh  ·  **Periods above €150:** 38 of 48 (79%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-07-29/price-wind-2026-07-29.png)

**Mean wind:** 14.5%  ·  **Range:** 9.3%–23.2%

## Week in Context

![7-Day Price Comparison](/charts/2026-07-29/week-compare-2026-07-29.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-07-29/pdc-2026-07-29.png)

**Periods above €150:** 38 (79% of day)  ·  **Above €200:** 12 (25% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-07-29/spread-2026-07-29.png)

**Peak avg (07:00–22:00):** €183.52/MWh  ·  **Off-peak avg:** €160.13/MWh  ·  **Spread:** €23.39/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €143/MWh | 13:00 | 2 MWh | −€285 |
| **Discharge** | €222/MWh | 19:00 | 1.7 MWh (85% RTE) | +€378 |
| **Gross profit** | | | | **€93** |
| **Price spread** | €80/MWh | | | **ROI: 32.5%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-07-29/bess-2026-07-29.png)

## Commentary

Wind dropped back to 14.5%, the second-lowest reading of the week, and the market responded exactly as it did on Thursday: flat and high, with 38 of 48 periods clearing above €150 and a full quarter of the day above €200. The morning ramp from 06:30 to 09:00 pushed price from €174.40 to a €215+ plateau as wind sat under 12%, and the evening did the same thing again — wind falling from 13% at 17:00 to 9.3% by 20:30 drove price to the day's €223.09 peak.

There was barely a trough at all. The cheapest period, €141.56 at 14:00, is higher than several days' peaks this week. Peak/off-peak spread came in positive at €23.39, back in line with Monday and Thursday — whenever wind sits under 20%, this market simply runs tight all day, with no meaningful daytime relief.

Storage cleared €93 gross on a 32.5% ROI — respectable, but nowhere near the wind-day numbers from Saturday and Sunday. The week bookends neatly: it opened on a thin, low-wind Thursday and closes on much the same shape. The volatile middle of the week was the exception, not the rule, and that's exactly when the battery made its money.


<details>
<summary>Half-hourly data — 2026-07-29</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 165.00 | 12.6% |
| 2 | 23:30 | 160.00 | 13.6% |
| 3 | 00:00 | 153.26 | 23.2% |
| 4 | 00:30 | 151.08 | 21.7% |
| 5 | 01:00 | 147.29 | 20.1% |
| 6 | 01:30 | 145.05 | 20.3% |
| 7 | 02:00 | 152.30 | 19.8% |
| 8 | 02:30 | 151.17 | 17.8% |
| 9 | 03:00 | 150.74 | 17.4% |
| 10 | 03:30 | 150.50 | 16.9% |
| 11 | 04:00 | 153.26 | 15.5% |
| 12 | 04:30 | 152.80 | 15.6% |
| 13 | 05:00 | 160.04 | 15.1% |
| 14 | 05:30 | 161.45 | 14.0% |
| 15 | 06:00 | 169.97 | 11.7% |
| 16 | 06:30 | 174.40 | 10.9% |
| 17 | 07:00 | 189.60 | 10.1% |
| 18 | 07:30 | 208.73 | 10.7% |
| 19 | 08:00 | 215.00 | 11.5% |
| 20 | 08:30 | 215.14 | 13.9% |
| 21 | 09:00 | 214.00 | 14.8% |
| 22 | 09:30 | 200.00 | 14.5% |
| 23 | 10:00 | 185.63 | 14.4% |
| 24 | 10:30 | 172.79 | 15.0% |
| 25 | 11:00 | 156.49 | 16.3% |
| 26 | 11:30 | 156.49 | 17.7% |
| 27 | 12:00 | 147.74 | 16.5% |
| 28 | 12:30 | 147.30 | 17.0% |
| 29 | 13:00 | 143.32 | 16.7% |
| 30 | 13:30 | 142.37 | 15.5% |
| 31 | 14:00 | 141.56 | 15.7% |
| 32 | 14:30 | 143.07 | 15.2% |
| 33 | 15:00 | 146.86 | 16.4% |
| 34 | 15:30 | 148.59 | 16.3% |
| 35 | 16:00 | 152.79 | 15.3% |
| 36 | 16:30 | 172.80 | 14.8% |
| 37 | 17:00 | 175.86 | 13.9% |
| 38 | 17:30 | 196.21 | 12.1% |
| 39 | 18:00 | 207.01 | 11.2% |
| 40 | 18:30 | 211.72 | 11.2% |
| 41 | 19:00 | 222.16 | 10.1% |
| 42 | 19:30 | 221.87 | 10.6% |
| 43 | 20:00 | 223.09 | 10.0% |
| 44 | 20:30 | 222.01 | 9.3% |
| 45 | 21:00 | 213.51 | 9.7% |
| 46 | 21:30 | 212.00 | 11.0% |
| 47 | 22:00 | 199.00 | 11.0% |
| 48 | 22:30 | 185.00 | 11.6% |

</details>

