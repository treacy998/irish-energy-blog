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
