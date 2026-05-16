# Irish Energy Blog — Working Guide

This is your complete reference for running the blog day to day. Read it once
end to end, then keep it handy. Everything you need to know is here.


---


## What this blog is

The blog publishes daily market briefings and occasional deeper analysis of the
Irish wholesale electricity market (I-SEM). Every daily post is built around
real price data downloaded from SEMO (the Single Electricity Market Operator).
Python scripts process the data, generate charts, and scaffold a markdown post
that you then open, write the commentary for, and publish.

The site itself is built with Hugo, a static site generator. There is no
database, no login page, no CMS to learn. Posts are markdown files. Charts are
PNG images. Publishing is a git push. Vercel builds and hosts the site
automatically when you push.

The whole system is controlled from one command: ./blog


---


## Before you start — one-time setup

These things should already be done. This section is here so you know what
exists and why.

The project lives at:   ~/dev/blog/irish-energy-blog/

Inside that folder you will find:

  blog            The command you run every day. This is the entry point.
  pipeline/       Python scripts that do all the data processing.
  site/           The Hugo website — content, themes, config, static files.
  data/           Where you drop SEMO CSV files before running the pipeline.
  venv/           A Python virtual environment with all dependencies installed.
  blog.log        A log file that records everything the CLI does, with timestamps.
  GUIDE.md        This file.

Hugo is installed at ~/.local/bin/hugo (version 0.146.0 extended).

The site is deployed at https://irish-energy-blog.vercel.app via Vercel. Every
time you push to git, Vercel rebuilds and publishes the site automatically.
You never interact with Vercel directly.

Git remote is already configured. Pushing to master = publishing to the web.


---


## The daily workflow

On a normal day, the sequence is:

  1. Download today's SEMO data file and drop it in data/
  2. Run ./blog → choose option 1 (New daily briefing)
  3. Write your commentary in the post that opens in VS Code
  4. Run ./blog → choose option 4 (Preview) to check it looks right
  5. Run ./blog → choose option 5 (Deploy) to publish

That is the whole workflow. Each step is explained in detail below.


---


## Step 1 — Getting the SEMO data

The pipeline needs a Day-Ahead Market results file from SEMO. This is a CSV
file that SEMO publishes every day after the DAM auction clears (usually by
midday). You download it manually and drop it in the data/ folder.

Where to download it:

  Go to sem-o.com
  Navigate to: Market Data → Dynamic Reports
  Look for: ETS Market Results
  Filter for: SEM-DA (Day-Ahead Market), the most recent auction
  Download the CSV file

The file will have a name like:
  MarketResult_SEM-DA_PWR-MRC-D+1_20260516100000_20260516105501.csv

That filename contains the auction date and time. The file covers delivery for
the following day (D+1). So a file from 16 May covers prices for 17 May.

Drop the downloaded file into the data/ folder inside the project. You do not
need to rename it. The pipeline finds the most recently modified
MarketResult_SEM-DA_*.csv file automatically.

You can have multiple files in data/ from previous days. The pipeline always
uses the newest one unless you pass a specific file path explicitly.


---


## Step 2 — Running the CLI

Open a terminal and navigate to the project folder:

  cd ~/dev/blog/irish-energy-blog

Then run:

  ./blog

You will see a menu like this:

  ╭─────────────────────────────────────────────────────╮
  │  INIS Energy Blog  ·  irish-energy-blog.vercel.app  │
  ╰─────────────────────────────────────────────────────╯

    1  New daily briefing    (run pipeline)
    2  New post               (blank, manual)
    3  Manage posts
    4  Preview site           (localhost:1313)
    5  Deploy to Vercel
    6  Quit

  Enter number:

Type a number and press Enter. That is all there is to navigation.

After any option completes, you are shown "Press Enter to return to menu" and
then taken back to the main menu. Press Ctrl+C at any point to exit cleanly.


---


## Option 1 — New daily briefing (the automated pipeline)

This is the main option you will use most days. It does everything automatically:

  - Finds the most recent SEMO CSV in data/
  - Reads and parses the 48 half-hourly price periods
  - Calculates: mean price, peak price and time, minimum price and time, price range
  - Generates charts (see the Charts section below)
  - Writes a pre-filled markdown post in site/content/daily/
  - Opens the post in VS Code so you can add your commentary

When it finishes, VS Code will open showing the new post. The post already
contains the market snapshot table, the chart images, and a commented-out
guide for what to write in the Commentary section.

