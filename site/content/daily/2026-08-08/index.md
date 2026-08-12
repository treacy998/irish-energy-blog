---
title: "I-SEM Daily Briefing — 8 August 2026"
date: 2026-08-08
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €129.2/MWh, peaking at €184.99/MWh at 23:00."
images: ["charts/2026-08-08/card-2026-08-08.png"]
draft: false
---

{{< statbar mean="€129.2" peak="€184.99" min="€47.51" spread="€137.48" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €129.2/MWh    |
| Median Price         | €147.11/MWh    |
| Std Dev              | €43.86/MWh    |
| Peak Price           | €184.99/MWh (23:00) |
| Min Price            | €47.51/MWh (15:00)   |
| Price Range          | €137.48/MWh   |
| Periods above €150   | 19 of 48 (40%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €113.04/MWh    |
| Off-peak Avg (22–07) | €156.14/MWh    |
| Peak/Off-Peak Spread | €-43.1/MWh   |
| Wind % of Demand     | 21.0%          |
| Wind Range           | 13.8%–28.6% |
| Mean Demand          | 3529 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-08/dam-2026-08-08.png)

**Std dev** €43.86/MWh  ·  **Median** €147.11/MWh  ·  **Periods above €150:** 19 of 48 (40%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-08/price-wind-2026-08-08.png)

**Mean wind:** 21.0%  ·  **Range:** 13.8%–28.6%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-08/week-compare-2026-08-08.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-08/pdc-2026-08-08.png)

**Periods above €150:** 19 (40% of day)  ·  **Above €200:** 0 (0% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-08/spread-2026-08-08.png)

**Peak avg (07:00–22:00):** €113.04/MWh  ·  **Off-peak avg:** €156.14/MWh  ·  **Spread:** €-43.1/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €49/MWh | 13:30 | 2 MWh | −€99 |
| **Discharge** | €177/MWh | 20:00 | 1.7 MWh (85% RTE) | +€301 |
| **Gross profit** | | | | **€202** |
| **Price spread** | €128/MWh | | | **ROI: 204.8%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-08/bess-2026-08-08.png)

<!-- BESS Commentary: Was today a good day for storage? What drove the spread? -->

## Commentary

Saturday's lower weekend demand (mean 3,529 MW) combined with decent wind (21.0%, up to 28.6%) to carve out a long, deep midday trough — price sank under €100 by 10:00 and stayed there for six hours, bottoming at €47.51 at 15:00. The day opened high, tailing off Friday evening's peak at €184.99, then fell almost the whole morning before the familiar evening ramp rebuilt it back to the high €170s by 20:30.

That long, cheap daytime window is exactly what dragged the peak/off-peak spread deep negative, to –€43.10 — worse even than Wednesday's wind-driven inversion, but for a different reason: this was weekend demand doing the work, not a wind glut. Wind here was only moderate; it was the missing commercial/industrial load that let it fall this far.

Storage had its second-best day of the week for it: charge at €49 (near the floor), discharge at €177, €202 gross, a 204.8% ROI. A weekend trough this wide and this cheap is a gift for anyone with a battery — the lesson from Wednesday holding again: it's the shape, not the headline mean, that pays.


<details>
<summary>Half-hourly data — 2026-08-08</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 184.99 | 16.8% |
| 2 | 23:30 | 171.46 | 16.7% |
| 3 | 00:00 | 169.24 | 13.8% |
| 4 | 00:30 | 161.55 | 13.8% |
| 5 | 01:00 | 156.53 | 14.5% |
| 6 | 01:30 | 154.04 | 14.2% |
| 7 | 02:00 | 152.73 | 14.1% |
| 8 | 02:30 | 150.04 | 13.9% |
| 9 | 03:00 | 148.10 | 15.9% |
| 10 | 03:30 | 145.07 | 17.6% |
| 11 | 04:00 | 145.00 | 19.7% |
| 12 | 04:30 | 144.90 | 22.7% |
| 13 | 05:00 | 148.15 | 24.6% |
| 14 | 05:30 | 148.04 | 26.8% |
| 15 | 06:00 | 150.38 | 28.5% |
| 16 | 06:30 | 148.46 | 28.6% |
| 17 | 07:00 | 146.22 | 27.5% |
| 18 | 07:30 | 148.00 | 26.5% |
| 19 | 08:00 | 134.54 | 25.8% |
| 20 | 08:30 | 128.41 | 26.2% |
| 21 | 09:00 | 132.49 | 25.3% |
| 22 | 09:30 | 120.42 | 28.1% |
| 23 | 10:00 | 100.33 | 26.0% |
| 24 | 10:30 | 75.00 | 24.9% |
| 25 | 11:00 | 67.70 | 24.1% |
| 26 | 11:30 | 50.40 | 24.1% |
| 27 | 12:00 | 72.36 | 24.9% |
| 28 | 12:30 | 68.33 | 24.8% |
| 29 | 13:00 | 69.36 | 24.3% |
| 30 | 13:30 | 50.45 | 21.4% |
| 31 | 14:00 | 50.04 | 18.9% |
| 32 | 14:30 | 49.59 | 16.9% |
| 33 | 15:00 | 47.51 | 17.1% |
| 34 | 15:30 | 58.72 | 17.6% |
| 35 | 16:00 | 82.53 | 18.7% |
| 36 | 16:30 | 87.55 | 21.6% |
| 37 | 17:00 | 129.25 | 25.9% |
| 38 | 17:30 | 137.00 | 26.7% |
| 39 | 18:00 | 160.90 | 23.3% |
| 40 | 18:30 | 165.17 | 20.2% |
| 41 | 19:00 | 175.09 | 18.4% |
| 42 | 19:30 | 175.36 | 18.8% |
| 43 | 20:00 | 176.00 | 18.1% |
| 44 | 20:30 | 178.04 | 17.3% |
| 45 | 21:00 | 175.80 | 16.9% |
| 46 | 21:30 | 178.67 | 17.8% |
| 47 | 22:00 | 166.81 | 18.3% |
| 48 | 22:30 | 165.00 | 17.4% |

</details>

