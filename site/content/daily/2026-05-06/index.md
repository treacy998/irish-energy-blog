---
title: "I-SEM Daily Briefing — 6 May 2026"
date: 2026-05-06
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €185.49/MWh, peaking at €250.1/MWh at 21:00."
images: ["charts/2026-05-06/card-2026-05-06.png"]
draft: false
---

{{< statbar mean="€185.49" peak="€250.1" min="€144.0" spread="€106.1" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €185.49/MWh    |
| Median Price         | €172.77/MWh    |
| Std Dev              | €30.91/MWh    |
| Peak Price           | €250.1/MWh (21:00) |
| Min Price            | €144.0/MWh (04:30)   |
| Price Range          | €106.1/MWh   |
| Periods above €150   | 45 of 48 (94%) |
| Periods above €200   | 16 of 48 (33%) |
| Peak Avg (07–22)     | €199.42/MWh    |
| Off-peak Avg (22–07) | €162.27/MWh    |
| Peak/Off-Peak Spread | €37.15/MWh   |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-05-06/dam-2026-05-06.png)

**Std dev** €30.91/MWh  ·  **Median** €172.77/MWh  ·  **Periods above €150:** 45 of 48 (94%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-05-06/price-wind-2026-05-06.png)

## Week in Context

![7-Day Price Comparison](/charts/2026-05-06/week-compare-2026-05-06.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-05-06/pdc-2026-05-06.png)

**Periods above €150:** 45 (94% of day)  ·  **Above €200:** 16 (33% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-05-06/spread-2026-05-06.png)

**Peak avg (07:00–22:00):** €199.42/MWh  ·  **Off-peak avg:** €162.27/MWh  ·  **Spread:** €37.15/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €147/MWh | 03:30 | 2 MWh | −€294 |
| **Discharge** | €236/MWh | 20:30 | 1.7 MWh (85% RTE) | +€402 |
| **Gross profit** | | | | **€108** |
| **Price spread** | €89/MWh | | | **ROI: 36.5%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-05-06/bess-2026-05-06.png)

€108 gross, and better than the spread alone implies. Charged at €147 (03:30), discharged at €236 (20:30): €89 of captured spread. The dual-peak shape — €231 morning, €250 evening — gave two viable discharge windows. The evening was taken. Unlike Monday and Tuesday, both would have worked.

## Commentary

The wind drought peaked on Wednesday. Mean wind fell to 3.8% — a number so low it barely registers — and held there through the entire working day. Six hours of sub-1% wind during peak demand hours, gas marginal in every period.

Mean price hit €185.49/MWh, the week's highest. Two peaks cleared above €230 — a morning ramp (€231 at 07:30) and an evening peak (€250 at 21:00). The first day of the run to produce a proper dual-peak shape, with both windows genuinely expensive.

The comparison that tells the week's story so far is Monday to Wednesday. Bank holiday Monday, 13% wind, suppressed demand: €152 mean. Working Wednesday, 3.8% wind, full commercial load: €185 mean. €33 of difference, almost entirely attributable to losing nine wind percentage points. That's as close to a marginal cost of wind as a single-day comparison will give you.


<details>
<summary>Half-hourly data — 2026-05-06</summary>

| Period | Time | Price (€/MWh) |
|--------|------|--------------|
| 1 | 23:00 | 167.85 |
| 2 | 23:30 | 152.00 |
| 3 | 00:00 | 171.00 |
| 4 | 00:30 | 163.91 |
| 5 | 01:00 | 158.36 |
| 6 | 01:30 | 151.80 |
| 7 | 02:00 | 151.06 |
| 8 | 02:30 | 150.59 |
| 9 | 03:00 | 150.34 |
| 10 | 03:30 | 150.34 |
| 11 | 04:00 | 147.20 |
| 12 | 04:30 | 144.00 |
| 13 | 05:00 | 147.12 |
| 14 | 05:30 | 159.00 |
| 15 | 06:00 | 151.12 |
| 16 | 06:30 | 182.56 |
| 17 | 07:00 | 216.01 |
| 18 | 07:30 | 231.00 |
| 19 | 08:00 | 229.13 |
| 20 | 08:30 | 217.03 |
| 21 | 09:00 | 229.24 |
| 22 | 09:30 | 201.00 |
| 23 | 10:00 | 188.59 |
| 24 | 10:30 | 168.78 |
| 25 | 11:00 | 188.52 |
| 26 | 11:30 | 177.84 |
| 27 | 12:00 | 170.00 |
| 28 | 12:30 | 167.85 |
| 29 | 13:00 | 170.10 |
| 30 | 13:30 | 171.79 |
| 31 | 14:00 | 166.00 |
| 32 | 14:30 | 164.26 |
| 33 | 15:00 | 159.59 |
| 34 | 15:30 | 167.85 |
| 35 | 16:00 | 173.76 |
| 36 | 16:30 | 193.20 |
| 37 | 17:00 | 195.00 |
| 38 | 17:30 | 218.00 |
| 39 | 18:00 | 217.02 |
| 40 | 18:30 | 222.25 |
| 41 | 19:00 | 217.03 |
| 42 | 19:30 | 217.03 |
| 43 | 20:00 | 228.12 |
| 44 | 20:30 | 226.09 |
| 45 | 21:00 | 250.10 |
| 46 | 21:30 | 240.40 |
| 47 | 22:00 | 229.00 |
| 48 | 22:30 | 193.70 |

</details>