If the pipeline fails, check the terminal output for the error message. The
most common cause is no SEMO file in data/, or a file that is not a SEM-DA
results file.


---


## Step 3 — Writing the commentary

The generated post has four sections:

  Market Snapshot   — a table of the key metrics, already filled in
  Price Profile     — the main chart, already embedded
  Week in Context   — the 7-day comparison chart, already embedded
  Commentary        — this is the section you write

The Commentary section contains a block comment showing what to cover:

  <!-- 
  Write 2-3 paragraphs here:
  - What drove the price shape today?
  - How does wind/demand explain the peak and trough?
  - Anything unusual compared to the week?
  - Market context: outages, interconnector, weather forecast?
  -->

Delete that comment block and replace it with your analysis. Aim for 150-300
words. Think about what a market analyst reading this for the first time would
want to know.

Useful questions to answer in the commentary:

  What time did the peak occur and what probably caused it? (morning ramp,
  evening demand, interconnector constraints, low wind?)

  How does today's price level compare to recent days? (the Week in Context
  chart makes this easy to see)

  Was there anything unusual? Very high or low prices, a flat profile, a
  sharp spike at a specific period?

  What is the wind situation? High wind days tend to produce lower prices,
  low wind days drive prices up. If you have wind generation data from
  EirGrid, reference it.

  Any market events you are aware of? Unit outages, interconnector issues,
  extreme weather, CRU consultations?

Save the file in VS Code (Ctrl+S) when done. Hugo will pick up the change
immediately when the preview server is running.


---


## Step 4 — Previewing the site

Before publishing, use the preview to check the post looks right.

Run ./blog and choose option 4 (Preview site).

The terminal will say:
  Open http://localhost:1313 in your browser.
  Press Ctrl+C to stop the server.

Open your browser and go to http://localhost:1313. You will see the full site
as it will appear when published, including your new post.

Navigate to the post and check:

  - The market snapshot table is correctly formatted
  - The charts are displaying (they should appear as images inline)
  - The commentary reads well
  - There are no obvious formatting errors

If you edit the post in VS Code while the preview server is running, the
browser will reload automatically. You can edit and preview simultaneously.

When you are happy with the post, go back to the terminal, press Ctrl+C to
stop Hugo, and then press Enter to return to the menu.


---


## Step 5 — Deploying to Vercel

Run ./blog and choose option 5 (Deploy to Vercel).

You will be asked for a commit message. A default is provided:

  Commit message [content: publish 2026-05-16]:

Press Enter to use the default, or type your own message and press Enter.

The CLI then runs three git commands in sequence:

  git add .          — stages all changed and new files
  git commit -m ...  — commits with your message
  git push           — pushes to the remote repository

Vercel detects the push and rebuilds the site automatically. It takes about
30 seconds. The new post will be live at https://irish-energy-blog.vercel.app
when the build finishes.

You do not need to do anything on Vercel's website. The push is the trigger.


---


## Option 2 — New post (manual)

Use this when you want to write a post that is not driven by the automated
pipeline. For example: a weekly analysis piece, a post about a specific market
event, an explainer about how the I-SEM works, or a post where you are using
a chart you made yourself in another tool.

When you choose option 2, you are asked:

  1. Section: Daily briefing or Weekly deep-dive?
  2. Post title: a default is suggested based on today's date, but you can
     type anything you want.

The CLI creates a markdown file with the correct frontmatter (draft: true),
and opens it in VS Code. The post starts as a blank template with a comment
showing how to embed images.

To embed a chart you made elsewhere:

  Put the PNG file in:   site/static/charts/
  Reference it in the post with:   ![Description](/charts/your-filename.png)

The post is created with draft: true, which means it will show in local
preview but will not be published to the live site until you explicitly
publish it. Use option 3 (Manage posts) to publish it when ready.


---


## Option 3 — Manage posts

This shows a table of all your posts across both sections (daily and weekly),
with their publication status:

  #   Title                                   Date        Section  Status
  1   I-SEM Daily Briefing — 15 May 2026      2026-05-15  daily    Live
  2   I-SEM Daily Briefing — 13 May 2026      2026-05-13  daily    Live
  3   I-SEM Daily Briefing — 12 May 2026      2026-05-12  daily    Live
  ...

Posts are sorted by most recently modified first.

Enter a number to select a post. You are then given four options:

  1  Edit in VS Code         — opens the markdown file in VS Code
  2  Publish now             — changes draft: true to draft: false in the file
     (or: Unpublish)         — changes draft: false to draft: true
  3  Delete permanently      — deletes the file (asks for confirmation first)
  4  Back to post list       — returns to the table without doing anything

