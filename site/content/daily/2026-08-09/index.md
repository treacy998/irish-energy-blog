---
title: "I-SEM Daily Briefing — 9 August 2026"
date: 2026-08-09
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €151.57/MWh, peaking at €203.07/MWh at 21:30."
images: ["charts/2026-08-09/card-2026-08-09.png"]
draft: false
---

{{< statbar mean="€151.57" peak="€203.07" min="€115.4" spread="€87.67" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €151.57/MWh    |
| Median Price         | €150.48/MWh    |
| Std Dev              | €26.02/MWh    |
| Peak Price           | €203.07/MWh (21:30) |
| Min Price            | €115.4/MWh (11:30)   |
| Price Range          | €87.67/MWh   |
| Periods above €150   | 25 of 48 (52%) |
| Periods above €200   | 4 of 48 (8%) |
| Peak Avg (07–22)     | €148.77/MWh    |
| Off-peak Avg (22–07) | €156.23/MWh    |
| Peak/Off-Peak Spread | €-7.46/MWh   |
| Wind % of Demand     | 21.5%          |
| Wind Range           | 14.4%–33.9% |
| Mean Demand          | 3511 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-09/dam-2026-08-09.png)

**Std dev** €26.02/MWh  ·  **Median** €150.48/MWh  ·  **Periods above €150:** 25 of 48 (52%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-09/price-wind-2026-08-09.png)

**Mean wind:** 21.5%  ·  **Range:** 14.4%–33.9%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-09/week-compare-2026-08-09.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-09/pdc-2026-08-09.png)

**Periods above €150:** 25 (52% of day)  ·  **Above €200:** 4 (8% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-09/spread-2026-08-09.png)

**Peak avg (07:00–22:00):** €148.77/MWh  ·  **Off-peak avg:** €156.23/MWh  ·  **Spread:** €-7.46/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €115/MWh | 13:30 | 2 MWh | −€231 |
| **Discharge** | €202/MWh | 20:30 | 1.7 MWh (85% RTE) | +€343 |
| **Gross profit** | | | | **€113** |
| **Price spread** | €87/MWh | | | **ROI: 48.8%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-09/bess-2026-08-09.png)

<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->

## Commentary

Sunday reset back toward a single-cycle shape, much like the 3rd. Price drifted down from an overnight €150-ish band into a flat trough — pinned at exactly €115.40 for most of 11:30 to 15:00 — then built steadily through the afternoon into one clean evening peak, €203.07 at 21:30, with 4 of 48 periods clearing €200. Wind held a moderate, fairly stable 21.5% through the day, doing little to disturb the shape either way.

Peak/off-peak spread came in only slightly negative (–€7.46), close to flat, because the evening peak — while the week's second-highest — sits right at the edge of the 22:00 cutoff and doesn't fully offset an elevated off-peak average. Std dev of €26.02 puts this squarely mid-pack for the week.

Storage landed mid-table too: €113 gross off a €115 charge and €202 discharge, 48.8% ROI — almost a repeat of the 3rd's textbook Sunday, just with a firmer floor and a sharper peak. A quiet close to the weekend before Monday's usual step-up in demand.


<details>
<summary>Half-hourly data — 2026-08-09</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 174.02 | 14.4% |
| 2 | 23:30 | 158.99 | 14.8% |
| 3 | 00:00 | 157.99 | 18.0% |
| 4 | 00:30 | 151.09 | 17.9% |
| 5 | 01:00 | 156.82 | 17.5% |
| 6 | 01:30 | 153.58 | 18.4% |
| 7 | 02:00 | 165.00 | 17.6% |
| 8 | 02:30 | 153.00 | 17.4% |
| 9 | 03:00 | 150.93 | 18.6% |
| 10 | 03:30 | 145.12 | 20.3% |
| 11 | 04:00 | 148.11 | 20.8% |
| 12 | 04:30 | 144.84 | 21.6% |
| 13 | 05:00 | 143.30 | 21.4% |
| 14 | 05:30 | 142.00 | 20.5% |
| 15 | 06:00 | 142.69 | 20.0% |
| 16 | 06:30 | 143.83 | 19.3% |
| 17 | 07:00 | 133.61 | 18.2% |
| 18 | 07:30 | 147.33 | 18.2% |
| 19 | 08:00 | 159.30 | 17.3% |
| 20 | 08:30 | 164.59 | 19.0% |
| 21 | 09:00 | 154.53 | 20.6% |
| 22 | 09:30 | 150.03 | 17.6% |
| 23 | 10:00 | 140.44 | 18.4% |
| 24 | 10:30 | 128.74 | 20.0% |
| 25 | 11:00 | 126.16 | 21.6% |
| 26 | 11:30 | 115.40 | 21.9% |
| 27 | 12:00 | 115.40 | 22.6% |
| 28 | 12:30 | 115.40 | 22.5% |
| 29 | 13:00 | 125.92 | 22.6% |
| 30 | 13:30 | 115.40 | 24.3% |
| 31 | 14:00 | 115.40 | 25.0% |
| 32 | 14:30 | 115.40 | 25.4% |
| 33 | 15:00 | 115.40 | 23.9% |
| 34 | 15:30 | 117.31 | 26.4% |
| 35 | 16:00 | 126.39 | 26.8% |
| 36 | 16:30 | 133.86 | 28.0% |
| 37 | 17:00 | 156.90 | 32.0% |
| 38 | 17:30 | 165.00 | 32.9% |
| 39 | 18:00 | 172.01 | 33.9% |
| 40 | 18:30 | 172.79 | 32.8% |
| 41 | 19:00 | 187.37 | 28.9% |
| 42 | 19:30 | 188.43 | 24.7% |
| 43 | 20:00 | 197.12 | 21.4% |
| 44 | 20:30 | 202.75 | 19.6% |
| 45 | 21:00 | 201.76 | 18.8% |
| 46 | 21:30 | 203.07 | 17.0% |
| 47 | 22:00 | 200.47 | 15.0% |
| 48 | 22:30 | 180.36 | 14.7% |

</details>

