---
title: "I-SEM Daily Briefing — 5 August 2026"
date: 2026-08-05
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €109.05/MWh, peaking at €192.1/MWh at 22:00."
images: ["charts/2026-08-05/card-2026-08-05.png"]
draft: false
---

{{< statbar mean="€109.05" peak="€192.1" min="€8.12" spread="€183.98" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €109.05/MWh    |
| Median Price         | €140.83/MWh    |
| Std Dev              | €62.41/MWh    |
| Peak Price           | €192.1/MWh (22:00) |
| Min Price            | €8.12/MWh (13:30)   |
| Price Range          | €183.98/MWh   |
| Periods above €150   | 14 of 48 (29%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €83.98/MWh    |
| Off-peak Avg (22–07) | €150.84/MWh    |
| Peak/Off-Peak Spread | €-66.86/MWh   |
| Wind % of Demand     | 42.3%          |
| Wind Range           | 22.9%–61.1% |
| Mean Demand          | 3724 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-05/dam-2026-08-05.png)

**Std dev** €62.41/MWh  ·  **Median** €140.83/MWh  ·  **Periods above €150:** 14 of 48 (29%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-05/price-wind-2026-08-05.png)

**Mean wind:** 42.3%  ·  **Range:** 22.9%–61.1%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-05/week-compare-2026-08-05.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-05/pdc-2026-08-05.png)

**Periods above €150:** 14 (29% of day)  ·  **Above €200:** 0 (0% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-05/spread-2026-08-05.png)

**Peak avg (07:00–22:00):** €83.98/MWh  ·  **Off-peak avg:** €150.84/MWh  ·  **Spread:** €-66.86/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €9/MWh | 13:00 | 2 MWh | −€18 |
| **Discharge** | €181/MWh | 20:30 | 1.7 MWh (85% RTE) | +€307 |
| **Gross profit** | | | | **€289** |
| **Price spread** | €172/MWh | | | **ROI: 1603.8%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-05/bess-2026-08-05.png)

## Commentary

Wednesday is the week's outlier, and it isn't close. Wind averaged 42.3% of demand and peaked at 61.1%, and the merit order showed it: price fell off a cliff from a €150 mid-morning level down to single digits by 10:00, bottoming at €8.12 at 13:30 and holding under €15 for nearly two hours either side of it. That's cannibalisation working exactly as advertised — once wind is deep enough into the stack, every extra MWh of it pushes gas out and the clearing price collapses toward zero.

The knock-on effect flips the daily rhythm on its head. Peak avg (07:00–22:00) came in at €83.98 against an off-peak avg of €150.84 — a spread of **-€66.86**, the week's only negative-shape day of this scale, because the cheap hours are the sunny, windy afternoon rather than the small hours. Std dev of €62.41 is more than double any other day this week.

For storage this was a gift: charge at €9 for 2 MWh (–€18) and discharge into the €181 evening peak for +€307, netting €289 gross — over three times any other day's return this week, for a 1,600%+ ROI. This is the clean illustration of the rule: storage revenue comes from volatility, not price level, and today's near-zero trough manufactured more of it than a whole week of gas-set days combined.


<details>
<summary>Half-hourly data — 2026-08-05</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 162.90 | 24.6% |
| 2 | 23:30 | 156.64 | 25.3% |
| 3 | 00:00 | 154.16 | 52.3% |
| 4 | 00:30 | 151.00 | 56.9% |
| 5 | 01:00 | 148.83 | 57.3% |
| 6 | 01:30 | 145.89 | 56.7% |
| 7 | 02:00 | 143.78 | 56.3% |
| 8 | 02:30 | 140.79 | 56.1% |
| 9 | 03:00 | 139.95 | 59.1% |
| 10 | 03:30 | 139.40 | 59.1% |
| 11 | 04:00 | 140.87 | 61.1% |
| 12 | 04:30 | 140.50 | 60.9% |
| 13 | 05:00 | 144.27 | 61.0% |
| 14 | 05:30 | 145.94 | 61.1% |
| 15 | 06:00 | 146.05 | 60.7% |
| 16 | 06:30 | 150.23 | 57.4% |
| 17 | 07:00 | 144.26 | 55.7% |
| 18 | 07:30 | 144.99 | 54.5% |
| 19 | 08:00 | 122.08 | 49.5% |
| 20 | 08:30 | 120.03 | 49.2% |
| 21 | 09:00 | 81.23 | 47.1% |
| 22 | 09:30 | 73.05 | 43.9% |
| 23 | 10:00 | 27.13 | 41.8% |
| 24 | 10:30 | 23.36 | 42.0% |
| 25 | 11:00 | 15.00 | 37.7% |
| 26 | 11:30 | 11.68 | 33.5% |
| 27 | 12:00 | 9.90 | 28.8% |
| 28 | 12:30 | 10.00 | 29.7% |
| 29 | 13:00 | 9.43 | 29.3% |
| 30 | 13:30 | 8.12 | 26.8% |
| 31 | 14:00 | 8.79 | 24.7% |
| 32 | 14:30 | 9.70 | 23.7% |
| 33 | 15:00 | 9.81 | 22.9% |
| 34 | 15:30 | 13.04 | 23.8% |
| 35 | 16:00 | 52.56 | 30.8% |
| 36 | 16:30 | 64.00 | 38.0% |
| 37 | 17:00 | 110.37 | 46.3% |
| 38 | 17:30 | 120.00 | 43.7% |
| 39 | 18:00 | 147.00 | 42.5% |
| 40 | 18:30 | 151.57 | 44.8% |
| 41 | 19:00 | 164.55 | 42.8% |
| 42 | 19:30 | 166.90 | 38.9% |
| 43 | 20:00 | 170.51 | 36.3% |
| 44 | 20:30 | 179.00 | 32.6% |
| 45 | 21:00 | 172.97 | 29.4% |
| 46 | 21:30 | 178.33 | 26.6% |
| 47 | 22:00 | 192.10 | 23.7% |
| 48 | 22:30 | 171.91 | 24.0% |

</details>

