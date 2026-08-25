---
title: "I-SEM Daily Briefing — 17 August 2026"
date: 2026-08-17
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €192.2/MWh, peaking at €248.0/MWh at 09:30."
images: ["charts/2026-08-17/card-2026-08-17.png"]
draft: false
---

{{< statbar mean="€192.2" peak="€248.0" min="€162.12" spread="€85.88" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €192.2/MWh    |
| Median Price         | €189.95/MWh    |
| Std Dev              | €24.16/MWh    |
| Peak Price           | €248.0/MWh (09:30) |
| Min Price            | €162.12/MWh (15:30)   |
| Price Range          | €85.88/MWh   |
| Periods above €150   | 48 of 48 (100%) |
| Periods above €200   | 20 of 48 (42%) |
| Peak Avg (07–22)     | €200.55/MWh    |
| Off-peak Avg (22–07) | €178.27/MWh    |
| Peak/Off-Peak Spread | €22.28/MWh   |
| Wind % of Demand     | 23.7%          |
| Wind Range           | 8.2%–48.0% |
| Mean Demand          | 3920 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-17/dam-2026-08-17.png)

**Std dev** €24.16/MWh  ·  **Median** €189.95/MWh  ·  **Periods above €150:** 48 of 48 (100%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-17/price-wind-2026-08-17.png)

**Mean wind:** 23.7%  ·  **Range:** 8.2%–48.0%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-17/week-compare-2026-08-17.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-17/pdc-2026-08-17.png)

**Periods above €150:** 48 (100% of day)  ·  **Above €200:** 20 (42% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-17/spread-2026-08-17.png)

**Peak avg (07:00–22:00):** €200.55/MWh  ·  **Off-peak avg:** €178.27/MWh  ·  **Spread:** €22.28/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €163/MWh | 14:30 | 2 MWh | −€326 |
| **Discharge** | €236/MWh | 08:30 | 1.7 MWh (85% RTE) | +€402 |
| **Gross profit** | | | | **€76** |
| **Price spread** | €74/MWh | | | **ROI: 23.3%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-17/bess-2026-08-17.png)

## Commentary

Monday broke the shape as well as the pattern. Overnight wind was strong — 46–48% through the small hours — but it collapsed to single digits by 06:00–09:30, right as morning demand ramped up, and the price spiked into a €248.00 peak at 09:30. That's a morning squeeze, not the usual evening one, and it's why every single period cleared above €150 today (100%, the first time this week) and 42% cleared above €200. Wind recovered steadily through the afternoon and evening — back to 40%+ by 18:00 — which capped what would otherwise have been a second, evening peak: prices eased to a €162.12 trough at 15:30 and only climbed back to €215-ish by 19:00, well under the morning's €248.

Storage followed the shape, not the clock: charge into the afternoon trough near 14:30, discharge into the morning squeeze near 08:30 — the model picks the day's single cheapest and priciest windows independently, with no requirement that charging comes first, so an unusual double-peaked day like this one produces a discharge that clock-wise precedes the charge. €76 gross, 23.3% ROI — a modest return given how sharp the morning peak was, because the trough-to-peak spread it found was the afternoon-to-morning one, not the wider overnight-to-morning collapse that actually drove the day's price.


<details>
<summary>Half-hourly data — 2026-08-17</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 191.10 | 46.2% |
| 2 | 23:30 | 187.40 | 47.9% |
| 3 | 00:00 | 178.62 | 18.2% |
| 4 | 00:30 | 176.78 | 18.7% |
| 5 | 01:00 | 169.46 | 18.7% |
| 6 | 01:30 | 166.55 | 18.7% |
| 7 | 02:00 | 166.43 | 17.1% |
| 8 | 02:30 | 166.43 | 16.3% |
| 9 | 03:00 | 166.71 | 15.7% |
| 10 | 03:30 | 165.49 | 15.9% |
| 11 | 04:00 | 169.75 | 16.1% |
| 12 | 04:30 | 170.35 | 16.2% |
| 13 | 05:00 | 183.45 | 15.1% |
| 14 | 05:30 | 188.81 | 13.2% |
| 15 | 06:00 | 203.26 | 11.4% |
| 16 | 06:30 | 208.01 | 9.9% |
| 17 | 07:00 | 210.01 | 9.1% |
| 18 | 07:30 | 227.09 | 9.4% |
| 19 | 08:00 | 220.15 | 9.4% |
| 20 | 08:30 | 227.81 | 9.4% |
| 21 | 09:00 | 234.84 | 8.2% |
| 22 | 09:30 | 248.00 | 9.0% |
| 23 | 10:00 | 235.31 | 10.2% |
| 24 | 10:30 | 225.00 | 9.3% |
| 25 | 11:00 | 219.86 | 9.5% |
| 26 | 11:30 | 206.29 | 11.0% |
| 27 | 12:00 | 195.62 | 11.7% |
| 28 | 12:30 | 181.00 | 12.5% |
| 29 | 13:00 | 172.09 | 14.1% |
| 30 | 13:30 | 166.24 | 16.3% |
| 31 | 14:00 | 164.59 | 20.8% |
| 32 | 14:30 | 163.99 | 23.5% |
| 33 | 15:00 | 162.24 | 27.1% |
| 34 | 15:30 | 162.12 | 27.8% |
| 35 | 16:00 | 163.52 | 29.0% |
| 36 | 16:30 | 167.33 | 31.2% |
| 37 | 17:00 | 192.81 | 31.7% |
| 38 | 17:30 | 195.17 | 35.0% |
| 39 | 18:00 | 213.07 | 39.6% |
| 40 | 18:30 | 214.74 | 41.3% |
| 41 | 19:00 | 215.42 | 42.6% |
| 42 | 19:30 | 214.00 | 44.7% |
| 43 | 20:00 | 208.00 | 45.7% |
| 44 | 20:30 | 206.30 | 45.6% |
| 45 | 21:00 | 203.03 | 46.7% |
| 46 | 21:30 | 201.00 | 46.9% |
| 47 | 22:00 | 180.01 | 45.9% |
| 48 | 22:30 | 170.24 | 48.0% |

</details>

