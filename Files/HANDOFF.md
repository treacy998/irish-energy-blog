# INIS Energy Blog — Full Project Handoff
*Updated 20 May 2026 (rev 4)*

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

## 3. Current State (as of 20 May 2026)

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
- **Extended stats in every post** — median price, std dev, periods above €150/€200, peak/off-peak averages and spread, wind range (min/max %) — surfaced in the Market Snapshot table and as inline callouts under each chart section
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
    static/charts/YYYY-MM-DD/*.png     content/daily/YYYY-MM-DD/index.md
    static/charts/YYYY-MM-DD/*.html    (interactive Plotly, local only)
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
| Charts | matplotlib + Plotly | 5 chart types per day — PNG for blog, interactive HTML for local analysis |
| CLI/TUI | Rich + plain input() | Numbered menu |
| Deployment | Vercel | Auto-deploy on push |
| Source control | Git | github.com/treacy998/irish-energy-blog |

---

## 5. Pipeline Components

### `./blog` (entry point)
Two-line bash script. Activates venv, launches `pipeline/tui.py`. All activity logged to `blog.log`.

### `pipeline/tui.py`
7-option numbered menu:
1. New daily briefing — runs pipeline, opens post in VS Code
2. New post — blank daily or weekly, opens in VS Code
3. Manage posts — table of all posts; edit/toggle draft/delete
4. Open interactive charts — lists last 10 dates with charts, pick a number, all HTML charts open in browser
5. Preview site — hugo server -D at localhost:1313
6. Deploy — git add → commit → push
7. Quit

`get_all_posts()` finds both leaf bundles (`YYYY-MM-DD/index.md`) and legacy flat `.md` files, so Manage Posts works correctly with the new directory structure.

### `pipeline/fetch.py`
Two public functions:

**`fetch_semo(delivery_date, out_dir)`** — Downloads SEM-DA Market Results CSV from the SEMOpx REST API. Handles caching, date lookups, streaming download. Returns Path to saved file or None. Runs automatically at pipeline start.

**`fetch_wind_and_demand(delivery_date)`** — Hits EirGrid Smart Grid Dashboard API at `https://www.smartgriddashboard.com/api/chart/` with `chartType=wind` or `demand`. Returns 48-row DataFrame (30-min periods). Failures non-fatal.

> ⚠️ The old `DashboardService.svc` endpoint is permanently dead since ~Jan 2026. Always use `/api/chart/`.

### `pipeline/process.py`
Parses SEMO's non-standard semicolon-delimited format. Extracts 48-period EUR DAM prices. Timezone conversion uses `zoneinfo.ZoneInfo("Europe/Dublin")` — correct for both BST and GMT.

Output: DataFrame with `DeliveryDate | Period | StartTime | DAMPrice_EUR_MWh`

`daily_summary()` returns an extended stats dict:

| Key | Description |
|-----|-------------|
| `mean_price` | Daily mean DAM price |
| `median_price` | Median — less sensitive to spike distortion than mean |
| `peak_price` / `peak_time` | Highest half-hour price and its time |
| `min_price` / `min_time` | Lowest half-hour price and its time |
| `price_range` | Peak − min |
| `std_dev` | Standard deviation — proxy for intraday price volatility |
| `periods_above_150` | Count of half-hours with price > €150 |
| `periods_above_200` | Count of half-hours with price > €200 |
| `peak_mean` | Mean price during peak hours (07:00–22:00) |
| `offpeak_mean` | Mean price during off-peak hours (22:00–07:00) |
| `peak_offpeak_spread` | `peak_mean − offpeak_mean` |
| `wind_pct_mean` | Mean wind % of demand (if EirGrid data available) |
| `wind_pct_min` / `wind_pct_max` | Wind generation range across the day |
| `demand_mean_mw` | Mean system demand in MW |

### `pipeline/bess.py`
Simulates a 1MW/2MWh battery making one optimal DAM cycle per day.

- Charge window: 4 consecutive lowest-price half-hours
- Discharge window: 4 consecutive highest-price half-hours
- Round-trip efficiency: 85% applied to discharge
- Returns: `charge_mean`, `charge_start`, `discharge_mean`, `discharge_start`, `gross_revenue`, `charge_cost`, `gross_profit`, `spread`
- Gross figures only — before network charges, capacity costs, degradation

### `pipeline/charts.py`
5 charts per day, 12×4.8", 150 DPI, warm cream palette. All outputs go into `site/static/charts/YYYY-MM-DD/` (one folder per date).

| Chart | PNG file | Description |
|-------|----------|-------------|
| DAM Price Profile | `dam-YYYY-MM-DD.png` | 48-period price line, peak/min annotations, mean dashed |
| Price vs Wind | `price-wind-YYYY-MM-DD.png` | Dual-axis price + wind %. Skipped if no EirGrid data |
| Price Duration Curve | `pdc-YYYY-MM-DD.png` | 48 prices sorted high-to-low, bars, €100/150/200 reference lines |
| Peak/Off-Peak Spread | `spread-YYYY-MM-DD.png` | Two horizontal bars (amber peak, brown off-peak), spread bracket |
| BESS Dispatch | `bess-YYYY-MM-DD.png` | Price profile with charge (brown) and discharge (amber) windows |

After generating PNGs, `charts.py` calls `generate_interactive_charts()` from `charts_interactive.py`, producing an `.html` version of each chart in the same folder.

Palette: `#FAFAF9` bg, `#395e16` price green, `#B8722A` amber, `#A83C3C` min red, `#7A6D5E` wind stone.

### `pipeline/charts_interactive.py`
Generates standalone Plotly HTML charts alongside every PNG. Same 5 chart types; same palette. Files are self-contained (CDN-linked Plotly.js) — open directly in a browser. Features:
- Hover for exact price/time values on every period
- Zoom and pan any time window
- Week comparison: click legend entries to show/hide individual days
- No extra installs beyond `plotly` (already in `venv/`)

**Viewing:** At the end of every `run_daily.py` run, all HTML charts for that date are auto-opened in the browser via `xdg-open`. Write commentary in VS Code while charts are live in the browser — no manual navigation needed.

To re-open charts for any date, use the TUI: `./blog → option 4 → pick a date`. Lists the 10 most recent dates with charts; defaults to the most recent.

### `pipeline/scaffold.py`
Generates `site/content/daily/YYYY-MM-DD/index.md` (Hugo leaf bundle — keeps URL as `/daily/YYYY-MM-DD/`). Contains:
- YAML frontmatter
- `{{< statbar >}}` shortcode — 4 metric chips (mean/peak/min/spread)
- Collapsible **Market Snapshot** table — expanded to include: mean, median, std dev, peak, min, range, periods above €150/€200, peak avg, off-peak avg, peak/off-peak spread, wind % mean, wind range, mean demand
- 5 conditionally embedded chart images (paths: `/charts/YYYY-MM-DD/chartname.png`), each followed by an inline stat callout:
  - **Price Profile** → std dev · median · periods above €150
  - **Price vs Wind** → mean wind · wind range (min–max %)
  - **Price Duration Curve** → periods above €150 and €200 with % of day
  - **Peak/Off-Peak Spread** → peak avg · off-peak avg · spread
- BESS dispatch table — charge/discharge windows, gross profit, price spread, ROI %
- `## Commentary` placeholder
- Collapsed `<details>` block with the full 48-period half-hourly data table (period, time, price, wind % if available)

### `pipeline/storage.py`
Handles upload and download of chart PNGs to/from Vercel Blob. All functions are no-ops when `BLOB_READ_WRITE_TOKEN` is not set, so the pipeline works without blob configured.

- `upload_charts_for_date(chart_day_dir)` — called automatically by `run_daily.py` after chart generation
- `bulk_upload()` — one-time migration of all existing PNGs
- `bulk_download()` — called by Vercel at build time to restore charts before Hugo runs

### `site/layouts/shortcodes/statbar.html`
Named params: `mean`, `peak`, `min`, `spread`. Renders 4 dark navy metric chips with teal values.

### `site/assets/css/custom.css`
IBM Plex Serif headings, JetBrains Mono numbers, teal accent `#2EC4B6`, tag pills navy/teal.

### `vercel.json`
Downloads Hugo Extended 0.146.0 and installs `requests` at build time. Runs `python3 pipeline/storage.py download` before the Hugo build — no-ops if no blob token, downloads charts from Vercel Blob if token is set. Builds from `site/`, outputs to `site/public/`.

---

## 6. Daily Workflow

Fully automated — no manual steps except writing commentary.

**Normal daily run (from project root):**

```bash
cd ~/dev/blog/irish-energy-blog
./blog
# Select option 1 — New daily briefing
# Pipeline auto-downloads SEMO, fetches EirGrid, generates 5 charts,
# scaffolds the post, and opens it in VS Code.
```

**Write the Commentary section, then preview and deploy:**

```bash
./blog
# Select option 5 — Preview site (http://localhost:1313)

./blog
# Select option 6 — Deploy (git add → commit → push → Vercel auto-builds)
```

**Backfill a specific past date (without the TUI):**

```bash
cd ~/dev/blog/irish-energy-blog
pipeline/run_daily.py --date 2026-05-04
```

**Backfill a range of dates:**

```bash
cd ~/dev/blog/irish-energy-blog
for d in 2026-05-04 2026-05-05 2026-05-06 2026-05-07 2026-05-08; do
    pipeline/run_daily.py --date $d
done
```

---

## 7. Known Gaps

### ✅ 7.1 `--date` backfill flag

`argparse` added to `run_daily.py` with a `--date YYYY-MM-DD` argument. When provided, it is passed directly to `fetch_semo()`, which converts to the correct SEMOpx trading date and skips the download if the file is already cached.

```bash
cd ~/dev/blog/irish-energy-blog
pipeline/run_daily.py --date 2026-05-04
```

---

### ✅ 7.2 Git grows with binary chart files

**HTML files** — fully resolved. Interactive Plotly charts (`*.html`) are now gitignored and removed from the index. They are local-only analysis tools; Hugo and Vercel never needed them. New pipeline runs will not track them.

**PNG files** — infrastructure complete, activation requires a Vercel Blob store (one-time setup below).

#### What was built

- `pipeline/storage.py` — uploads PNGs to Vercel Blob after each pipeline run; downloads them at Vercel build time so Hugo can find them. No-ops gracefully without the token.
- `pipeline/run_daily.py` — calls `upload_charts_for_date()` after every run. New charts auto-upload once the token is in the environment.
- `vercel.json` — runs `python3 pipeline/storage.py download` before `hugo` at build time. Without a token this is a no-op and charts are served from git as before.
- `.gitignore` — HTML files gitignored and removed from index. PNG rule is present but commented out, ready to uncomment after the one-time upload below.

#### How to activate Vercel Blob (one-time)

**Step 1 — Create the Blob store:**

Go to https://vercel.com/dashboard → your project → **Storage** tab → **Create Database** → **Blob**. Copy the `BLOB_READ_WRITE_TOKEN` value shown.

**Step 2 — Upload all existing chart PNGs:**

```bash
cd ~/dev/blog/irish-energy-blog
export BLOB_READ_WRITE_TOKEN=vercel_blob_rw_xxxxxxxxxxxxxxxxxx
venv/bin/python pipeline/storage.py upload
```

**Step 3 — Add the token to Vercel's build environment:**

Go to https://vercel.com/dashboard → your project → **Settings** → **Environment Variables** → add:
- Key: `BLOB_READ_WRITE_TOKEN`
- Value: the token from Step 1
- Environments: Production, Preview, Development

**Step 4 — Stop tracking PNGs in git:**

```bash
cd ~/dev/blog/irish-energy-blog

# Uncomment the PNG line in .gitignore (line reads: # site/static/charts/**/*.png)
sed -i 's|# site/static/charts/\*\*/\*.png|site/static/charts/**/*.png|' .gitignore

