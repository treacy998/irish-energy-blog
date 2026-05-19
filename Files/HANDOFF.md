# INIS Energy Blog — Full Project Handoff
*Updated 19 May 2026*

---

## 1. Who This Is For

**Eoin Treacy** — Cork-based energy broker, founder of INIS Energy (CRU-regulated). Background in computer science (React, Laravel, Python). Career goal: transition into high-value energy roles — analyst, flexibility, trading, consulting, regulatory — and command a strong salary.

---

## 2. What the Blog Is and Why It Exists

A personal data-driven energy market blog at **https://irish-energy-blog.vercel.app**, publishing daily and weekly analysis of the Irish electricity market (I-SEM / SEM-DA).

**Four simultaneous purposes:**
1. **Public portfolio** — proves to hiring managers that Eoin understands Irish energy markets and can work with real data
2. **Daily learning** — writing commentary forces daily engagement with market dynamics
3. **Python skill-building** — the pipeline is itself a demonstrable project
4. **SEO and visibility** — Irish energy market content is low-competition; consistent posts rank quickly

Eoin's brother (also in energy) will join as co-author later.

---

## 3. Current State (as of 19 May 2026)

**The full pipeline is operational.** All infrastructure priorities are complete.

### Live content
- 5 live daily posts (16 Apr, 6 May, 12 May, 13 May, 15 May 2026)
- All posts still have `<!-- Commentary -->` placeholder — **writing commentary is the current focus**
- 0 weekly posts published (section exists, template works)
- Active backfill in progress: targeting 2 weeks of daily posts with full commentary

### What fully works
- `./blog` TUI — single entry point, numbered menu, any terminal
- Automated SEMO download via `fetch_semo()` — no manual CSV download needed
- EirGrid wind + demand auto-fetch via `/api/chart/` endpoint
- **5 charts per daily post:** DAM profile, price-vs-wind, price duration curve, peak/off-peak spread, BESS dispatch
- Stat bar shortcode — 4 metric chips (mean/peak/min/spread) at top of every post
- BESS dispatch simulation — optimal 1MW/2MWh cycle, gross profit, running total
- Dark navy chart style, IBM Plex Serif headings, JetBrains Mono numbers
- BST/GMT timezone correct via `zoneinfo.ZoneInfo("Europe/Dublin")`
- Hugo + Congo + Vercel — auto-deploys on push, ~30s

---

## 4. Architecture

```
SEMO API (auto)               EirGrid API (auto)
      │                              │
      ▼                              ▼
 data/*.csv ──────────── process.py + fetch.py
                                     │
                                run_daily.py
                          ┌──────────┼──────────┐
                       charts.py  bess.py  scaffold.py
                          │                     │
              static/charts/*.png     content/daily/YYYY-MM-DD.md
                                     │
                                Hugo build
                                     │
                              git push → Vercel
                                     │
                          irish-energy-blog.vercel.app
```

### Tech stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Site generator | Hugo Extended 0.146.0 | Static, ~250ms build |
| Theme | Congo (git submodule) | Ocean scheme, custom CSS overrides |
| Data processing | Python 3.13.7 + pandas | In `venv/` |
| Charts | matplotlib | 5 chart types, dark navy style |
| CLI/TUI | Rich + plain input() | Numbered menu |
| Deployment | Vercel | Auto-deploy on push |
| Source control | Git | github.com/treacy998/irish-energy-blog |

---

## 5. Pipeline Components

### `./blog` (entry point)
Two-line bash script. Activates venv, launches `pipeline/tui.py`. All activity logged to `blog.log`.

### `pipeline/tui.py`
6-option numbered menu:
1. New daily briefing — runs pipeline, opens post in VS Code
2. New post — blank daily or weekly, opens in VS Code
3. Manage posts — table of all posts; edit/toggle draft/delete
4. Preview site — hugo server -D at localhost:1313
5. Deploy — git add → commit → push
6. Quit

### `pipeline/fetch.py`
Two public functions:

**`fetch_semo(delivery_date, out_dir)`** — Downloads SEM-DA Market Results CSV from the SEMOpx REST API. Handles caching, date lookups, streaming download. Returns Path to saved file or None. Runs automatically at pipeline start.

**`fetch_wind_and_demand(delivery_date)`** — Hits EirGrid Smart Grid Dashboard API at `https://www.smartgriddashboard.com/api/chart/` with `chartType=wind` or `demand`. Returns 48-row DataFrame (30-min periods). Failures non-fatal.

