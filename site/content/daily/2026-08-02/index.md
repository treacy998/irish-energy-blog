---
title: "I-SEM Daily Briefing — 2 August 2026"
date: 2026-08-02
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €167.3/MWh, peaking at €220.53/MWh at 23:00."
images: ["charts/2026-08-02/card-2026-08-02.png"]
draft: false
---

{{< statbar mean="€167.3" peak="€220.53" min="€140.77" spread="€79.76" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €167.3/MWh    |
| Median Price         | €161.74/MWh    |
| Std Dev              | €20.99/MWh    |
| Peak Price           | €220.53/MWh (23:00) |
| Min Price            | €140.77/MWh (11:30)   |
| Price Range          | €79.76/MWh   |
| Periods above €150   | 35 of 48 (73%) |
| Periods above €200   | 5 of 48 (10%) |
| Peak Avg (07–22)     | €163.4/MWh    |
| Off-peak Avg (22–07) | €173.82/MWh    |
| Peak/Off-Peak Spread | €-10.42/MWh   |
| Wind % of Demand     | 13.9%          |
| Wind Range           | 1.6%–29.6% |
| Mean Demand          | 3466 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-08-02/dam-2026-08-02.png)

**Std dev** €20.99/MWh  ·  **Median** €161.74/MWh  ·  **Periods above €150:** 35 of 48 (73%)

## Price vs Wind

![Price vs Wind Generation](/charts/2026-08-02/price-wind-2026-08-02.png)

**Mean wind:** 13.9%  ·  **Range:** 1.6%–29.6%

## Week in Context

![7-Day Price Comparison](/charts/2026-08-02/week-compare-2026-08-02.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-08-02/pdc-2026-08-02.png)

**Periods above €150:** 35 (73% of day)  ·  **Above €200:** 5 (10% of day)

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-08-02/spread-2026-08-02.png)

**Peak avg (07:00–22:00):** €163.4/MWh  ·  **Off-peak avg:** €173.82/MWh  ·  **Spread:** €-10.42/MWh

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €143/MWh | 11:00 | 2 MWh | −€286 |
| **Discharge** | €198/MWh | 19:00 | 1.7 MWh (85% RTE) | +€337 |
| **Gross profit** | | | | **€51** |
| **Price spread** | €55/MWh | | | **ROI: 17.8%** |

*Updated 2026-08-27: the BESS simulation previously allowed the discharge window to occur before the charge window ended, which is physically impossible for a battery — in this case, by picking periods 1–4 (23:00–00:30), which precede the 11:00 charge. Recalculated enforcing charge-before-discharge; gross profit corrected from €58 to €51.*

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-08-02/bess-2026-08-02.png)

## Commentary

The day opened already elevated — €220.53 at 23:00, €206.62 by 23:30, the tail end of Saturday evening demand — before wind reasserted itself just after midnight, collapsing from 29.6% to 1.7% in a single half-hour and dragging price down through the €200s and €190s as it went. From there the pattern turned clean: wind climbed steadily through the morning, reaching 19.4% by 14:00, and price sank in step, bottoming at €140.77 at 11:30 in a shallow trough that ran from 09:30 clean through to 15:30.

The evening rebuild is the odd part. Price climbed to a local high of €200.50 at 19:00 even with wind sitting at a moderate 14% — demand doing the lifting, not wind — only for wind to keep rising into the close, 21.3% at 21:00 and 27.5% by 22:30, and pull price back down to €171.52. Std dev was the lowest of the week at €20.99, and the negative peak/off-peak spread (€-10.42) is the same story as the last few days: the real extremes sit either side of the 07:00–22:00 window, not inside it.

Storage had a quieter day for it — €51 gross, 17.8% ROI, the softest return since Thursday. Charging at €143 and discharging into the evening peak at €198 only found a €55 spread, thin by the week's standards, because this trough was shallow rather than sharp. Calmer prices, calmer battery.


<details>
<summary>Half-hourly data — 2026-08-02</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 220.53 | 29.6% |
| 2 | 23:30 | 206.62 | 29.3% |
| 3 | 00:00 | 200.23 | 1.7% |
| 4 | 00:30 | 182.20 | 1.6% |
| 5 | 01:00 | 175.30 | 2.2% |
| 6 | 01:30 | 171.86 | 2.9% |
| 7 | 02:00 | 175.37 | 3.3% |
| 8 | 02:30 | 167.40 | 4.4% |
| 9 | 03:00 | 163.72 | 5.3% |
| 10 | 03:30 | 161.35 | 6.6% |
| 11 | 04:00 | 164.75 | 7.3% |
| 12 | 04:30 | 163.74 | 8.2% |
| 13 | 05:00 | 159.80 | 9.0% |
| 14 | 05:30 | 157.85 | 10.8% |
| 15 | 06:00 | 155.27 | 12.4% |
| 16 | 06:30 | 155.84 | 13.9% |
| 17 | 07:00 | 154.01 | 13.9% |
| 18 | 07:30 | 155.00 | 14.7% |
| 19 | 08:00 | 159.85 | 12.8% |
| 20 | 08:30 | 161.38 | 12.0% |
| 21 | 09:00 | 154.59 | 11.3% |
| 22 | 09:30 | 148.18 | 10.3% |
| 23 | 10:00 | 149.13 | 10.0% |
| 24 | 10:30 | 145.00 | 11.6% |
| 25 | 11:00 | 142.69 | 14.0% |
| 26 | 11:30 | 140.77 | 15.8% |
| 27 | 12:00 | 144.12 | 16.8% |
| 28 | 12:30 | 144.91 | 17.4% |
| 29 | 13:00 | 145.01 | 18.7% |
| 30 | 13:30 | 145.00 | 19.2% |
| 31 | 14:00 | 142.91 | 19.4% |
| 32 | 14:30 | 142.00 | 18.3% |
| 33 | 15:00 | 145.00 | 18.3% |
| 34 | 15:30 | 145.01 | 17.7% |
| 35 | 16:00 | 156.70 | 16.6% |
| 36 | 16:30 | 162.10 | 16.4% |
| 37 | 17:00 | 172.20 | 15.4% |
| 38 | 17:30 | 178.12 | 15.0% |
| 39 | 18:00 | 195.02 | 12.8% |
| 40 | 18:30 | 195.02 | 13.7% |
| 41 | 19:00 | 200.50 | 14.0% |
| 42 | 19:30 | 200.01 | 13.4% |
| 43 | 20:00 | 197.75 | 14.9% |
| 44 | 20:30 | 195.02 | 17.1% |
| 45 | 21:00 | 195.00 | 21.3% |
| 46 | 21:30 | 189.93 | 24.9% |
| 47 | 22:00 | 175.35 | 25.3% |
| 48 | 22:30 | 171.52 | 27.5% |

</details>