# Remove all tracked PNGs from the git index (keeps local files intact)
git rm --cached site/static/charts/**/*.png

# Commit and push — Vercel will now download from blob at build time
git add .gitignore
git commit -m "Move chart PNGs to Vercel Blob, stop tracking in git"
git push
```

After this, every `run_daily.py` run automatically uploads new PNGs to blob. The git repo no longer grows with binary files.

---

### 7.3 Week comparison requires retained CSVs

`chart_week_comparison()` scans `data/` for prior CSV files. If old CSVs are deleted the week-compare chart shows fewer days.

**Fix:** Export processed DataFrames to SQLite or Parquet so week history is preserved independently of the raw CSV files.

### 7.4 TUI shows exit code not error detail

When `run_daily.py` fails inside the TUI, the error is swallowed. Check `blog.log` for the full traceback:

```bash
cat ~/dev/blog/irish-energy-blog/blog.log | tail -50
```

### 7.5 Weekly posts section unused

Zero posts published. Looks empty to visitors.

### 7.6 Commentary placeholder on all live posts

Active work item — targeting 2 weeks of backfilled daily commentary.

---

## 8. Priority Backlog

### ✅ Complete (1–9)
1. Chart style overhaul — dark navy palette, annotations, watermark
2. Congo typography + colour identity — IBM Plex Serif, JetBrains Mono, teal accent
3. EirGrid wind + demand integration — new `/api/chart/` endpoint
4. Price duration curve + peak/off-peak spread — two new chart types
5. Stat bar shortcode — 4 metric chips at post header
6. BESS dispatch simulation — `bess.py` module, chart, scaffold integration
7. BST/GMT timezone fix — `zoneinfo.ZoneInfo("Europe/Dublin")`
8. Automated SEMO download — `fetch_semo()` via SEMOpx REST API
9. Extended post statistics — median, std dev, periods above €150/€200, peak/off-peak breakdown, wind range. Surfaced in Market Snapshot table and as inline stat callouts below each chart.

### ✅ 7.2 Git binary growth — HTML charts removed; PNG blob infrastructure ready
HTML chart files are gitignored and removed from index. PNG upload/download via Vercel Blob is implemented and wired into the pipeline. One manual step remaining: create a Blob store and follow the §7.2 activation steps above.

### Remaining (10–13)
10. **Homepage hero** — sparkline of last 7 days mean price
11. **Post card redesign** — mean price on list page cards (Congo partial override)
12. **Carbon intensity overlay** — EirGrid CO₂ intensity (gCO₂/kWh) per half-hour
13. **GB interconnector data** — Elexon BMRS, I-SEM vs GB daily comparison

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
| Charts output | `site/static/charts/YYYY-MM-DD/` (one folder per date, PNG + HTML) |
| Raw data | `data/` (gitignored) |
| Activity log | `blog.log` |
| Editor | VS Code (`code <file>`) |
| OS | Ubuntu |

---

## 12. The Bigger Picture

The pipeline is complete. 5 charts per post, fully automated data fetching, BESS simulation, professional site design. **What the blog needs now is content.**

Daily posts with real commentary — explaining why prices moved, what the wind data means, what the BESS numbers say about market conditions — is what turns an impressive Python project into a genuine career asset. Hiring managers in energy analysis, flexibility, trading, and consulting will find this blog. A candidate publishing daily I-SEM price analysis with BESS dispatch simulation, written by someone who clearly understands the market, is rare.

**The pipeline is done. Write.**