> ⚠️ The old `DashboardService.svc` endpoint is permanently dead since ~Jan 2026. Always use `/api/chart/`.

### `pipeline/process.py`
Parses SEMO's non-standard semicolon-delimited format. Extracts 48-period EUR DAM prices. Timezone conversion uses `zoneinfo.ZoneInfo("Europe/Dublin")` — correct for both BST and GMT.

Output: DataFrame with `DeliveryDate | Period | StartTime | DAMPrice_EUR_MWh`

### `pipeline/bess.py`
Simulates a 1MW/2MWh battery making one optimal DAM cycle per day.

- Charge window: 4 consecutive lowest-price half-hours
- Discharge window: 4 consecutive highest-price half-hours
- Round-trip efficiency: 85% applied to discharge
- Returns: `charge_mean`, `charge_start`, `discharge_mean`, `discharge_start`, `gross_revenue`, `charge_cost`, `gross_profit`, `spread`
- Gross figures only — before network charges, capacity costs, degradation

### `pipeline/charts.py`
5 charts per day, 12×4.8", 150 DPI, dark navy:

| Chart | File | Description |
|-------|------|-------------|
| DAM Price Profile | `dam-YYYY-MM-DD.png` | 48-period price line, peak/min annotations, mean dashed |
| Price vs Wind | `price-wind-YYYY-MM-DD.png` | Dual-axis price + wind %. Skipped if no EirGrid data |
| Price Duration Curve | `pdc-YYYY-MM-DD.png` | 48 prices sorted high-to-low, teal bars, €100/150/200 reference lines, period count annotations |
| Peak/Off-Peak Spread | `spread-YYYY-MM-DD.png` | Two horizontal bars (amber peak, blue off-peak), spread bracket, large €X label |
| BESS Dispatch | `bess-YYYY-MM-DD.png` | Full price profile with charge window (blue), discharge window (amber), spread bracket |

Palette: `#0D1B2A` bg, `#2EC4B6` price, `#FFB703` amber, `#E63946` min, `#7FB069` wind, `#85B7EB` historical.

### `pipeline/scaffold.py`
Generates `site/content/daily/YYYY-MM-DD.md` with:
- YAML frontmatter
- `{{< statbar >}}` shortcode — 4 metric chips (mean/peak/min/spread)
- Collapsible full stats table
- 5 conditionally embedded chart images
- BESS dispatch table (charge/discharge windows, gross profit)
- `## Commentary` and `## BESS Dispatch` commentary placeholders

### `site/layouts/shortcodes/statbar.html`
Named params: `mean`, `peak`, `min`, `spread`. Renders 4 dark navy metric chips with teal values.

### `site/assets/css/custom.css`
IBM Plex Serif headings, JetBrains Mono numbers, teal accent `#2EC4B6`, tag pills navy/teal.

### `vercel.json`
Downloads Hugo Extended 0.146.0 at build time. Builds from `site/`, outputs to `site/public/`.

---

## 6. Daily Workflow

Fully automated — no manual steps except writing commentary.

```
./blog → option 1    # auto-downloads SEMO, fetches EirGrid,
                     # generates 5 charts, scaffolds post, opens in VS Code
```

Write commentary → `./blog → option 4` (preview) → `./blog → option 5` (deploy)

**For backfilling past dates:** Pass `--date YYYY-MM-DD` directly to `run_daily.py` — it auto-downloads that day's SEM-DA CSV, fetches EirGrid wind/demand, generates all 5 charts, and scaffolds the post.

---

## 7. Known Gaps

### ✅ 7.1 `--date` flag added to `run_daily.py`
`argparse` added with a `--date YYYY-MM-DD` argument (mutually exclusive with a positional CSV path). When provided, it is passed directly to `fetch_semo()`, which converts to the correct SEMOpx trading date and skips the download if the file is already cached. Backfill a day with:

```bash
venv/bin/python pipeline/run_daily.py --date 2026-05-04
```

Or loop over a range:

```bash
for d in 2026-05-04 2026-05-05 2026-05-06 ...; do
    venv/bin/python pipeline/run_daily.py --date $d
done
```

### 7.2 Git grows with binary chart PNGs
5 charts per post committed to git. After 100 days: ~500 PNGs, ~70MB git history.

