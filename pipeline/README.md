# Pipeline conventions

Path and date-semantics decisions that aren't obvious from the code, kept
here so they don't have to be rediscovered.

## Content layout

Both `daily` and `weekly` posts are Hugo page bundles — one directory per
post under `site/content/<section>/<date>/`, containing only `index.md`.
Chart PNGs are **not** page resources; they live separately under
`site/static/charts/<section>/<date>/` and are referenced from front matter
and body by absolute path (`/charts/weekly/2026-08-16/...`). This is
deliberate, not an oversight — it matches how `pipeline/charts.py` already
writes daily charts, and keeps the chart-writing code identical between the
two sections.

`site/content/weekly/2026-08-16.md` (flat, no directory) was published for
one day before being converted to `2026-08-16/index.md` to match. If you're
reading this before that fix landed, the flat form was a mistake, not a
second supported convention.

## Weekly filename/date = last day of coverage, not first

`pipeline/weekly.py` names the weekly draft and sets `date:` to the
**Sunday** the ISO week ends on, not the Monday it starts. So the week of
10–16 August 2026 is `weekly/2026-08-16.md`, and the following week (17–23
August) will be `weekly/2026-08-23.md`. This is consistent but is the
opposite of the more obvious "name it by the Monday" guess — if you're
about to write a script that reads or generates these filenames, check this
first.

`date:` in front matter also drives the URL (`permalinks.weekly` in
`hugo.toml` uses `:year/:month/:slug`) and RSS pubDate. A post covering the
week ending 16 August, published on 21 August, will show up in feeds and
structured data as five days old at launch. Harmless as a one-off. If
publish lag from coverage-end becomes routine (e.g. the roundup regularly
goes out a week late), reconsider adding a separate `date` (publish) vs.
`coverage_end` (content) field — not done yet because it touches the RSS
template and permalink behaviour, which wasn't worth the risk for a
one-post fix.

## Automated daily run (GitHub Actions)

`.github/workflows/daily.yml` runs `pipeline/ci_daily.py`, which does one unattended daily post. It is
`workflow_dispatch` only for now; the two intended schedules (06:30 and 18:30 UTC) are commented out in
the file. Both fall after Irish midnight and before the next one in summer and winter, and the target
date is computed by the Irish calendar in Python, so UTC vs IST does not matter.

- **No-op retry.** If `site/content/daily/<date>/index.md` is already in the checkout, the run exits 0
  before any network call. A second attempt after a morning success changes nothing and commits nothing.
- **Fail closed.** `run_daily.py` is called unchanged, so its stale-data gate and `fetch.py`'s fail-closed
  paths decide. Any nonzero exit fails the job and nothing is committed.
- **No wind, no post (default).** EirGrid's demand feed is intermittently empty and `run_daily.py` carries
  on without wind, leaving a one-hour wind stub on the Price vs Wind chart. CI treats that as a failure
  and keeps nothing, so the evening attempt can retry. In testing about half of the days needed a second
  attempt. Dispatch with `allow_no_wind` to publish anyway.
- **Source of truth.** For published figures, the raw files the CI run fetched are the record, not your
  local `data/history.db`. The store is derived and can lag or have gaps; the audit compares posts to it,
  so a flag on a CI-written post usually means the local store needs `store.py --heal` / `--rebuild-conditions`.
- **Raw archive repo.** `data/` is gitignored and a runner is ephemeral, so each run's raw SEMOpx CSVs and
  EirGrid JSON go to a separate private repo (default `treacy998/inis-energy-data`, branch `main`),
  mirroring `data/` so `sha256sum -c pipeline/data-manifest.sha256` works from its root
  (`pipeline/raw_archive.py`). It is append-only: a file already there is never replaced, and a
  differing one fails the run. Order in the job: restore history from it, generate, build and check,
  **push raw, then push content**; if the raw push fails the content is never pushed. A run that dies
  between the two leaves raw files without a post. The retry does not race them: `--restore-raw` also
  restores the target day's own SEMOpx file and EirGrid archive, and `ci_daily.py` runs
  `run_daily.py --prefer-archived-raw`, which generates from the archived bytes and fetches an area live
  only if nothing is archived for it. The retry's post is byte-identical and the raw push finds every
  file already there (`pipeline/test_ci_retry.py` simulates the death with a local bare repo). One-off seeding from a local `data/`:
  `python pipeline/raw_archive.py seed` (about 380 MB, `history.db` excluded), then `verify` clones fresh
  and runs `sha256sum -c` against the manifest. `verify` reports and skips any entry that is not raw data.
