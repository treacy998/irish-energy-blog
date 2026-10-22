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
- **History.** `data/` is gitignored, so a runner starts empty. It fetches the 6 prior days from SEMOpx
  (the 7-day chart needs them; a missing day fails the run) and the previous day's EirGrid archive.
- **Manifest.** `pipeline/update_manifest.py` merges the new raw-file checksums into
  `pipeline/data-manifest.sha256` and never removes an entry. A recorded file whose hash changed aborts
  the run. The raw files themselves live only on the runner, so CI-written entries cannot be re-verified
  from a fresh checkout. `sha256sum -c --ignore-missing pipeline/data-manifest.sha256` checks the rest.
- **Local store.** CI does not update `data/history.db` or run `audit_posts.py`; both need the local
  store. Run the nightly store job and the audit locally as before. Until `--heal` has filled demand,
  the audit flags CI-written posts for days the local store holds no demand for.
- **Render check.** The job builds Hugo and checks that the new page has `noindex, follow` and a weekly
  pointer exactly when a weekly covers its day (`pipeline/ci_verify_render.py`).
- **Secrets.** None for the fetch (SEMOpx and EirGrid are unauthenticated). The push uses the built-in
  `GITHUB_TOKEN` with `contents: write`. `BLOB_READ_WRITE_TOKEN` is not needed (PNGs are committed).

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