Publish / Unpublish just edits one line in the file. It does not push anything
to git. After publishing or unpublishing a post, you still need to run option
5 (Deploy) to make the change live on the website.

Delete is permanent. There is a confirmation prompt, but there is no undo.
If you delete a post, the markdown file is gone. The charts in static/charts/
are not deleted — only the post file.


---


## The charts

The pipeline generates charts using matplotlib and saves them as PNG files in
site/static/charts/. Hugo serves them directly at the /charts/ path.

Three chart types are produced:

  DAM Price Profile (dam-YYYY-MM-DD.png)
  This is the main chart. It shows the 48 half-hourly DAM prices across the
  day as a line chart with an area fill. Peak and minimum prices are marked
  with coloured dots. A dashed line shows the daily mean. This chart is
  generated for every daily post.

  Price vs Wind (price-wind-YYYY-MM-DD.png)
  A dual-axis chart showing price on the left axis and wind generation
  percentage on the right axis. This makes the inverse relationship between
  high wind and low prices immediately visible. This chart is only generated
  if the data file includes wind generation data. Real SEMO CSVs do not
  include wind data, so this chart is currently only generated when using
  the sample data file. Adding a second data source from EirGrid would fix
  this.

  Week in Context (week-compare-YYYY-MM-DD.png)
  An overlay of the last 7 days of prices on a single chart. Earlier days
  are shown in pale blue, today's prices in a bold darker blue. This chart
  lets the reader immediately see how today's prices compare to the recent
  week. This chart is generated for every daily post, as long as the data
  file contains enough history.

All charts use a consistent colour palette: deep blue for prices, green for
wind, red for peak markers, white background. They are designed to look
clean and professional in the blog's ocean theme.


---


## Adding a chart made outside the pipeline

If you create a chart in Excel, Python, Datawrapper, or any other tool, you
can include it in any post. The process is:

  1. Export the chart as a PNG file.
  2. Name it something descriptive, like wind-analysis-may-2026.png.
  3. Copy it to:  site/static/charts/
  4. In your post markdown, add:
       ![Your description here](/charts/wind-analysis-may-2026.png)

That is all. The image will appear inline in the post at that location.

Keep filenames lowercase, use hyphens instead of spaces, no special characters.


---


## Post frontmatter explained

Every post starts with a block of metadata between --- markers. Here is what
each field does:

  ---
  title: "I-SEM Daily Briefing — 15 May 2026"
  date: 2026-05-15
  authors: ["Eoin"]
  tags: ["daily-briefing", "DAM", "I-SEM"]
  summary: "DAM prices averaged €149.91/MWh, peaking at €244.26/MWh at 22:00."
  draft: false
  ---

  title       Appears as the post headline and in the browser tab.
              Change it to whatever you want.

  date        The publication date. Hugo sorts posts by this.
              Format must be YYYY-MM-DD.

  authors     Shown on the post. Can be changed or left out.

  tags        Appear at the bottom of the post and create tag index pages.
              Use consistent tags so related posts group together.
              Common tags: daily-briefing, DAM, I-SEM, wind, interconnector,
              flexibility, weekly-analysis.

  summary     Shown on the list pages and as the post excerpt. It is also used
              as the meta description for search engines. Keep it to one
              sentence. The pipeline fills this in automatically.

  draft       true means the post is not published to the live site.
              false means it is live. Toggle this with option 3 (Manage posts)
              or edit it directly in VS Code.


---


## Writing tips for SEO

The blog's purpose includes being discoverable by people searching for
information about Irish energy markets. A few habits that help:

Use specific terms in your titles. "I-SEM Daily Briefing — 15 May 2026" is
better than "Today's market update" because it contains the date and the
market name.

Fill in the summary field with a real sentence. This becomes the description
that appears in Google search results. Make it specific: include the mean
price, any notable event, the date.

Use consistent tags. Every daily post should have at minimum: daily-briefing,
DAM, I-SEM. If there was a notable wind event, add: wind. If you discuss the
interconnector, add: interconnector. These tag pages accumulate over time and
become reference pages in themselves.

Write the commentary in plain language. Explain what the numbers mean, not
just what they are. "Prices spiked to €244/MWh at 22:00 as wind generation
fell to under 10% during the evening peak, pushing the system onto more
expensive gas units" is more useful to a reader (and to a search engine) than
"there was a price spike in the evening."

Link between posts when it is natural. If today's prices are unusually high,
you can link to a previous post that covered a similar event.


