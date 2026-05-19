# Irish Energy Market Blog — Full Project History

## Who This Is For

Eoin, Cork-based energy broker and founder of INIS Energy (CRU-regulated). Background in computer science (React, Laravel, Python). Career goal: transition into specialist energy roles — top targets are flexibility/demand response (GridBeyond Cork) and energy data (ESB Networks). Five ranked career paths: Flexibility/DR, BESS Revenue Optimisation, Energy Market Consulting, Energy Data/Grid Intelligence, AI Forecasting/VPPs.

---

## What the Blog Is Supposed to Be

A simple, clean energy market blog — essentially a personal Substack — where Eoin publishes daily and weekly posts about the Irish electricity market (I-SEM). Each post features Python-generated charts and data analysis with some written commentary. The blog serves four purposes simultaneously:

1. **Public portfolio** — Proves to hiring managers (GridBeyond, ESB Networks, VIOTAS) that Eoin understands Irish energy markets and can work with real market data.
2. **Daily learning** — Writing commentary forces daily engagement with market dynamics (wind-price correlation, demand shape, price drivers).
3. **Python skill-building** — The data pipeline (fetching, cleaning, charting SEMO data) is itself a demonstrable project.
4. **SEO and visibility** — Irish energy market content is a low-competition niche; consistent posts rank quickly.

The content model is a blend of:
- **Daily market briefings** — Templated, data-driven posts with DAM price charts, key stats, and 2-3 paragraphs of commentary. Quick to produce once the pipeline works.
- **Weekly deep-dives** — Longer analysis pieces (800-1200 words) on topics like wind cannibalisation, flexibility value, cross-market comparisons.
- **Benchmarking/comparison** content — Ireland vs GB, week-on-week, seasonal patterns.

Eoin's brother (also in energy) will join later as a co-author on the same platform.

The blog ties into a broader learning programme ("Enerriculum") and a LinkedIn content strategy where chart images are posted natively with insight snippets, driving traffic back to the blog.

---

## What Was Actually Built

### Tech Stack
- **Site generator:** Hugo (static site generator — markdown files become HTML pages)
- **Theme:** Congo (replaced PaperMod mid-project for better design — card layouts, ocean colour scheme, dark/light toggle, search)
- **Hosting:** Vercel (auto-deploys from GitHub on every push, free)
- **Repo:** github.com/treacy998/irish-energy-blog (public)
- **Live URL:** irish-energy-blog.vercel.app
- **Python pipeline:** pandas + matplotlib for data processing and chart generation
- **Environment:** Python venv at ~/dev/blog/irish-energy-blog/venv

### Project Structure
```
~/dev/blog/irish-energy-blog/
├── pipeline/
│   ├── run_daily.py          — one-command entry point, prompts for title
│   ├── process.py            — parses real SEMO CSV format → clean DataFrame
│   ├── charts.py             — generates PNG charts
│   ├── scaffold.py           — creates markdown post from data + charts
│   ├── fetch.py              — data download stubs (not yet implemented)
│   └── generate_sample_data.py — synthetic test data generator
├── site/
│   ├── config/_default/      — Hugo config (split across 4 files)
│   │   ├── hugo.toml         — base config, URLs, permalinks
│   │   ├── params.toml       — theme params, colour scheme, layout
│   │   ├── languages.en.toml — site title, author, social links
│   │   └── menus.en.toml     — navigation menu
│   ├── content/
│   │   ├── daily/            — daily briefing .md posts
│   │   ├── weekly/           — weekly analysis .md posts (empty)
│   │   └── about.md
│   ├── static/charts/        — generated PNGs
│   └── themes/congo/         — git submodule
├── data/                     — market CSVs (gitignored)
├── venv/                     — Python virtual environment (gitignored)
├── blog                      — shell script entry point (broken — see below)
├── vercel.json
└── README.md
```

### The Python Pipeline — What Works

The pipeline successfully:
- Parses real SEMO ETS Market Results CSVs (unusual format: semicolon-delimited, European decimal commas, wide/transposed layout with 48 values per row, metadata header rows)
- Extracts DAM prices from the "Index prices EUR" block
- Derives the delivery date from the auction date + 1 day
- Converts UTC timestamps to Irish time (currently a simple +1h offset — correct April-October only, breaks in winter)
- Generates three chart types: DAM price profile with peak/min markers, price-vs-wind dual-axis overlay (skipped without EirGrid data), 7-day comparison overlay
- Scaffolds a markdown blog post pre-filled with stats table, chart image references, and a commentary placeholder
- Prompts for a custom post title with a sensible default
- Auto-detects the most recent SEM-DA file in data/ (rejects IDA1/IDA2/SEM-GB files)

Running `python pipeline/run_daily.py` works end-to-end: drop a SEMO CSV in data/, run the command, get charts and a scaffolded post.

### The Hugo Site — What Exists

The Hugo site with Congo theme is configured and deployed to Vercel. It has:
- Ocean colour scheme, dark/light mode, card layout, built-in search
- SEO metadata, Open Graph, RSS feed, semantic URLs
- Daily and weekly content sections with navigation
- An about page
- Vercel auto-deploy on git push (this works)

