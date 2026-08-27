---
title: "I-SEM Daily Briefing — 4 August 2026"
date: 2026-08-04
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €159.85/MWh, peaking at €201.03/MWh at 09:00."
images: ["charts/2026-08-04/card-2026-08-04.png"]
draft: false
---

{{< statbar mean="€159.85" peak="€201.03" min="€129.44" spread="€71.59" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €159.85/MWh    |
| Median Price         | €156.43/MWh    |
| Std Dev              | €18.86/MWh    |
| Peak Price           | €201.03/MWh (09:00) |
| Min Price            | €129.44/MWh (14:30)   |
| Price Range          | €71.59/MWh   |
| Periods above €150   | 31 of 48 (65%) |
| Periods above €200   | 1 of 48 (2%) |
| Peak Avg (07–22)     | €161.72/MWh    |
| Off-peak Avg (22–07) | €156.73/MWh    |
| Peak/Off-Peak Spread | €4.99/MWh   |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-04/dam-2026-08-04.png)

**Std dev** €18.86/MWh  ·  **Median** €156.43/MWh  ·  **Periods above €150:** 31 of 48 (65%)

## Week in Context

![7-Day Price Comparison](/charts/2026-08-04/week-compare-2026-08-04.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-04/pdc-2026-08-04.png)

**Periods above €150:** 31 (65% of day)  ·  **Above €200:** 1 (2% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-04/spread-2026-08-04.png)

**Peak avg (07:00–22:00):** €161.72/MWh  ·  **Off-peak avg:** €156.73/MWh  ·  **Spread:** €4.99/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €131/MWh | 14:00 | 2 MWh | −€262 |
| **Discharge** | €183/MWh | 19:00 | 1.7 MWh (85% RTE) | +€311 |
| **Gross profit** | | | | **€49** |
| **Price spread** | €52/MWh | | | **ROI: 18.8%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

*Updated 2026-08-25: the BESS simulation previously allowed the discharge window to occur before the charge window ended, which is physically impossible for a battery. This day's figure was recalculated enforcing charge-before-discharge; gross profit corrected from €67 to €49.*

![BESS Dispatch](/charts/2026-08-04/bess-2026-08-04.png)

## Commentary

Tuesday's shape flipped the usual script: the day's high, €201.03, landed at 09:00, not in the evening. Price built steadily from a €146 overnight floor into a sharp commuter-hour ramp, then cracked €200 before 09:30 and spent the rest of the day unwinding — down to a €129.44 trough at 14:30, then a second, smaller climb into a 183-ish evening plateau (18:30–20:30) that never troubled the morning's peak.

That double-hump, morning-led profile is why std dev came in at €18.86 — the flattest day of the week so far. Both humps sit inside the 07:00–22:00 window, so the peak/off-peak spread barely registers at €4.99: nearly all the volatility is happening *within* the daytime block rather than between day and night, leaving nothing for a simple peak/off-peak split to capture.

Storage had a thin day of it — €49 gross, charging at €131 (14:00) and discharging into the €183 evening plateau — because the trough isn't cheap enough to build a real spread against a morning peak that peaked early and eased off well before the battery could reach it. A muted start to the week; worth watching whether Wednesday's wind forecast breaks the pattern.


<details>
<summary>Half-hourly data — 2026-08-04</summary>

| Period | Time | Price (€/MWh) |
|--------|------|--------------|
| 1 | 23:00 | 165.12 |
| 2 | 23:30 | 160.84 |
| 3 | 00:00 | 156.83 |
| 4 | 00:30 | 154.70 |
| 5 | 01:00 | 150.52 |
| 6 | 01:30 | 149.98 |
| 7 | 02:00 | 149.00 |
| 8 | 02:30 | 148.26 |
| 9 | 03:00 | 146.66 |
| 10 | 03:30 | 146.09 |
| 11 | 04:00 | 151.22 |
| 12 | 04:30 | 151.65 |
| 13 | 05:00 | 160.47 |
| 14 | 05:30 | 162.22 |
| 15 | 06:00 | 171.00 |
| 16 | 06:30 | 177.72 |
| 17 | 07:00 | 182.70 |
| 18 | 07:30 | 197.24 |
| 19 | 08:00 | 187.95 |
| 20 | 08:30 | 187.96 |
| 21 | 09:00 | 201.03 |
| 22 | 09:30 | 188.60 |
| 23 | 10:00 | 168.00 |
| 24 | 10:30 | 157.42 |
| 25 | 11:00 | 144.44 |
| 26 | 11:30 | 141.81 |
| 27 | 12:00 | 142.74 |
| 28 | 12:30 | 139.32 |
| 29 | 13:00 | 143.82 |
| 30 | 13:30 | 136.40 |
| 31 | 14:00 | 131.33 |
| 32 | 14:30 | 129.44 |
| 33 | 15:00 | 130.72 |
| 34 | 15:30 | 132.00 |
| 35 | 16:00 | 138.10 |
| 36 | 16:30 | 142.81 |
| 37 | 17:00 | 150.10 |
| 38 | 17:30 | 156.02 |
| 39 | 18:00 | 169.34 |
| 40 | 18:30 | 171.99 |
| 41 | 19:00 | 183.47 |
| 42 | 19:30 | 181.59 |
| 43 | 20:00 | 183.81 |
| 44 | 20:30 | 182.58 |
| 45 | 21:00 | 177.97 |
| 46 | 21:30 | 170.95 |
| 47 | 22:00 | 163.80 |
| 48 | 22:30 | 155.00 |

</details>

