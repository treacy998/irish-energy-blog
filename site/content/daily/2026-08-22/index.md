---
title: "I-SEM Daily Briefing — 22 August 2026"
date: 2026-08-22
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €178.45/MWh, peaking at €240.0/MWh at 19:00."
images: ["charts/2026-08-22/card-2026-08-22.png"]
draft: false
---

{{< statbar mean="€178.45" peak="€240.0" min="€146.88" spread="€93.12" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €178.45/MWh    |
| Median Price         | €161.66/MWh    |
| Std Dev              | €29.57/MWh    |
| Peak Price           | €240.0/MWh (19:00) |
| Min Price            | €146.88/MWh (09:30)   |
| Price Range          | €93.12/MWh   |
| Periods above €150   | 47 of 48 (98%) |
| Periods above €200   | 10 of 48 (21%) |
| Peak Avg (07–22)     | €180.81/MWh    |
| Off-peak Avg (22–07) | €174.51/MWh    |
| Peak/Off-Peak Spread | €6.3/MWh   |
| Wind % of Demand     | 8.2%          |
| Wind Range           | 3.6%–19.3% |
| Mean Demand          | 3636 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-22/dam-2026-08-22.png)

**Std dev** €29.57/MWh  ·  **Median** €161.66/MWh  ·  **Periods above €150:** 47 of 48 (98%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-22/price-wind-2026-08-22.png)

**Mean wind:** 8.2%  ·  **Range:** 3.6%–19.3%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-22/week-compare-2026-08-22.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-22/pdc-2026-08-22.png)

**Periods above €150:** 47 (98% of day)  ·  **Above €200:** 10 (21% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-22/spread-2026-08-22.png)

**Peak avg (07:00–22:00):** €180.81/MWh  ·  **Off-peak avg:** €174.51/MWh  ·  **Spread:** €6.3/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €155/MWh | 08:00 | 2 MWh | −€309 |
| **Discharge** | €235/MWh | 18:30 | 1.7 MWh (85% RTE) | +€399 |
| **Gross profit** | | | | **€90** |
| **Price spread** | €80/MWh | | | **ROI: 29.0%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-22/bess-2026-08-22.png)

## Commentary

Saturday's wind fell off a cliff — from around 19% at midnight down to under 5% by 08:30, and it never really recovered, bottoming at 3.6% right at 20:00. Weekend demand kept the midday trough shallow regardless (€146.88 at 09:30, still low-wind territory), but by evening the no-wind, low-relief combination pushed price into a sharp spike: €240.00 at 19:00, the single highest print of the run, and the widest spread of the four days at €29.57 std dev.

Storage made the most of it — charged at 08:00 for €155 right as wind was collapsing, discharged at 18:30 for €235 just ahead of the evening peak, for €90 gross and a 29.0% ROI, the best of the week so far. Low wind is reliably good for storage economics, and Saturday had about as little of it as the week produced.


<details>
<summary>Half-hourly data — 2026-08-22</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 190.18 | 4.1% |
| 2 | 23:30 | 182.02 | 4.3% |
| 3 | 00:00 | 179.07 | 18.9% |
| 4 | 00:30 | 176.03 | 19.3% |
| 5 | 01:00 | 171.00 | 19.0% |
| 6 | 01:30 | 167.27 | 19.1% |
| 7 | 02:00 | 168.00 | 16.9% |
| 8 | 02:30 | 166.70 | 17.2% |
| 9 | 03:00 | 161.41 | 16.8% |
| 10 | 03:30 | 159.00 | 16.7% |
| 11 | 04:00 | 157.93 | 16.4% |
| 12 | 04:30 | 157.60 | 15.0% |
| 13 | 05:00 | 158.41 | 12.7% |
| 14 | 05:30 | 160.34 | 11.4% |
| 15 | 06:00 | 159.82 | 10.8% |
| 16 | 06:30 | 164.00 | 10.6% |
| 17 | 07:00 | 158.35 | 9.1% |
| 18 | 07:30 | 172.82 | 7.7% |
| 19 | 08:00 | 158.00 | 6.1% |
| 20 | 08:30 | 161.90 | 4.3% |
| 21 | 09:00 | 152.00 | 4.0% |
| 22 | 09:30 | 146.88 | 5.0% |
| 23 | 10:00 | 161.35 | 5.9% |
| 24 | 10:30 | 161.35 | 6.0% |
| 25 | 11:00 | 161.33 | 5.2% |
| 26 | 11:30 | 161.33 | 5.0% |
| 27 | 12:00 | 161.35 | 5.4% |
| 28 | 12:30 | 161.33 | 5.8% |
| 29 | 13:00 | 161.33 | 6.0% |
| 30 | 13:30 | 157.84 | 5.6% |
| 31 | 14:00 | 158.75 | 6.2% |
| 32 | 14:30 | 155.00 | 5.4% |
| 33 | 15:00 | 158.75 | 5.2% |
| 34 | 15:30 | 158.75 | 5.2% |
| 35 | 16:00 | 151.07 | 5.4% |
| 36 | 16:30 | 164.11 | 5.0% |
| 37 | 17:00 | 179.65 | 4.9% |
| 38 | 17:30 | 199.37 | 5.3% |
| 39 | 18:00 | 225.00 | 4.5% |
| 40 | 18:30 | 231.18 | 4.1% |
| 41 | 19:00 | 240.00 | 3.7% |
| 42 | 19:30 | 236.86 | 3.7% |
| 43 | 20:00 | 231.17 | 3.6% |
| 44 | 20:30 | 231.17 | 4.1% |
| 45 | 21:00 | 235.00 | 4.4% |
| 46 | 21:30 | 231.18 | 4.1% |
| 47 | 22:00 | 236.00 | 4.1% |
| 48 | 22:30 | 226.44 | 4.1% |

</details>

