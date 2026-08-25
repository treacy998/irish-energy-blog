---
title: "I-SEM Daily Briefing — 28 July 2026"
date: 2026-07-28
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €148.32/MWh, peaking at €205.0/MWh at 21:30."
images: ["charts/2026-07-28/card-2026-07-28.png"]
draft: false
---

{{< statbar mean="€148.32" peak="€205.0" min="€106.95" spread="€98.05" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €148.32/MWh    |
| Median Price         | €147.06/MWh    |
| Std Dev              | €28.93/MWh    |
| Peak Price           | €205.0/MWh (21:30) |
| Min Price            | €106.95/MWh (13:30)   |
| Price Range          | €98.05/MWh   |
| Periods above €150   | 18 of 48 (38%) |
| Periods above €200   | 4 of 48 (8%) |
| Peak Avg (07–22)     | €145.8/MWh    |
| Off-peak Avg (22–07) | €152.52/MWh    |
| Peak/Off-Peak Spread | €-6.72/MWh   |
| Wind % of Demand     | 38.3%          |
| Wind Range           | 19.9%–54.2% |
| Mean Demand          | 3877 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-07-28/dam-2026-07-28.png)

**Std dev** €28.93/MWh  ·  **Median** €147.06/MWh  ·  **Periods above €150:** 18 of 48 (38%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-07-28/price-wind-2026-07-28.png)

**Mean wind:** 38.3%  ·  **Range:** 19.9%–54.2%

## Week in Context

![7-Day Price Comparison](/charts/2026-07-28/week-compare-2026-07-28.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-07-28/pdc-2026-07-28.png)

**Periods above €150:** 18 (38% of day)  ·  **Above €200:** 4 (8% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-07-28/spread-2026-07-28.png)

**Peak avg (07:00–22:00):** €145.8/MWh  ·  **Off-peak avg:** €152.52/MWh  ·  **Spread:** €-6.72/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €108/MWh | 12:30 | 2 MWh | −€216 |
| **Discharge** | €203/MWh | 20:00 | 1.7 MWh (85% RTE) | +€345 |
| **Gross profit** | | | | **€129** |
| **Price spread** | €95/MWh | | | **ROI: 60.0%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-07-28/bess-2026-07-28.png)

## Commentary

Wind climbed back to 38.3%, its highest since Sunday, and the peak/off-peak spread slipped just barely negative again at -€6.72 — essentially flat between day and night rather than sharply inverted. The overnight hours actually carried the higher average this time, as wind above 40% between 01:00 and 06:00 kept a lid on prices while the daytime trough (€106.95 at 13:30) came from a more modest wind level in the mid-30s.

The evening told a different story. Wind fell away from 36% at 18:00 to under 22% by 21:30, and price climbed steadily from €175 to a €205.0 close — a clean, gradual ramp rather than a sharp spike, which tracks with wind's gradual decline rather than a sudden drop-off. No single dramatic swing today, just a market drifting with the wind curve all day long.

Storage took €129 gross on a 60% ROI, comfortably mid-pack for the week — a moderate spread from a moderate, high-but-not-extreme wind day.


<details>
<summary>Half-hourly data — 2026-07-28</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 172.05 | 21.1% |
| 2 | 23:30 | 165.99 | 23.2% |
| 3 | 00:00 | 155.92 | 37.4% |
| 4 | 00:30 | 153.20 | 38.6% |
| 5 | 01:00 | 148.00 | 41.6% |
| 6 | 01:30 | 148.93 | 42.9% |
| 7 | 02:00 | 145.61 | 43.2% |
| 8 | 02:30 | 143.08 | 45.8% |
| 9 | 03:00 | 141.99 | 48.5% |
| 10 | 03:30 | 137.61 | 50.1% |
| 11 | 04:00 | 137.77 | 52.4% |
| 12 | 04:30 | 135.72 | 53.9% |
| 13 | 05:00 | 142.04 | 54.2% |
| 14 | 05:30 | 142.66 | 53.7% |
| 15 | 06:00 | 148.59 | 52.9% |
| 16 | 06:30 | 155.38 | 48.7% |
| 17 | 07:00 | 154.17 | 45.1% |
| 18 | 07:30 | 155.61 | 41.3% |
| 19 | 08:00 | 149.94 | 39.8% |
| 20 | 08:30 | 149.60 | 40.0% |
| 21 | 09:00 | 148.59 | 39.2% |
| 22 | 09:30 | 146.12 | 39.4% |
| 23 | 10:00 | 126.77 | 39.3% |
| 24 | 10:30 | 125.00 | 38.3% |
| 25 | 11:00 | 113.84 | 38.5% |
| 26 | 11:30 | 111.16 | 36.3% |
| 27 | 12:00 | 111.15 | 34.7% |
| 28 | 12:30 | 107.61 | 34.7% |
| 29 | 13:00 | 107.61 | 38.6% |
| 30 | 13:30 | 106.95 | 35.6% |
| 31 | 14:00 | 109.48 | 35.3% |
| 32 | 14:30 | 108.10 | 39.2% |
| 33 | 15:00 | 113.43 | 41.4% |
| 34 | 15:30 | 117.18 | 43.6% |
| 35 | 16:00 | 121.67 | 43.8% |
| 36 | 16:30 | 129.24 | 41.8% |
| 37 | 17:00 | 145.28 | 39.1% |
| 38 | 17:30 | 153.62 | 36.8% |
| 39 | 18:00 | 175.00 | 36.6% |
| 40 | 18:30 | 180.00 | 34.8% |
| 41 | 19:00 | 194.43 | 31.7% |
| 42 | 19:30 | 200.00 | 28.5% |
| 43 | 20:00 | 200.10 | 26.9% |
| 44 | 20:30 | 204.00 | 24.8% |
| 45 | 21:00 | 203.29 | 23.5% |
| 46 | 21:30 | 205.00 | 21.4% |
| 47 | 22:00 | 188.30 | 19.9% |
| 48 | 22:30 | 182.52 | 20.9% |

</details>