- **History.** A run restores the 6 prior days of SEMOpx files and the previous day's EirGrid archive
  from the raw repo (`--restore-raw`; failure fails the run), and fetches from SEMOpx whatever is still
  missing. A missing day fails the run: the 7-day chart would otherwise be quietly wrong.
- **Manifest.** `pipeline/update_manifest.py` merges new raw-file checksums into
  `pipeline/data-manifest.sha256` and never removes an entry. A recorded file whose hash changed aborts
  the run. `sha256sum -c --ignore-missing pipeline/data-manifest.sha256` checks what a local `data/` holds.
- **Local store.** CI does not update `data/history.db` or run `audit_posts.py`; both need the local
  store. Run the nightly store job and the audit locally as before. Until `--heal` has filled demand,
  the audit flags CI-written posts for days the local store holds no demand for.
- **Render check.** The job builds Hugo and checks that the new page has `noindex, follow` and a weekly
  pointer exactly when a weekly covers its day (`pipeline/ci_verify_render.py`).
- **Secrets and variables.** None for the fetch (SEMOpx and EirGrid are unauthenticated). The content
  push uses the built-in `GITHUB_TOKEN` (`contents: write`). To create in the blog repo (Settings >
  Secrets and variables > Actions): secret `DATA_REPO_TOKEN` (fine-grained PAT, the raw repo only,
  Contents read and write); variables `GIT_COMMIT_NAME` and `GIT_COMMIT_EMAIL` (your GitHub-verified
  identity: commits are authored as it, because Vercel may refuse unknown authors), and optionally
  `DATA_REPO` (`owner/name`). The job fails first thing if the token or identity is missing.
  `BLOB_READ_WRITE_TOKEN` is not needed (PNGs are committed).

### Schedules only run from the default branch

GitHub reads `schedule:` triggers from the workflow file on the default branch (`master`) only, and
`workflow_dispatch` appears in the Actions tab only once the file is there. Nothing on a feature branch
runs on a timer, and merging is what switches a schedule on (the daily one is commented out until then).

### Scheduled workflows are disabled after 60 days of repo inactivity

GitHub turns off `schedule:` triggers on a repository with no activity for 60 days, with no failure
and no email. Nothing then runs the daily job. `deadman.yml` is a separate workflow (Monday 09:00 UTC
and `workflow_dispatch`) that does not use `daily.yml`'s outcome: it checks that each of the last 7
days (Irish calendar) has `site/content/daily/<date>/index.md` and fails if any is missing, which
sends the usual failed-run email. A silent stop of the daily job shows up as a red deadman on the next Monday.

Limits: deadman is itself a scheduled workflow, so it is disabled by the same rule. It only helps while
something else keeps the repo active, for example the manual commits you make when it fires. It also
cannot tell a stopped schedule from a failing run; both look like missing posts. If you see no deadman
run for a week, open the Actions tab and re-enable the workflows. Whether commits pushed by
`GITHUB_TOKEN` count as activity for the 60-day rule has not been verified.

### Weekly roundup

`weekly.py` directories are named by the last day of the ISO week (Sunday), like the post's `date:`;
`week_start` stays in the front matter. Before building, it checks the week for gaps (a day without all
its prices, or too little demand for a wind %) and, if any, refreshes the store through `scripts/nightly.sh`
(lock, backup, read-only afterwards), at most 3 times 2 minutes apart, then re-checks. The completeness
check itself is unchanged: a week whose final day is still short is refused. The 12 Oct refusal was a
missing Sunday price, not incomplete demand: the 06:30 and 07:30 cron jobs did not fire (the machine was
suspended) so the store was still at 9 Oct.

### Data licence

The EirGrid Group Open Data Licence (smartgriddashboard.com/ni/open-data-license) names SEMO and SEMOpx
and permits copying, publishing and distributing the data on condition of the statement "Supported by
EirGrid Group Data". It can be revised without notice. This is a note, not legal advice.
