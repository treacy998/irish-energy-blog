---
title: "I-SEM Daily Briefing — 31 July 2026"
date: 2026-07-31
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €166.9/MWh, peaking at €223.14/MWh at 23:00."
images: ["charts/2026-07-31/card-2026-07-31.png"]
draft: false
---

{{< statbar mean="€166.9" peak="€223.14" min="€124.63" spread="€98.51" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €166.9/MWh    |
| Median Price         | €164.69/MWh    |
| Std Dev              | €27.85/MWh    |
| Peak Price           | €223.14/MWh (23:00) |
| Min Price            | €124.63/MWh (14:30)   |
| Price Range          | €98.51/MWh   |
| Periods above €150   | 35 of 48 (73%) |
| Periods above €200   | 7 of 48 (15%) |
| Peak Avg (07–22)     | €161.32/MWh    |
| Off-peak Avg (22–07) | €176.21/MWh    |
| Peak/Off-Peak Spread | €-14.89/MWh   |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-07-31/dam-2026-07-31.png)

**Std dev** €27.85/MWh  ·  **Median** €164.69/MWh  ·  **Periods above €150:** 35 of 48 (73%)

## Week in Context

![7-Day Price Comparison](/charts/2026-07-31/week-compare-2026-07-31.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-07-31/pdc-2026-07-31.png)

**Periods above €150:** 35 (73% of day)  ·  **Above €200:** 7 (15% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-07-31/spread-2026-07-31.png)

**Peak avg (07:00–22:00):** €161.32/MWh  ·  **Off-peak avg:** €176.21/MWh  ·  **Spread:** €-14.89/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €126/MWh | 13:30 | 2 MWh | −€252 |
| **Discharge** | €212/MWh | 21:00 | 1.7 MWh (85% RTE) | +€360 |
| **Gross profit** | | | | **€108** |
| **Price spread** | €85/MWh | | | **ROI: 42.7%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-07-31/bess-2026-07-31.png)

<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->

## Commentary

Today flipped the usual script: the single highest price of the day, €223.14, landed at 23:00 — the very first half-hour on the clock — before sliding steadily through the small hours into a long, shallow trough across the early afternoon. By 14:30 price had fallen to €124.63, roughly half the overnight peak, before demand pulled it straight back up: €181.53 by 18:00, past €200 by 20:00, and a second high plateau — €206 to €223 — running from 20:00 clean through to the following midnight.

That gives the widest negative peak/off-peak spread of the week, €-14.89, with off-peak averaging €176.21 against €161.32 for the 07:00–22:00 window. It's a distribution with two tails and not much middle: 35 of 48 periods above €150, but only 7 above €200, all of them clustered at either edge of the day. Std dev came in at €27.85, close to the recent norm — this wasn't a volatile day so much as a lopsided one.

Storage still found its spread. Charging at €126 in the afternoon trough and discharging at €212 into the evening ramp cleared €108 gross at 42.7% ROI, right in line with yesterday's €116/47.7%. Two days running now with a genuine daytime low to work against — worth watching whether that becomes the week's new pattern.


<details>
<summary>Half-hourly data — 2026-07-31</summary>

| Period | Time | Price (€/MWh) |
|--------|------|--------------|
| 1 | 23:00 | 223.14 |
| 2 | 23:30 | 193.45 |
| 3 | 00:00 | 181.31 |
| 4 | 00:30 | 171.20 |
| 5 | 01:00 | 165.61 |
| 6 | 01:30 | 163.86 |
| 7 | 02:00 | 158.70 |
| 8 | 02:30 | 156.09 |
| 9 | 03:00 | 156.05 |
| 10 | 03:30 | 154.72 |
| 11 | 04:00 | 160.00 |
| 12 | 04:30 | 158.78 |
| 13 | 05:00 | 169.22 |
| 14 | 05:30 | 171.60 |
| 15 | 06:00 | 176.09 |
| 16 | 06:30 | 179.60 |
| 17 | 07:00 | 185.09 |
| 18 | 07:30 | 199.58 |
| 19 | 08:00 | 181.94 |
| 20 | 08:30 | 177.00 |
| 21 | 09:00 | 165.52 |
| 22 | 09:30 | 157.65 |
| 23 | 10:00 | 151.00 |
| 24 | 10:30 | 145.89 |
| 25 | 11:00 | 136.46 |
| 26 | 11:30 | 136.18 |
| 27 | 12:00 | 133.62 |
| 28 | 12:30 | 131.00 |
| 29 | 13:00 | 128.29 |
| 30 | 13:30 | 126.32 |
| 31 | 14:00 | 126.09 |
| 32 | 14:30 | 124.63 |
| 33 | 15:00 | 126.99 |
| 34 | 15:30 | 128.00 |
| 35 | 16:00 | 138.67 |
| 36 | 16:30 | 143.13 |
| 37 | 17:00 | 154.06 |
| 38 | 17:30 | 158.00 |
| 39 | 18:00 | 181.53 |
| 40 | 18:30 | 183.58 |
| 41 | 19:00 | 194.42 |
| 42 | 19:30 | 198.27 |
| 43 | 20:00 | 206.00 |
| 44 | 20:30 | 207.02 |
| 45 | 21:00 | 206.42 |
| 46 | 21:30 | 207.24 |
| 47 | 22:00 | 218.69 |
| 48 | 22:30 | 213.64 |

</details>

