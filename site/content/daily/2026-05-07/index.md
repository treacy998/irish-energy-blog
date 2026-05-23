---
title: "I-SEM Daily Briefing — 7 May 2026"
date: 2026-05-07
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €174.4/MWh, peaking at €241.77/MWh at 23:00."
draft: false
---

{{< statbar mean="€174.4" peak="€241.77" min="€119.0" spread="€122.77" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €174.4/MWh    |
| Median Price         | €173.5/MWh    |
| Std Dev              | €37.85/MWh    |
| Peak Price           | €241.77/MWh (23:00) |
| Min Price            | €119.0/MWh (11:30)   |
| Price Range          | €122.77/MWh   |
| Periods above €150   | 33 of 48 (69%) |
| Periods above €200   | 15 of 48 (31%) |
| Peak Avg (07–22)     | €169.3/MWh    |
| Off-peak Avg (22–07) | €182.9/MWh    |
| Peak/Off-Peak Spread | €-13.6/MWh   |
| Wind % of Demand     | 11.0%          |
| Wind Range           | 2.6%–22.6% |
| Mean Demand          | 3875 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-05-07/dam-2026-05-07.png)

**Std dev** €37.85/MWh  ·  **Median** €173.5/MWh  ·  **Periods above €150:** 33 of 48 (69%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-05-07/price-wind-2026-05-07.png)

**Mean wind:** 11.0%  ·  **Range:** 2.6%–22.6%

## Week in Context

![7-Day Price Comparison](/charts/2026-05-07/week-compare-2026-05-07.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-05-07/pdc-2026-05-07.png)

**Periods above €150:** 33 (69% of day)  ·  **Above €200:** 15 (31% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-05-07/spread-2026-05-07.png)

**Peak avg (07:00–22:00):** €169.3/MWh  ·  **Off-peak avg:** €182.9/MWh  ·  **Spread:** €-13.6/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €123/MWh | 11:30 | 2 MWh | −€245 |
| **Discharge** | €226/MWh | 07:00 | 1.7 MWh (85% RTE) | +€385 |
| **Gross profit** | | | | **€139** |
| **Price spread** | €104/MWh | | | **ROI: 56.8%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-05-07/bess-2026-05-07.png)

€139 gross — the week's best, and wind built it. Charged at €123 (11:30) and discharged at €226 (07:00), capturing €104 of spread. The charge price was the cheapest of the week; the midday trough that built it was 22.6% wind at €119. A real operator realises 70–85% of the model spread — but even at the low end, this is the week's best day by a distance.

## Commentary

Wind cannibalisation, compressed into six hours. Wind climbed from 8.6% at 09:00 to 22.6% by 15:00 — a 14-point surge — and price fell in lockstep: €204 → €180 → €152 → €137 → €123 → €119. Seven consecutive half-hours below €130, with the daily minimum (€119) at 11:30. The inverse correlation is tight enough to put a number on: roughly €6 of price suppression per 1% rise in wind penetration through that window.

The consequence for wind farms is the cannibalisation problem in its most legible form. Wind generated heavily in the cheap midday window (16–23% of demand during €119–150 periods) and barely at all through the expensive overnight and morning-peak periods (2–5% during €189–242). Capture price today probably sat around €130–145 against a €174 time-weighted mean — meaningful volume, realised well below the day's average price.

The peak/off-peak spread went negative: peak hours averaged €169.30, off-peak averaged €182.90. Off-peak more expensive than peak. The midday trough sat inside peak hours; overnight retained Wednesday's wind-drought tail. Any commercial product banded on conventional peak/off-peak windows misfires on a day like this. Storage, on the other hand, made its best money of the week. €139 gross from a €104 spread — the shape that cannibalises wind revenue is exactly the shape batteries are built for.


<details>
<summary>Half-hourly data — 2026-05-07</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 241.77 | 3.9% |
| 2 | 23:30 | 223.60 | 3.0% |
| 3 | 00:00 | 209.74 | 3.4% |
| 4 | 00:30 | 188.88 | 2.6% |
| 5 | 01:00 | 175.00 | 3.1% |
| 6 | 01:30 | 166.29 | 3.7% |
| 7 | 02:00 | 192.11 | 4.3% |
| 8 | 02:30 | 186.68 | 4.6% |
| 9 | 03:00 | 168.15 | 5.3% |
| 10 | 03:30 | 160.36 | 5.6% |
| 11 | 04:00 | 150.80 | 7.2% |
| 12 | 04:30 | 150.00 | 8.4% |
| 13 | 05:00 | 149.49 | 8.5% |
| 14 | 05:30 | 152.96 | 8.2% |
| 15 | 06:00 | 172.00 | 8.5% |
| 16 | 06:30 | 188.63 | 8.2% |
| 17 | 07:00 | 223.59 | 7.7% |
| 18 | 07:30 | 234.08 | 6.9% |
| 19 | 08:00 | 225.86 | 7.3% |
| 20 | 08:30 | 221.56 | 6.6% |
| 21 | 09:00 | 204.50 | 8.6% |
| 22 | 09:30 | 180.00 | 11.0% |
| 23 | 10:00 | 152.15 | 13.2% |
| 24 | 10:30 | 137.03 | 15.6% |
| 25 | 11:00 | 123.50 | 16.3% |
| 26 | 11:30 | 119.00 | 19.3% |
| 27 | 12:00 | 126.00 | 20.1% |
| 28 | 12:30 | 122.62 | 19.1% |
| 29 | 13:00 | 123.00 | 18.7% |
| 30 | 13:30 | 121.91 | 18.3% |
| 31 | 14:00 | 124.00 | 20.2% |
| 32 | 14:30 | 122.43 | 20.0% |
| 33 | 15:00 | 125.00 | 22.6% |
| 34 | 15:30 | 128.00 | 20.8% |
| 35 | 16:00 | 136.00 | 22.3% |
| 36 | 16:30 | 149.11 | 20.0% |
| 37 | 17:00 | 151.00 | 18.9% |
| 38 | 17:30 | 166.00 | 16.5% |
| 39 | 18:00 | 179.00 | 14.5% |
| 40 | 18:30 | 187.20 | 13.4% |
| 41 | 19:00 | 203.80 | 11.1% |
| 42 | 19:30 | 215.00 | 9.4% |
| 43 | 20:00 | 215.00 | 8.9% |
| 44 | 20:30 | 219.55 | 7.9% |
| 45 | 21:00 | 223.56 | 7.0% |
| 46 | 21:30 | 219.55 | 6.0% |
| 47 | 22:00 | 220.00 | 6.1% |
| 48 | 22:30 | 195.65 | 4.9% |

</details>