---


## Troubleshooting

Problem: ./blog does nothing or hangs immediately.
Check blog.log for any errors at startup. The most common cause is a broken
Python import. Run this to check:
  source venv/bin/activate && python pipeline/tui.py
If that produces an error message, it will tell you what is wrong.

Problem: Option 1 fails with "No SEMO CSV found in data/".
You need to download a SEMO DAM results file and put it in the data/ folder.
See Step 1 above.

Problem: Option 1 runs but the pipeline fails.
Look at the terminal output — it will show which step failed and why. Also
check blog.log for the pipeline exit code. Common cause: the SEMO file is
not a DAM results file (the filename must contain "SEM-DA").

Problem: Option 4 (Preview) starts but localhost:1313 says "site can't be reached".
The Hugo server takes a moment to start. Wait 2-3 seconds and refresh.
If it still does not work, check that Hugo is installed at ~/.local/bin/hugo
by running:  ~/.local/bin/hugo version

Problem: A chart is not appearing in the preview.
The image file must exist in site/static/charts/ and the path in the markdown
must be exactly /charts/filename.png (leading slash, no "static" in the path).

Problem: The post is showing as live in preview but not on the website.
You need to deploy. Run option 5. If you already deployed, wait 30-60 seconds
for Vercel to finish building.

Problem: Option 5 (Deploy) says "Failed" at git push.
This usually means the git remote is not reachable, or there is a conflict.
Run this in the terminal to see the full error:
  git push
Resolve any conflict and try again.

Problem: Something went wrong and I do not know what.
Run:  cat blog.log
This shows a timestamped record of everything the CLI did, including exact
paths, exit codes, and any exceptions. Share this log when asking for help.


---


## File naming conventions

Daily posts:     site/content/daily/YYYY-MM-DD.md
Weekly posts:    site/content/weekly/YYYY-MM-DD.md  (or YYYY-MM-DD-slug.md)
Charts:          site/static/charts/dam-YYYY-MM-DD.png
                 site/static/charts/week-compare-YYYY-MM-DD.png
                 site/static/charts/price-wind-YYYY-MM-DD.png
                 site/static/charts/[anything-descriptive].png

Filenames for charts should be lowercase, hyphens only, no spaces.
Post filenames for daily posts are just the date. The pipeline creates these
automatically. Manual posts from option 2 get a date-slug.md format.


---


## Sections and URL structure

Posts in site/content/daily/ appear at:
  /daily/YYYY/MM/post-slug/

Posts in site/content/weekly/ appear at:
  /weekly/YYYY/MM/post-slug/

The nav bar links to:
  /daily/     — list of all daily briefings
  /weekly/    — list of all weekly analysis posts
  /tags/      — tag index
  /about/     — about page

The homepage shows the 6 most recent posts from both sections combined,
in card layout.


---


## What does not exist yet (but could)

Automated SEMO download. Right now you download the CSV manually. The fetch.py
file has placeholder code for automating this. SEMO publishes results at
predictable URLs. This could be a one-command morning step eventually.

Wind data. The price vs wind chart only works with sample data right now
because real SEMO files do not include wind generation figures. EirGrid
publishes wind generation data through their Smart Grid Dashboard API. Adding
a second fetch step from EirGrid would unlock this chart for every real post.

Weekly posts. The template and section are set up. The workflow for writing
weekly analysis is option 2 → Weekly deep-dive. No weekly posts have been
published yet.

BST correction. The pipeline adds one hour to all timestamps to correct for
British Summer Time (UTC+1, April to October). During winter months (November
to March, when Ireland is on GMT), this correction is wrong by one hour. The
price periods will appear shifted. This is a known issue that needs a calendar-
aware fix before the clocks change in October.


---


## Quick reference card

Normal day:

  1. Download SEMO CSV from sem-o.com → drop in data/
  2. ./blog → 1 → write commentary in VS Code
  3. ./blog → 4 → check at localhost:1313 → Ctrl+C to stop
  4. ./blog → 5 → Enter to confirm commit message

Manual post:

  ./blog → 2 → choose section → enter title → write in VS Code
  → use option 3 to publish when ready → option 5 to deploy

Edit an existing post:

  ./blog → 3 → enter post number → 1 (Edit in VS Code)
  → save in VS Code → ./blog → 5 (Deploy)

Unpublish a post:

  ./blog → 3 → enter post number → 2 (Unpublish) → ./blog → 5 (Deploy)

Check what went wrong:

  cat blog.log
