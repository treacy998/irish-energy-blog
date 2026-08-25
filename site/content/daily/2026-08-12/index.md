---
title: "I-SEM Daily Briefing — 12 August 2026"
date: 2026-08-12
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €171.8/MWh, peaking at €276.75/MWh at 19:00."
images: ["charts/2026-08-12/card-2026-08-12.png"]
draft: false
---

{{< statbar mean="€171.8" peak="€276.75" min="€128.17" spread="€148.58" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €171.8/MWh    |
| Median Price         | €153.91/MWh    |
| Std Dev              | €47.26/MWh    |
| Peak Price           | €276.75/MWh (19:00) |
| Min Price            | €128.17/MWh (15:00)   |
| Price Range          | €148.58/MWh   |
| Periods above €150   | 27 of 48 (56%) |
| Periods above €200   | 11 of 48 (23%) |
| Peak Avg (07–22)     | €178.3/MWh    |
| Off-peak Avg (22–07) | €160.98/MWh    |
| Peak/Off-Peak Spread | €17.32/MWh   |
| Wind % of Demand     | 19.2%          |
| Wind Range           | 6.8%–36.8% |
| Mean Demand          | 3952 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-12/dam-2026-08-12.png)

**Std dev** €47.26/MWh  ·  **Median** €153.91/MWh  ·  **Periods above €150:** 27 of 48 (56%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-12/price-wind-2026-08-12.png)

**Mean wind:** 19.2%  ·  **Range:** 6.8%–36.8%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-12/week-compare-2026-08-12.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-12/pdc-2026-08-12.png)

**Periods above €150:** 27 (56% of day)  ·  **Above €200:** 11 (23% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-12/spread-2026-08-12.png)

**Peak avg (07:00–22:00):** €178.3/MWh  ·  **Off-peak avg:** €160.98/MWh  ·  **Spread:** €17.32/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €130/MWh | 11:00 | 2 MWh | −€260 |
| **Discharge** | €269/MWh | 18:30 | 1.7 MWh (85% RTE) | +€458 |
| **Gross profit** | | | | **€198** |
| **Price spread** | €139/MWh | | | **ROI: 76.2%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-12/bess-2026-08-12.png)

## Commentary

Wednesday broke Tuesday's flatness wide open. Std dev jumped to €47.26 as a moderate 19.2% wind day (6.8–36.8% range) gave way to a classic evening scarcity ramp: a soft €128.17 trough at 15:00 running into a €276.75 peak just four hours later at 19:00, a €148.58 top-to-bottom range. Eleven of forty-eight periods cleared above €200 — the floor stayed gas-set through the afternoon, the ceiling opened up once wind eased into the evening squeeze.

Storage cashed in on exactly that shape: charge at the 11:00 €130 trough, discharge into the 18:30 ramp at €269, for €198 gross and a 76.2% ROI — comfortably the best return since Tuesday's near-zero spread. The lesson from Tuesday holds in reverse: give storage a real peak to sell into, and the numbers move.


<details>
<summary>Half-hourly data — 2026-08-12</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 160.18 | 7.0% |
| 2 | 23:30 | 154.89 | 6.8% |
| 3 | 00:00 | 152.94 | 34.4% |
| 4 | 00:30 | 150.30 | 35.5% |
| 5 | 01:00 | 144.20 | 36.8% |
| 6 | 01:30 | 142.23 | 35.6% |
| 7 | 02:00 | 143.98 | 34.1% |
| 8 | 02:30 | 142.02 | 34.9% |
| 9 | 03:00 | 141.10 | 33.9% |
| 10 | 03:30 | 141.17 | 32.9% |
| 11 | 04:00 | 145.77 | 33.1% |
| 12 | 04:30 | 146.97 | 32.6% |
| 13 | 05:00 | 155.00 | 32.5% |
| 14 | 05:30 | 159.25 | 31.8% |
| 15 | 06:00 | 163.70 | 28.5% |
| 16 | 06:30 | 169.98 | 27.4% |
| 17 | 07:00 | 176.00 | 24.4% |
| 18 | 07:30 | 178.64 | 22.3% |
| 19 | 08:00 | 157.68 | 20.1% |
| 20 | 08:30 | 165.90 | 19.5% |
| 21 | 09:00 | 152.68 | 16.7% |
| 22 | 09:30 | 147.09 | 15.9% |
| 23 | 10:00 | 136.51 | 15.9% |
| 24 | 10:30 | 133.56 | 15.2% |
| 25 | 11:00 | 131.20 | 14.9% |
| 26 | 11:30 | 129.88 | 14.4% |
| 27 | 12:00 | 129.88 | 15.6% |
| 28 | 12:30 | 128.56 | 16.2% |
| 29 | 13:00 | 133.56 | 15.0% |
| 30 | 13:30 | 132.00 | 15.1% |
| 31 | 14:00 | 131.80 | 14.0% |
| 32 | 14:30 | 131.11 | 15.2% |
| 33 | 15:00 | 128.17 | 15.9% |
| 34 | 15:30 | 128.56 | 15.5% |
| 35 | 16:00 | 155.97 | 14.6% |
| 36 | 16:30 | 163.30 | 12.6% |
| 37 | 17:00 | 190.05 | 13.0% |
| 38 | 17:30 | 201.00 | 11.5% |
| 39 | 18:00 | 251.00 | 11.2% |
| 40 | 18:30 | 270.88 | 10.3% |
| 41 | 19:00 | 276.75 | 9.2% |
| 42 | 19:30 | 265.00 | 8.5% |
| 43 | 20:00 | 264.56 | 7.9% |
| 44 | 20:30 | 262.10 | 7.4% |
| 45 | 21:00 | 252.62 | 8.6% |
| 46 | 21:30 | 243.00 | 8.2% |
| 47 | 22:00 | 251.00 | 8.5% |
| 48 | 22:30 | 232.95 | 8.4% |

</details>