**Fix:** Add `site/static/charts/` to `.gitignore`, upload to Vercel Blob or Cloudflare R2 at build time.

### 7.3 Week comparison requires retained CSVs
`chart_week_comparison()` scans `data/` for prior files.

**Fix:** Export processed DataFrames to SQLite or Parquet.

### 7.4 TUI shows exit code not error detail
When `run_daily.py` fails, check `blog.log` for the actual error.

### 7.5 Weekly posts section unused
Zero posts published. Looks empty to visitors.

### 7.6 Commentary placeholder on all live posts
Active work item — targeting 2 weeks of backfilled daily commentary.

---

## 8. Priority Backlog

### ✅ Complete (1–8)
1. Chart style overhaul — dark navy palette, annotations, watermark
2. Congo typography + colour identity — IBM Plex Serif, JetBrains Mono, teal accent
3. EirGrid wind + demand integration — new `/api/chart/` endpoint
4. Price duration curve + peak/off-peak spread — two new chart types
5. Stat bar shortcode — 4 metric chips at post header
6. BESS dispatch simulation — `bess.py` module, chart, scaffold integration
7. BST/GMT timezone fix — `zoneinfo.ZoneInfo("Europe/Dublin")`
8. Automated SEMO download — `fetch_semo()` via SEMOpx REST API

### Remaining (9–12)
9. **Homepage hero** — sparkline of last 7 days mean price
10. **Post card redesign** — mean price on list page cards (Congo partial override)
11. **Carbon intensity overlay** — EirGrid CO₂ intensity (gCO₂/kWh) per half-hour
12. **GB interconnector data** — Elexon BMRS, I-SEM vs GB daily comparison

---

## 9. Writing Reference

Five printed A4 reference sheets exist (one per chart type) covering what to look for, angles to rotate through, hook formulas, and salary signal keywords. Structure for every post:

1. **Hook** — lead with the most surprising number
2. **Context** — why did that happen?
3. **Insight** — pattern, trend, implication
4. **Signal** — forward-looking, what should a market participant do with this?

| Chart | Primary angle | Salary signal keywords |
|-------|--------------|----------------------|
| DAM price profile | Price formation, morning ramp, spike cause | Marginal cost pricing, thermal price-setting |
| Price vs wind | Cannibalisation depth, decoupling events | Merit order effect, capture price |
| Price duration curve | Market structure, scarcity hours | PDC, intraday spread, scarcity pricing |
| BESS dispatch | Gross profit, wind-spread correlation | Dispatch optimisation, arbitrage, DS3 |
| Demand shape | Load factor, DR value, duck curve | Peak shaving, demand response, network peak |

---

## 10. SEMO Data Format Reference

File pattern: `MarketResult_SEM-DA_PWR-MRC-D+1_*.csv`

| Property | Value |
|----------|-------|
| Delimiter | Semicolon (;) |
| Decimal separator | European comma (161,70 = 161.70) |
| Layout | Wide/transposed — 48 values per row |
| Key block | `Index prices;30;EUR` = DAM prices in €/MWh |
| Timestamps | UTC. SEM day: 22:00Z–21:30Z |
| Delivery date | Auction date + 1 day |
| Valid files only | SEM-DA. Reject IDA1, IDA2, SEM-GB |

---

## 11. Environment Reference

| Item | Value |
|------|-------|
| Project root | `~/dev/blog/irish-energy-blog` |
| Entry point | `./blog` |
| Python env | `venv/` (Python 3.13.7) |
| Hugo binary | `~/.local/bin/hugo` v0.146.0 |
| Content | `site/content/daily/` and `site/content/weekly/` |
| Charts output | `site/static/charts/` |
| Raw data | `data/` (gitignored) |
| Activity log | `blog.log` |
| Editor | VS Code (`code <file>`) |
| OS | Ubuntu |

---

## 12. The Bigger Picture

The pipeline is complete. 5 charts per post, fully automated data fetching, BESS simulation, professional site design. **What the blog needs now is content.**

Daily posts with real commentary — explaining why prices moved, what the wind data means, what the BESS numbers say about market conditions — is what turns an impressive Python project into a genuine career asset. Hiring managers in energy analysis, flexibility, trading, and consulting will find this blog. A candidate publishing daily I-SEM price analysis with BESS dispatch simulation, written by someone who clearly understands the market, is rare.

**The pipeline is done. Write.**
