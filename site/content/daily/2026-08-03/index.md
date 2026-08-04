---
title: "I-SEM Daily Briefing — 3 August 2026"
date: 2026-08-03
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €158.28/MWh, peaking at €206.0/MWh at 19:30."
images: ["charts/2026-08-03/card-2026-08-03.png"]
draft: false
---

{{< statbar mean="€158.28" peak="€206.0" min="€127.56" spread="€78.44" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €158.28/MWh    |
| Median Price         | €154.49/MWh    |
| Std Dev              | €22.49/MWh    |
| Peak Price           | €206.0/MWh (19:30) |
| Min Price            | €127.56/MWh (13:00)   |
| Price Range          | €78.44/MWh   |
| Periods above €150   | 30 of 48 (62%) |
| Periods above €200   | 3 of 48 (6%) |
| Peak Avg (07–22)     | €159.38/MWh    |
| Off-peak Avg (22–07) | €156.46/MWh    |
| Peak/Off-Peak Spread | €2.92/MWh   |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-03/dam-2026-08-03.png)

**Std dev** €22.49/MWh  ·  **Median** €154.49/MWh  ·  **Periods above €150:** 30 of 48 (62%)

## Week in Context

![7-Day Price Comparison](/charts/2026-08-03/week-compare-2026-08-03.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-03/pdc-2026-08-03.png)

**Periods above €150:** 30 (62% of day)  ·  **Above €200:** 3 (6% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-03/spread-2026-08-03.png)

**Peak avg (07:00–22:00):** €159.38/MWh  ·  **Off-peak avg:** €156.46/MWh  ·  **Spread:** €2.92/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €128/MWh | 12:00 | 2 MWh | −€257 |
| **Discharge** | €203/MWh | 18:30 | 1.7 MWh (85% RTE) | +€344 |
| **Gross profit** | | | | **€88** |
| **Price spread** | €74/MWh | | | **ROI: 34.1%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-03/bess-2026-08-03.png)

<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->

## Commentary

Sunday gave the market its cleanest single-cycle day in over a week: one trough, one peak, no double humps. Price eased from €160 at 23:00 down to €144 by 03:30, ticked up briefly around the 05:00–06:30 morning ramp, then settled into a proper trough from 10:00 to 14:30 — €127.56 the low, held for a full hour either side of 13:00. From there it built steadily through the afternoon into a single evening peak, €206.00 at 19:30, before easing back to €174.40 by close.

That shape is what finally flips the peak/off-peak spread positive again — €2.92, the first positive reading since the 29th, after five straight days where the real extremes sat outside the daytime window. Std dev at €22.49 was the second-lowest of the week. With lighter Sunday demand and nothing pulling price sharply into either overnight bookend, this was about as close to a textbook I-SEM day as the week produced.

Storage landed squarely mid-pack: €88 gross, 34.1% ROI, charging at €128 and discharging at €203 for a €74 spread — unremarkable, much like the 27th. A calm end to a choppy week; worth seeing whether Monday brings the volatility back.


<details>
<summary>Half-hourly data — 2026-08-03</summary>

| Period | Time | Price (€/MWh) |
|--------|------|--------------|
| 1 | 23:00 | 160.09 |
| 2 | 23:30 | 155.57 |
| 3 | 00:00 | 152.09 |
| 4 | 00:30 | 150.39 |
| 5 | 01:00 | 147.45 |
| 6 | 01:30 | 148.14 |
| 7 | 02:00 | 146.26 |
| 8 | 02:30 | 144.68 |
| 9 | 03:00 | 144.39 |
| 10 | 03:30 | 144.00 |
| 11 | 04:00 | 150.52 |
| 12 | 04:30 | 150.77 |
| 13 | 05:00 | 162.85 |
| 14 | 05:30 | 164.00 |
| 15 | 06:00 | 170.00 |
| 16 | 06:30 | 171.20 |
| 17 | 07:00 | 161.95 |
| 18 | 07:30 | 164.00 |
| 19 | 08:00 | 152.85 |
| 20 | 08:30 | 153.96 |
| 21 | 09:00 | 155.02 |
| 22 | 09:30 | 157.09 |
| 23 | 10:00 | 139.50 |
| 24 | 10:30 | 134.07 |
| 25 | 11:00 | 132.99 |
| 26 | 11:30 | 130.38 |
| 27 | 12:00 | 130.20 |
| 28 | 12:30 | 128.46 |
| 29 | 13:00 | 127.56 |
| 30 | 13:30 | 127.56 |
| 31 | 14:00 | 130.38 |
| 32 | 14:30 | 132.31 |
| 33 | 15:00 | 139.16 |
| 34 | 15:30 | 141.00 |
| 35 | 16:00 | 156.00 |
| 36 | 16:30 | 156.00 |
| 37 | 17:00 | 169.33 |
| 38 | 17:30 | 176.67 |
| 39 | 18:00 | 192.70 |
| 40 | 18:30 | 198.18 |
| 41 | 19:00 | 205.53 |
| 42 | 19:30 | 206.00 |
| 43 | 20:00 | 200.69 |
| 44 | 20:30 | 198.01 |
| 45 | 21:00 | 192.09 |
| 46 | 21:30 | 191.62 |
| 47 | 22:00 | 179.45 |
| 48 | 22:30 | 174.40 |

</details>

