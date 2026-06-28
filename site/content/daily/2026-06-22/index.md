---
title: "I-SEM Daily Briefing — 22 June 2026"
date: 2026-06-22
authors: ["Eoin"]
tags: ["daily-briefing", "DAM", "I-SEM"]
summary: "DAM prices averaged €179.0/MWh, peaking at €240.7/MWh at 22:00."
images: ["charts/2026-06-22/card-2026-06-22.png"]
draft: false
---

{{< statbar mean="€179.0" peak="€240.7" min="€131.5" spread="€109.2" >}}

<details>
<summary>Market Snapshot</summary>

| Metric               | Value               |
|----------------------|---------------------|
| Mean DAM Price       | €179.0/MWh    |
| Median Price         | €174.92/MWh    |
| Std Dev              | €35.86/MWh    |
| Peak Price           | €240.7/MWh (22:00) |
| Min Price            | €131.5/MWh (01:30)   |
| Price Range          | €109.2/MWh   |
| Periods above €150   | 34 of 48 (71%) |
| Periods above €200   | 15 of 48 (31%) |
| Peak Avg (07–22)     | €191.93/MWh    |
| Off-peak Avg (22–07) | €157.44/MWh    |
| Peak/Off-Peak Spread | €34.49/MWh   |
| Wind % of Demand     | 5.3%          |
| Wind Range           | 1.8%–14.2% |
| Mean Demand          | 3802 MW       |

</details>

## Price Profile

![DAM Price Profile](/charts/2026-06-22/dam-2026-06-22.png)

**Std dev** €35.86/MWh  ·  **Median** €174.92/MWh  ·  **Periods above €150:** 34 of 48 (71%)

Monday arrived and the market repriced hard. Demand jumped back to 3,802 MW and wind stayed negligible at 5.3% with barely any range (1.8%–14.2%). Mean €179.00 — up €44 on Sunday. The morning ramp was steep: €137.80 at 05:00 to €200.59 at 06:30 in 90 minutes as commercial demand switched on. Then the evening scarcity — prices above €200 from 18:00 through end of day, peaking at €240.70 at 22:00. The only floor came from a brief overnight wind pulse around 01:00-02:00; without that, there was nowhere cheap all day.

## Price vs Wind

![Price vs Wind Generation](/charts/2026-06-22/price-wind-2026-06-22.png)

**Mean wind:** 5.3%  ·  **Range:** 1.8%–14.2%

A brief overnight recovery (11-14% from 23:30-02:00) gave the only softness — the €131-145 window. From 04:00 onward wind fell steadily: 9.7% at 04:00, 5.7% at 07:00, bottoming at 1.8% by 20:00. Price and wind moved in lock-step. When wind hit 2% in the evening, prices hit €232-240. The inverse correlation doesn't get much cleaner.

## Week in Context

![7-Day Price Comparison](/charts/2026-06-22/week-compare-2026-06-22.png)

## Price Duration Curve

![Price Duration Curve](/charts/2026-06-22/pdc-2026-06-22.png)

**Periods above €150:** 34 (71% of day)  ·  **Above €200:** 15 (31% of day)

15 periods above €200 (31%), 34 above €150 (71%). The curve is steep at the top — a genuine scarcity cluster from the evening. The floor is still €131.50 thanks to the overnight wind pulse; without that, it would have been a fully gas-set 48-period day. From 06:00 onward, the merit order is essentially all-gas, all-day.

## Peak / Off-Peak Spread

![Peak / Off-Peak Spread](/charts/2026-06-22/spread-2026-06-22.png)

**Peak avg (07:00–22:00):** €191.93/MWh  ·  **Off-peak avg:** €157.44/MWh  ·  **Spread:** €34.49/MWh

Spread back in positive territory at €34.49 — normal weekday structure restored. The off-peak (€157.44) was elevated by the late Sunday scarcity tail plus Monday evening. The peak (€191.93) is the morning ramp and prolonged evening scarcity averaged out. An arbitrage window existed via the overnight softness, but you needed patience — charge at 00:30 and wait all the way to 21:00 to discharge.

## BESS Dispatch Signal

| | Price | Time | Energy | Value |
|--|--|--|--|--|
| **Charge** | €135/MWh | 00:30 | 2 MWh | −€269 |
| **Discharge** | €237/MWh | 21:00 | 1.7 MWh (85% RTE) | +€402 |
| **Gross profit** | | | | **€133** |
| **Price spread** | €102/MWh | | | **ROI: 49.6%** |

