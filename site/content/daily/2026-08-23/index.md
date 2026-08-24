---
title: "I-SEM Daily Briefing — 23 August 2026"
date: 2026-08-23
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €177.19/MWh, peaking at €229.16/MWh at 21:00."
images: ["charts/2026-08-23/card-2026-08-23.png"]
draft: false
---

{{< statbar mean="€177.19" peak="€229.16" min="€146.2" spread="€82.96" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €177.19/MWh    |
| Median Price         | €167.16/MWh    |
| Std Dev              | €27.23/MWh    |
| Peak Price           | €229.16/MWh (21:00) |
| Min Price            | €146.2/MWh (10:30)   |
| Price Range          | €82.96/MWh   |
| Periods above €150   | 43 of 48 (90%) |
| Periods above €200   | 11 of 48 (23%) |
| Peak Avg (07–22)     | €177.47/MWh    |
| Off-peak Avg (22–07) | €176.73/MWh    |
| Peak/Off-Peak Spread | €0.74/MWh   |
| Wind % of Demand     | 3.1%          |
| Wind Range           | 0.1%–11.8% |
| Mean Demand          | 3537 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-23/dam-2026-08-23.png)

**Std dev** €27.23/MWh  ·  **Median** €167.16/MWh  ·  **Periods above €150:** 43 of 48 (90%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-23/price-wind-2026-08-23.png)

**Mean wind:** 3.1%  ·  **Range:** 0.1%–11.8%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-23/week-compare-2026-08-23.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-23/pdc-2026-08-23.png)

**Periods above €150:** 43 (90% of day)  ·  **Above €200:** 11 (23% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-23/spread-2026-08-23.png)

**Peak avg (07:00–22:00):** €177.47/MWh  ·  **Off-peak avg:** €176.73/MWh  ·  **Spread:** €0.74/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €148/MWh | 10:00 | 2 MWh | −€295 |
| **Discharge** | €228/MWh | 19:30 | 1.7 MWh (85% RTE) | +€387 |
| **Gross profit** | | | | **€92** |
| **Price spread** | €80/MWh | | | **ROI: 31.2%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-23/bess-2026-08-23.png)

<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->

## Commentary

Sunday pushed the wind drought to its most extreme point yet — 0.1% of demand at 09:00, essentially becalmed, staying in low single digits until a late recovery to near 12% by 23:00. Demand was Sunday-light, so the midday trough held at €146.20 (10:30), but with almost nothing coming from wind, both the evening peak (€229.16 at 21:00) and the tail of the previous night stayed high enough that the peak/off-peak spread compressed to almost nothing (€0.74) — there was no real overnight relief to speak of.

Storage kept its hot streak going: charged at 10:00 (€148), discharged at 19:30 (€228), for €92 gross and 31.2% ROI — the best return of the four days, closing out a weekend where calm air did a lot more for battery economics than for anyone's electricity bill.


<details>
<summary>Half-hourly data — 2026-08-23</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 212.99 | 11.8% |
| 2 | 23:30 | 199.26 | 11.7% |
| 3 | 00:00 | 193.31 | 4.3% |
| 4 | 00:30 | 176.13 | 4.6% |
| 5 | 01:00 | 175.40 | 4.2% |
| 6 | 01:30 | 170.80 | 3.5% |
| 7 | 02:00 | 178.00 | 2.8% |
| 8 | 02:30 | 172.00 | 2.5% |
| 9 | 03:00 | 167.51 | 2.4% |
| 10 | 03:30 | 162.53 | 2.2% |
| 11 | 04:00 | 158.91 | 1.7% |
| 12 | 04:30 | 158.91 | 1.5% |
| 13 | 05:00 | 157.39 | 1.5% |
| 14 | 05:30 | 157.39 | 1.1% |
| 15 | 06:00 | 158.90 | 0.6% |
| 16 | 06:30 | 159.90 | 0.5% |
| 17 | 07:00 | 164.70 | 0.3% |
| 18 | 07:30 | 166.04 | 0.3% |
| 19 | 08:00 | 168.40 | 0.2% |
| 20 | 08:30 | 166.81 | 0.2% |
| 21 | 09:00 | 156.57 | 0.1% |
| 22 | 09:30 | 148.97 | 0.4% |
| 23 | 10:00 | 147.01 | 0.8% |
| 24 | 10:30 | 146.20 | 1.2% |
| 25 | 11:00 | 148.38 | 1.5% |
| 26 | 11:30 | 148.50 | 1.4% |
| 27 | 12:00 | 152.63 | 1.5% |
| 28 | 12:30 | 152.01 | 1.3% |
| 29 | 13:00 | 155.40 | 1.1% |
| 30 | 13:30 | 151.07 | 1.0% |
| 31 | 14:00 | 152.59 | 1.1% |
| 32 | 14:30 | 152.00 | 0.8% |
| 33 | 15:00 | 159.00 | 1.0% |
| 34 | 15:30 | 161.00 | 1.1% |
| 35 | 16:00 | 175.00 | 1.6% |
| 36 | 16:30 | 178.22 | 1.7% |
| 37 | 17:00 | 181.12 | 1.8% |
| 38 | 17:30 | 196.51 | 2.2% |
| 39 | 18:00 | 215.00 | 2.5% |
| 40 | 18:30 | 223.20 | 3.4% |
| 41 | 19:00 | 223.00 | 3.9% |
| 42 | 19:30 | 226.14 | 4.6% |
| 43 | 20:00 | 229.04 | 5.8% |
| 44 | 20:30 | 226.66 | 7.7% |
| 45 | 21:00 | 229.16 | 9.8% |
| 46 | 21:30 | 223.83 | 10.8% |
| 47 | 22:00 | 220.78 | 10.9% |
| 48 | 22:30 | 201.00 | 11.3% |

</details>

