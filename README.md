# Irish Energy Market Blog

Daily data-driven analysis of Ireland's I-SEM wholesale electricity markets.

Built with Python (pandas, matplotlib) and Hugo. Data sourced from SEMO and EirGrid.

## What's Here

```
pipeline/          Python scripts for data fetching, processing, and chart generation
site/              Hugo static site — blog posts, config, templates
data/              Raw market data (gitignored — download your own from SEMO)
```

## Quick Start

### 1. Set up Hugo

```bash
# macOS
brew install hugo

# Linux
sudo apt install hugo

# Verify
hugo version
```

### 2. Install the PaperMod theme

```bash
cd site
git submodule add https://github.com/adityatelange/hugo-PaperMod themes/PaperMod
```

### 3. Install Python dependencies

```bash
pip install pandas matplotlib
```

### 4. Generate sample data and test the pipeline

```bash
cd pipeline
python generate_sample_data.py     # creates data/semo_dam_sample.csv
python scaffold.py 2026-04-16      # generates charts + scaffolds a daily post
```

### 5. Preview the site locally

```bash
cd site
hugo server -D    # -D includes draft posts
# Open http://localhost:1313
```

### 6. Deploy

Push to GitHub. Connect the repo to [Netlify](https://www.netlify.com/) or [Vercel](https://vercel.com/) — set the build command to `cd site && hugo` and publish directory to `site/public`.

## Daily Workflow

```bash
# 1. Download yesterday's DAM results from sem-o.com → data/
# 2. Generate charts and post template
python pipeline/scaffold.py

# 3. Open site/content/daily/YYYY-MM-DD.md, write commentary
# 4. Preview locally
cd site && hugo server -D

# 5. Commit and push — site auto-deploys
git add . && git commit -m "Daily briefing YYYY-MM-DD" && git push
```

## Data Sources

- [SEMO Market Data](https://www.sem-o.com/market-data/) — Day-Ahead Market results
- [EirGrid Smart Grid Dashboard](https://www.smartgriddashboard.com/) — Generation, demand, wind
- [CRU](https://www.cru.ie/) — Regulatory documents and consultations

## Authors

- **Eoin** — Energy broker, INIS Energy (Cork)

## License

Blog content: © Eoin, all rights reserved.
Code: MIT License — use the pipeline however you like.
