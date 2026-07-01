---
title: "I-SEM Daily Briefing — 29 June 2026"
date: 2026-06-29
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €130.61/MWh, peaking at €189.47/MWh at 19:00."
images: ["charts/2026-06-29/card-2026-06-29.png"]
draft: false
---

{{< statbar mean="€130.61" peak="€189.47" min="€105.21" spread="€84.26" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €130.61/MWh    |
| Median Price         | €119.71/MWh    |
| Std Dev              | €26.85/MWh    |
| Peak Price           | €189.47/MWh (19:00) |
| Min Price            | €105.21/MWh (13:30)   |
| Price Range          | €84.26/MWh   |
| Periods above €150   | 9 of 48 (19%) |
| Periods above €200   | 0 of 48 (0%) |
| Peak Avg (07–22)     | €137.8/MWh    |
| Off-peak Avg (22–07) | €118.63/MWh    |
| Peak/Off-Peak Spread | €19.17/MWh   |
| Wind % of Demand     | 35.6%          |
| Wind Range           | 25.8%–49.4% |
| Mean Demand          | 3794 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-06-29/dam-2026-06-29.png)

**Std dev** €26.85/MWh  ·  **Median** €119.71/MWh  ·  **Periods above €150:** 9 of 48 (19%)

Weekday demand came back and dragged the market with it. Mean jumped to €130.61 — up €53 on Sunday — even with wind (35.6%) still comfortably above its weekly average.

## Price vs Wind

![Price vs Wind Generation](/charts/2026-06-29/price-wind-2026-06-29.png)

**Mean wind:** 35.6%  ·  **Range:** 25.8%–49.4%

Wind eased back from the weekend's 50%+ readings into the 30s, and demand reasserted itself. The floor lifted to €105, and wind falling to 28% right as demand peaked pushed the evening ceiling up to €189.

## Week in Context

![7-Day Price Comparison](/charts/2026-06-29/week-compare-2026-06-29.png)

First bounce back after the weekend collapse — still nowhere near Wednesday/Thursday's scarcity levels, but demand is clearly returning.

## Price Duration Curve

![Price Duration Curve](/charts/2026-06-29/pdc-2026-06-29.png)

**Periods above €150:** 9 (19% of day)  ·  **Above €200:** 0 (0% of day)

A moderate day — nowhere near Saturday/Sunday's flat floor, nowhere near a scarcity spike either.

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-06-29/spread-2026-06-29.png)

**Peak avg (07:00–22:00):** €137.8/MWh  ·  **Off-peak avg:** €118.63/MWh  ·  **Spread:** €19.17/MWh

Spread back to positive. Normal weekday shape restored after two days of inverted, demand-collapsed spreads.

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €107/MWh | 13:00 | 2 MWh | −€214 |
| **Discharge** | €188/MWh | 18:30 | 1.7 MWh (85% RTE) | +€319 |
| **Gross profit** | | | | **€105** |
| **Price spread** | €81/MWh | | | **ROI: 49.0%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-06-29/bess-2026-06-29.png)

€105 gross, ROI 49% — back to an ordinary storage day. Charge at the €105 midday dip, discharge into the €188 evening peak, no weekend extremes to exploit.

## Commentary

Monday snapped the market back to normal. The weekend's giveaway prices are gone — demand returning to weekday levels (3794MW mean, up from Sunday's 3302MW) was enough on its own to add €53 to the average, even with wind still running above a third of demand.

The shape is textbook again: cheap-ish overnight and midday, a real evening peak as wind eased off into the demand ramp. After two days of an inverted, wind-flooded market, this is what "normal" looks like this month.


<details>
<summary>Half-hourly data — 2026-06-29</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 125.78 | 46.3% |
| 2 | 23:30 | 122.47 | 49.4% |
| 3 | 00:00 | 118.42 | 47.6% |
| 4 | 00:30 | 114.49 | 46.0% |
| 5 | 01:00 | 111.18 | 45.3% |
| 6 | 01:30 | 110.04 | 44.9% |
| 7 | 02:00 | 110.08 | 43.5% |
| 8 | 02:30 | 108.08 | 43.8% |
| 9 | 03:00 | 109.27 | 44.3% |
| 10 | 03:30 | 108.04 | 43.3% |
| 11 | 04:00 | 110.04 | 42.0% |
| 12 | 04:30 | 108.08 | 39.0% |
| 13 | 05:00 | 111.78 | 37.6% |
| 14 | 05:30 | 112.80 | 38.5% |
| 15 | 06:00 | 129.40 | 36.3% |
| 16 | 06:30 | 137.40 | 33.9% |
| 17 | 07:00 | 140.20 | 29.0% |
| 18 | 07:30 | 144.82 | 25.8% |
| 19 | 08:00 | 137.02 | 26.2% |
| 20 | 08:30 | 136.84 | 26.6% |
| 21 | 09:00 | 126.09 | 27.1% |
| 22 | 09:30 | 121.00 | 26.5% |
| 23 | 10:00 | 111.31 | 28.4% |
| 24 | 10:30 | 110.91 | 29.2% |
| 25 | 11:00 | 109.91 | 30.7% |
| 26 | 11:30 | 108.29 | 31.8% |
| 27 | 12:00 | 108.29 | 32.2% |
| 28 | 12:30 | 108.29 | 34.1% |
| 29 | 13:00 | 108.57 | 33.8% |
| 30 | 13:30 | 105.21 | 34.9% |
| 31 | 14:00 | 106.60 | 32.1% |
| 32 | 14:30 | 107.64 | 32.7% |
| 33 | 15:00 | 114.02 | 30.4% |
| 34 | 15:30 | 115.07 | 31.9% |
| 35 | 16:00 | 126.04 | 32.2% |
| 36 | 16:30 | 131.98 | 31.0% |
| 37 | 17:00 | 142.52 | 30.8% |
| 38 | 17:30 | 152.58 | 31.0% |
| 39 | 18:00 | 186.00 | 28.0% |
| 40 | 18:30 | 188.03 | 30.2% |
| 41 | 19:00 | 189.47 | 32.7% |
| 42 | 19:30 | 186.00 | 35.1% |
| 43 | 20:00 | 186.77 | 34.7% |
| 44 | 20:30 | 184.39 | 35.2% |
| 45 | 21:00 | 172.03 | 37.3% |
| 46 | 21:30 | 168.04 | 39.7% |
| 47 | 22:00 | 149.26 | 42.0% |
| 48 | 22:30 | 138.77 | 44.6% |

</details>

