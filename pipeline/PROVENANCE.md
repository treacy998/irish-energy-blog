# Data Provenance Log

Verification record for published daily briefings — did the pipeline fetch
real data, or fall through to a default/cached/sample path. See
`run_daily.py`'s stale-data gate (aborts if `delivery_date != expected_date`)
for the automated half of this check; this log is the manual half.

## 2026-08-20 — Backfill batch 2026-08-12 → 2026-08-19 (commit 67273b3)

**Trigger**: 8 posts published in one commit after a gap — the backfill path
(`run_daily.py --date`, looped) had not been exercised before and shares code
with `find_latest_data_file()`, which has a known silent-fallback-to-sample
precedent elsewhere in this codebase (comparison engine defaulting to
hardcoded rates on empty query).

**Code review** (`pipeline/run_daily.py`, `fetch.py`, `backfill_cards.py`):
- `run_daily.py` has an explicit validation gate (lines 120–126): if the
  loaded file's `DeliveryDate` doesn't match the requested/expected date, it
  aborts before scaffolding the post rather than silently publishing stale
  cached or sample data.
- `fetch.py`'s EirGrid fetcher fails closed — returns `None` on any error,
  never fabricates rows. `fetch_semo` raises `FileNotFoundError` on empty API
  results.
- `find_latest_data_file()`'s sample-CSV fallback exists but is only reached
  when `fetch_semo` raises *and* no dated file exists in `data/` — for a
  backfill run with an explicit `--date`, the stale-date gate would catch a
  sample-CSV date mismatch before publish. No `fillna`/`random`/`mock` in the
  code path that produces post content.
- No fallback risk found in this batch's generation path.

**Raw data cache**: confirmed. `data/MarketResult_SEM-DA_*.csv` files for
trade dates 2026-08-11 through 2026-08-18 (→ delivery dates 08-12–08-19) are
present, downloaded 2026-08-20 13:34–13:35, immediately preceding the 13:40
commit. These are the actual SEMOpx API responses, archived — full
provenance for DAM prices. **Gap**: EirGrid wind/demand responses are *not*
persisted to disk anywhere (`fetch.py` returns an in-memory DataFrame that's
discarded after scaffolding) — only the SEMOpx side has a raw-response
archive. Fix tracked below.

**Cross-source check — 2026-08-17**:
- DAM prices: all 48 half-hourly values in
  `site/content/daily/2026-08-17/index.md` compared cell-by-cell against
  `data/MarketResult_SEM-DA_PWR-MRC-D+1_20260816100000_20260816105501.csv`
  (the raw SEMOpx download). Exact match, all 48 periods.
- Wind %: post's 48 half-hourly wind percentages compared against a live
  re-fetch of EirGrid's Smart Grid Dashboard API for 2026-08-17 (source
  wasn't archived, so re-queried live instead). Exact match, all 48 periods,
  incl. mean 23.7%, range 8.2%–48.0%.
- Headline figures (mean €192.2, peak €248.00 @ 09:30, min €162.12 @ 15:30,
  spread €85.88) all verified against the same raw CSV.
- **Verdict: match.**

**Spot-check — 2026-08-19**: mean/peak/min/spread from the post
(€173.6 / €220.93 / €146.15 / €74.78) recomputed independently from
`MarketResult_SEM-DA_PWR-MRC-D+1_20260818100000_20260818105501.csv`.
Computed mean €173.597 ≈ €173.6, peak/min/spread exact. **Match.**

**Internal consistency**: headline means across the 8 posts (€171.8, 196.14,
182.7, 172.72, 168.38, 192.2, 168.19, 173.6) are non-monotonic, unrounded,
and show real day-to-day volatility — not clustered or suspiciously smooth.
Week-compare charts are built by combining the same cached raw CSVs
(`charts.py` — "Combine all available data files so the week-compare has
history"), so cross-post consistency with the pre-gap 2026-08-10 post
(€165.78 mean) is structural, not independently regenerated.

**Checked by**: Claude (Sonnet 5), at Eoin's request.

**Verdict: real data, not fallback/synthetic.** Posts stay live and are
cleared to feed the quarterly pillar / `compare-business-electricity-rates-
ireland` remediation item.

**Outstanding action**: archive raw EirGrid API responses to disk alongside
the SEMOpx CSVs (same pattern as `fetch_semo`'s `data/` cache) so this
verification doesn't require a live re-fetch next time.