### What Doesn't Work / What's Broken

**Hugo local preview is completely broken.** This is the main blocker. Running `hugo server -D` (whether directly, via a Makefile, or via the ./blog shell script) causes the terminal to hang with no visible output. Hugo appears to build successfully (build logs show when forced with --logLevel info) but the server startup message never appears and it's unclear whether localhost:1313 actually serves anything. Multiple approaches have been tried:
- Direct command: `cd site && ~/.local/bin/hugo server -D` — hangs
- Makefile wrapper — hangs
- Shell script (./blog) with various flags (--logLevel info, --logLevel error, --disableFastRender, --navigateToChanged) — hangs
- The terminal just sits there with no output and no URL. Ctrl+C kills it.

This has never been tested: **opening localhost:1313 in a browser while Hugo appears to hang.** Hugo may actually be serving fine with its output suppressed. This is the first thing to try.

If that doesn't work, the issue may be Hugo v0.146.0's TUI startup screen not rendering in certain terminal environments, or a port conflict from a previous Hugo process.

**The ./blog shell script has had persistent issues:**
- First version used `echo -e` which didn't work in Eoin's shell — menu text was invisible
- Second version fixed this with `printf` but the preview command still hangs (same underlying Hugo issue)
- The script concept is sound but needs the Hugo problem solved first

**The blog doesn't feel like a blog yet.** There are sample/test posts but no real published content. The site exists but looks empty.

**No EirGrid wind data integration.** The price-vs-wind chart is skipped because wind generation data isn't being fetched. Only SEMO DAM price data works currently.

**No automated data fetching.** You still manually download CSVs from the SEMO website. fetch.py is stubs only.

**UTC/Irish time offset is a hack.** The +1h offset works April-October but will break in winter. Needs proper timezone handling with zoneinfo.ZoneInfo("Europe/Dublin").

---

## The Core Problem — Honest Assessment

The blog was over-engineered relative to Eoin's actual goal. The vision was "a simple blog where I post charts and commentary" but the implementation became a complex system with Hugo, a custom Python pipeline, shell script wrappers, git workflows, and Vercel deployment — with a local preview that doesn't even work.

The question raised mid-project was valid: "Is Substack not much easier? Make the graphs elsewhere and just add them in as images?" The answer is yes, Substack would be dramatically simpler for the publishing side. The Python pipeline for generating charts is valuable and works. The Hugo/Vercel infrastructure is where the friction lives.

The ideal outcome is one of:
1. **Fix Hugo** — solve the preview hang, and the existing setup works. The pipeline is solid; Hugo is the only broken piece.
2. **Switch to Substack or similar** — keep the Python pipeline for chart generation, but publish on a platform with zero infrastructure overhead. Lose some SEO control but gain immediate usability.
3. **Simplify the Hugo setup** — strip out the complexity, maybe use a simpler theme, and make sure the basics actually work before adding features.

---

## What's on the Horizon (Not Yet Built)

- EirGrid wind/generation data integration (Smart Grid Dashboard API)
- Automated SEMO data fetching (fetch.py implementation)
- GitHub Actions for daily automation
- DST-aware timezone conversion (October)
- More chart types: price duration curve, monthly heatmap, rolling averages
- Interactive Plotly charts replacing static PNGs
- Email newsletter via RSS feed
- Brother joining as co-author
- Portfolio projects: FASS dispatch analysis (targeting GridBeyond), CER smart meter analysis (targeting ESB Networks)

---

## SEMO Data Format Reference

The ETS Market Results CSV (MarketResult_SEM-DA_PWR-MRC-D+1_*.csv) is not a standard CSV:
- Delimiter: semicolon (;)
- Decimals: European comma (161,70 = 161.70)
- Layout: wide/transposed — 48 values across one row
- Rows 1-7: metadata (auction name, date, FX rate, market)
- Data: repeating 3-row blocks (header / 48 timestamps / 48 values)
- Key block: "Index prices;30;EUR" = DAM prices in €/MWh
- Timestamps: UTC. SEM day runs 22:00Z to 21:30Z (23:00-22:30 Irish)
- Delivery date: auction date + 1 day
- Only SEM-DA files work. SEM-IDA1, SEM-IDA2, SEM-GB are different markets.

---

## Key Preferences and Constraints

- Eoin strongly prefers concise, punchy output over detailed prose
- Frontend coding effort should be minimised — bandwidth is for Python and energy content
- The blog must be simple to run day-to-day — no memorising terminal commands
- Substack-like simplicity is the benchmark for usability
- Phase A before Phase B — manual process first, automate once proven
- Currently using Claude Code alongside Claude chat for implementation work
- Local development environment: Ubuntu, ~/dev/blog/irish-energy-blog, Python 3 venv, Hugo v0.146.0 at ~/.local/bin/hugo

---

## Summary for New Chat

The Python data pipeline works and generates good charts from real SEMO data. The Hugo blog site exists and deploys to Vercel but the local preview has never worked (terminal hangs). The whole setup is more complex than it needs to be. The priority is either fixing Hugo preview or reconsidering the platform choice entirely. The blog has zero published real-data posts — the pipeline works but the publishing workflow is blocked by infrastructure friction.