*Simulated 1MW/2MWh battery, one optimal DAM cycle. Gross before network charges and capacity costs.*

![BESS Dispatch](/charts/2026-06-22/bess-2026-06-22.png)

Charge at €135 at 00:30 — overnight wind window, 11.2% wind at that moment. Discharge at €237 at 21:00 — middle of the evening scarcity. €133 gross, ROI 49.6%. The overnight wind pulse was short-lived but just long enough to create the charge window. The evening scarcity paid handsomely. Better than the compressed-spread May days: this spread came from a genuine scarcity spike, not a modest ramp.

## Commentary

Monday's return to work snapped the market back to full attention. Mean €179.00, up €44 on Sunday, and 15 periods clearing above €200 — the scarcity is real. Wind at 5.3% throughout contributed almost nothing, forcing gas to cover nearly all of the 3,802 MW mean demand.

The day has two distinct acts. The morning ramp (€137 → €200 in 90 minutes from 05:00 to 06:30) is demand waking up with no wind available. Prices held elevated through the midday (€145-198 range) before the evening scarcity took hold: from 16:00 onward, prices ran €186-240 as wind hit its lowest readings all week (1.8-3.5%) right into peak evening demand.

The only relief came from the overnight wind pulse around 01:00-02:00 (13-14%), which pulled the floor to €131.50 and gave storage its charge window. Without that pulse, the BESS would have had nowhere cheap to charge. Even with it, the spread was €135 to €237 — a good day for batteries, but a punishing day for everyone else.




<details>
<summary>Half-hourly data — 2026-06-22</summary>

| Period | Time | Price (€/MWh) | Wind % |
|--------|------|--------------|--------|
| 1 | 23:00 | 171.00 | 3.4% |
| 2 | 23:30 | 155.00 | 4.3% |
| 3 | 00:00 | 145.00 | 10.9% |
| 4 | 00:30 | 132.77 | 11.2% |
| 5 | 01:00 | 135.28 | 13.2% |
| 6 | 01:30 | 131.50 | 14.2% |
| 7 | 02:00 | 138.48 | 13.2% |
| 8 | 02:30 | 138.20 | 12.0% |
| 9 | 03:00 | 138.42 | 11.5% |
| 10 | 03:30 | 136.00 | 10.4% |
| 11 | 04:00 | 136.56 | 9.7% |
| 12 | 04:30 | 136.15 | 9.4% |
| 13 | 05:00 | 137.80 | 8.4% |
| 14 | 05:30 | 152.72 | 7.1% |
| 15 | 06:00 | 175.01 | 6.8% |
| 16 | 06:30 | 200.59 | 6.2% |
| 17 | 07:00 | 179.60 | 5.7% |
| 18 | 07:30 | 195.00 | 4.8% |
| 19 | 08:00 | 203.20 | 4.4% |
| 20 | 08:30 | 195.38 | 4.5% |
| 21 | 09:00 | 203.14 | 4.2% |
| 22 | 09:30 | 194.69 | 4.4% |
| 23 | 10:00 | 186.89 | 4.0% |
| 24 | 10:30 | 175.06 | 3.4% |
| 25 | 11:00 | 174.83 | 2.6% |
| 26 | 11:30 | 171.29 | 2.4% |
| 27 | 12:00 | 163.07 | 3.5% |
| 28 | 12:30 | 158.58 | 3.4% |
| 29 | 13:00 | 156.95 | 3.4% |
| 30 | 13:30 | 145.94 | 3.0% |
| 31 | 14:00 | 150.91 | 2.6% |
| 32 | 14:30 | 147.90 | 2.5% |
| 33 | 15:00 | 149.86 | 2.0% |
| 34 | 15:30 | 150.80 | 2.5% |
| 35 | 16:00 | 186.64 | 3.5% |
| 36 | 16:30 | 198.40 | 5.1% |
| 37 | 17:00 | 204.70 | 4.7% |
| 38 | 17:30 | 221.00 | 3.1% |
| 39 | 18:00 | 213.00 | 2.9% |
| 40 | 18:30 | 223.90 | 2.7% |
| 41 | 19:00 | 232.88 | 2.2% |
| 42 | 19:30 | 238.44 | 1.9% |
| 43 | 20:00 | 232.26 | 1.8% |
| 44 | 20:30 | 230.29 | 2.0% |
| 45 | 21:00 | 237.80 | 2.5% |
| 46 | 21:30 | 235.40 | 2.9% |
| 47 | 22:00 | 240.70 | 3.1% |
| 48 | 22:30 | 232.80 | 3.1% |

</details>

