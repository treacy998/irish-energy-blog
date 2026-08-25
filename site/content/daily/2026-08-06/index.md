---
title: "I-SEM Daily Briefing — 6 August 2026"
date: 2026-08-06
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €156.67/MWh, peaking at €226.11/MWh at 19:30."
images: ["charts/2026-08-06/card-2026-08-06.png"]
draft: false
---

{{< statbar mean="€156.67" peak="€226.11" min="€126.32" spread="€99.79" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €156.67/MWh    |
| Median Price         | €143.57/MWh    |
| Std Dev              | €30.93/MWh    |
| Peak Price           | €226.11/MWh (19:30) |
| Min Price            | €126.32/MWh (12:00)   |
| Price Range          | €99.79/MWh   |
| Periods above €150   | 21 of 48 (44%) |
| Periods above €200   | 7 of 48 (15%) |
| Peak Avg (07–22)     | €165.2/MWh    |
| Off-peak Avg (22–07) | €142.45/MWh    |
| Peak/Off-Peak Spread | €22.75/MWh   |
| Wind % of Demand     | 13.2%          |
| Wind Range           | 4.0%–25.8% |
| Mean Demand          | 3815 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-06/dam-2026-08-06.png)

**Std dev** €30.93/MWh  ·  **Median** €143.57/MWh  ·  **Periods above €150:** 21 of 48 (44%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-06/price-wind-2026-08-06.png)

**Mean wind:** 13.2%  ·  **Range:** 4.0%–25.8%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-06/week-compare-2026-08-06.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-06/pdc-2026-08-06.png)

**Periods above €150:** 21 (44% of day)  ·  **Above €200:** 7 (15% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-06/spread-2026-08-06.png)

**Peak avg (07:00–22:00):** €165.2/MWh  ·  **Off-peak avg:** €142.45/MWh  ·  **Spread:** €22.75/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €128/MWh | 11:00 | 2 MWh | −€255 |
| **Discharge** | €216/MWh | 18:30 | 1.7 MWh (85% RTE) | +€367 |
| **Gross profit** | | | | **€111** |
| **Price spread** | €88/MWh | | | **ROI: 43.6%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-06/bess-2026-08-06.png)

## Commentary

Wind collapsed overnight — from 61% on Wednesday to a mean of 13.2%, dipping as low as 4.0% through the mid-morning — and gas took the market straight back. This was the inverse of yesterday almost hour for hour: where Wednesday cannibalised itself into single digits, Thursday built into a €226.11 evening peak, the highest of the week, with 7 of 48 periods clearing €200.

The shape tells the same story twice over. A steep pre-dawn ramp pushed price to €197.76 by 07:30, right as wind bottomed out at 4.8%; it eased through a shallow €126.32 midday trough once demand slackened, then climbed hard from 17:00 into a sustained 200+ plateau from 19:00 to 21:30. Peak/off-peak spread flipped back positive at €22.75, restoring the normal daytime-expensive shape that Wednesday's wind glut had inverted.

Storage did well out of it — €128 charge against a €216 discharge, €111 gross, 43.6% ROI — a solid, unremarkable return built on an ordinary low-wind evening squeeze rather than anything exotic. Two days, two completely different markets, same underlying cause: wind sets the floor, and its absence sets the ceiling.


<details>
<summary>Half-hourly data — 2026-08-06</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 151.00 | 16.4% |
| 2 | 23:30 | 136.60 | 16.3% |
| 3 | 00:00 | 134.00 | 25.8% |
| 4 | 00:30 | 128.74 | 23.9% |
| 5 | 01:00 | 126.82 | 22.5% |
| 6 | 01:30 | 126.90 | 21.2% |
| 7 | 02:00 | 131.90 | 20.6% |
| 8 | 02:30 | 130.20 | 21.2% |
| 9 | 03:00 | 130.20 | 20.1% |
| 10 | 03:30 | 134.06 | 17.6% |
| 11 | 04:00 | 133.40 | 16.7% |
| 12 | 04:30 | 133.00 | 15.5% |
| 13 | 05:00 | 139.86 | 14.2% |
| 14 | 05:30 | 142.86 | 12.2% |
| 15 | 06:00 | 146.12 | 11.1% |
| 16 | 06:30 | 155.90 | 9.4% |
| 17 | 07:00 | 182.05 | 8.9% |
| 18 | 07:30 | 197.76 | 6.8% |
| 19 | 08:00 | 189.65 | 4.8% |
| 20 | 08:30 | 182.70 | 4.0% |
| 21 | 09:00 | 156.61 | 4.8% |
| 22 | 09:30 | 151.00 | 5.1% |
| 23 | 10:00 | 145.00 | 4.6% |
| 24 | 10:30 | 133.91 | 4.8% |
| 25 | 11:00 | 129.77 | 5.8% |
| 26 | 11:30 | 126.50 | 7.1% |
| 27 | 12:00 | 126.32 | 7.6% |
| 28 | 12:30 | 127.98 | 9.1% |
| 29 | 13:00 | 133.24 | 9.6% |
| 30 | 13:30 | 128.38 | 11.2% |
| 31 | 14:00 | 126.32 | 12.4% |
| 32 | 14:30 | 131.50 | 13.0% |
| 33 | 15:00 | 136.83 | 13.2% |
| 34 | 15:30 | 142.00 | 14.4% |
| 35 | 16:00 | 144.28 | 16.3% |
| 36 | 16:30 | 153.70 | 15.7% |
| 37 | 17:00 | 162.55 | 16.9% |
| 38 | 17:30 | 178.92 | 16.6% |
| 39 | 18:00 | 199.44 | 16.2% |
| 40 | 18:30 | 206.26 | 14.3% |
| 41 | 19:00 | 225.00 | 13.9% |
| 42 | 19:30 | 226.11 | 12.8% |
| 43 | 20:00 | 205.00 | 13.0% |
| 44 | 20:30 | 204.01 | 11.6% |
| 45 | 21:00 | 202.20 | 12.8% |
| 46 | 21:30 | 201.00 | 13.7% |
| 47 | 22:00 | 197.61 | 12.6% |
| 48 | 22:30 | 185.00 | 14.4% |

</details>

