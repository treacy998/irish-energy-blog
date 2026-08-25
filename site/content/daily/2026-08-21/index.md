---
title: "I-SEM Daily Briefing — 21 August 2026"
date: 2026-08-21
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €175.41/MWh, peaking at €213.08/MWh at 21:00."
images: ["charts/2026-08-21/card-2026-08-21.png"]
draft: false
---

{{< statbar mean="€175.41" peak="€213.08" min="€152.73" spread="€60.35" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €175.41/MWh    |
| Median Price         | €168.64/MWh    |
| Std Dev              | €20.95/MWh    |
| Peak Price           | €213.08/MWh (21:00) |
| Min Price            | €152.73/MWh (16:00)   |
| Price Range          | €60.35/MWh   |
| Periods above €150   | 48 of 48 (100%) |
| Periods above €200   | 11 of 48 (23%) |
| Peak Avg (07–22)     | €176.9/MWh    |
| Off-peak Avg (22–07) | €172.93/MWh    |
| Peak/Off-Peak Spread | €3.97/MWh   |
| Wind % of Demand     | 21.4%          |
| Wind Range           | 12.4%–27.9% |
| Mean Demand          | 3830 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-21/dam-2026-08-21.png)

**Std dev** €20.95/MWh  ·  **Median** €168.64/MWh  ·  **Periods above €150:** 48 of 48 (100%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-21/price-wind-2026-08-21.png)

**Mean wind:** 21.4%  ·  **Range:** 12.4%–27.9%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-21/week-compare-2026-08-21.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-21/pdc-2026-08-21.png)

**Periods above €150:** 48 (100% of day)  ·  **Above €200:** 11 (23% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-21/spread-2026-08-21.png)

**Peak avg (07:00–22:00):** €176.9/MWh  ·  **Off-peak avg:** €172.93/MWh  ·  **Spread:** €3.97/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €154/MWh | 11:30 | 2 MWh | −€308 |
| **Discharge** | €210/MWh | 20:00 | 1.7 MWh (85% RTE) | +€357 |
| **Gross profit** | | | | **€49** |
| **Price spread** | €56/MWh | | | **ROI: 15.9%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-21/bess-2026-08-21.png)

## Commentary

Friday's low point was a genuine morning squeeze: wind fell from 17.8% to 12.4% between 07:00 and 08:30, and price spiked to €205.04 right in the middle of it — the day's second-highest reading, beaten only by the evening. Wind recovered steadily through the afternoon, touching a 27.9% high at 17:00, and held above 20% for the rest of the evening — but that didn't stop price climbing to a €213.08 peak at 21:00 anyway. Demand was doing the driving this time, not wind: every single half-hour period cleared €150 today, the tightest floor of the run, with a €152.73 minimum.

Storage charged at 11:30 (€154) and discharged at 20:00 (€210) — a fine trade, but the weakest return of the week at €49 gross, 15.9% ROI. With wind sitting above 20% for most of the afternoon and evening, there wasn't much of a trough-to-peak spread left for the battery to work with.


<details>
<summary>Half-hourly data — 2026-08-21</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 179.00 | 19.9% |
| 2 | 23:30 | 174.77 | 20.4% |
| 3 | 00:00 | 169.01 | 26.0% |
| 4 | 00:30 | 167.09 | 24.8% |
| 5 | 01:00 | 160.85 | 23.7% |
| 6 | 01:30 | 159.48 | 22.8% |
| 7 | 02:00 | 159.00 | 22.5% |
| 8 | 02:30 | 158.83 | 22.4% |
| 9 | 03:00 | 158.05 | 22.1% |
| 10 | 03:30 | 156.19 | 22.3% |
| 11 | 04:00 | 161.84 | 22.0% |
| 12 | 04:30 | 163.18 | 22.3% |
| 13 | 05:00 | 180.18 | 21.2% |
| 14 | 05:30 | 182.30 | 20.4% |
| 15 | 06:00 | 191.16 | 20.6% |
| 16 | 06:30 | 196.60 | 20.0% |
| 17 | 07:00 | 201.00 | 17.8% |
| 18 | 07:30 | 205.04 | 16.3% |
| 19 | 08:00 | 201.65 | 13.3% |
| 20 | 08:30 | 197.32 | 12.4% |
| 21 | 09:00 | 176.36 | 13.9% |
| 22 | 09:30 | 168.28 | 15.5% |
| 23 | 10:00 | 156.01 | 18.9% |
| 24 | 10:30 | 156.44 | 19.1% |
| 25 | 11:00 | 154.18 | 20.1% |
| 26 | 11:30 | 153.00 | 21.4% |
| 27 | 12:00 | 154.75 | 22.3% |
| 28 | 12:30 | 154.01 | 21.9% |
| 29 | 13:00 | 154.01 | 22.9% |
| 30 | 13:30 | 153.30 | 22.8% |
| 31 | 14:00 | 154.50 | 23.0% |
| 32 | 14:30 | 154.01 | 22.6% |
| 33 | 15:00 | 154.44 | 23.6% |
| 34 | 15:30 | 154.77 | 25.5% |
| 35 | 16:00 | 152.73 | 25.1% |
| 36 | 16:30 | 156.73 | 24.8% |
| 37 | 17:00 | 169.98 | 27.9% |
| 38 | 17:30 | 175.00 | 25.7% |
| 39 | 18:00 | 195.82 | 24.5% |
| 40 | 18:30 | 201.48 | 25.8% |
| 41 | 19:00 | 206.04 | 25.6% |
| 42 | 19:30 | 206.74 | 22.9% |
| 43 | 20:00 | 209.36 | 21.5% |
| 44 | 20:30 | 209.36 | 20.8% |
| 45 | 21:00 | 213.08 | 19.8% |
| 46 | 21:30 | 207.69 | 18.9% |
| 47 | 22:00 | 201.28 | 17.1% |
| 48 | 22:30 | 194.01 | 18.2% |

</details>

