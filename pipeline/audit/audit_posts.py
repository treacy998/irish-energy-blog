"""
audit_posts.py — Ground-truth audit of every published daily post.

Every prior correctness pass compared representations against each other
(prose vs table, delta magnitude, clock-time strings) — each found real bugs,
each was incomplete. This audit compares every published figure against a
fresh computation from source (data/history.db), which is the only check
that can't miss a bug hiding in agreement between two stale representations.

Intentionally reports everything, unclassified — triage happens after,
against the full inventory in audit_report.csv, not per-post as bugs surface.

Run after any change to process.py / bess.py / scaffold.py to see which
published posts the change invalidates:

    python pipeline/audit/audit_posts.py [--allow-skips] [--exact]

Ground truth source: data/history.db (market_prices, system_conditions).
A post with no ground truth in the store is skipped, listed with its reason,
and makes the run exit non-zero unless --allow-skips is passed — a skip is
an unaudited post, not a clean one.

audit_known.csv (post, field, published, recomputed, reason) baselines flagged
rows that are understood and accepted. A flag matches a baseline row only if
post, field, published AND recomputed value all agree, so a figure that moves
again is new, not known. Known flags are printed under "known (baselined)";
the run exits 1 only for flagged rows that are not in the baseline.

Weekly posts (site/content/weekly/<slug>/index.md) are audited when their front
matter has `week_start: YYYY-MM-DD` (a Monday). Their figures are read from the
labelled table rows in WEEKLY_ROWS below and compared with weekly_stats.weekly_summary();
pipeline/audit/fixtures/weekly_2026-09-28.md shows the format. A baseline that
weekly_summary suppresses has no ground truth, so a post that publishes a rank or
verdict from it is flagged. Weekly posts without week_start are listed, not audited.

--exact sets the tolerance to 0 for integer-valued fields (INTEGER_FIELDS:
counts, rank, percentile, days_since). Every other numeric field keeps the
default ±1.0 tolerance, which would hide an off-by-one in a count.
"""

import argparse
import csv
import re
import sqlite3
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import pandas as pd
from process import daily_summary
from bess import simulate_bess
from weekly_stats import weekly_summary
from trading_day import calendar_label_to_utc, expected_periods, period_label_indices, period_start_utc

DB_PATH = ROOT / "data" / "history.db"
POSTS_DIR = ROOT / "site" / "content" / "daily"
REPORT_PATH = ROOT / "audit_report.csv"
KNOWN_PATH = Path(__file__).parent / "audit_known.csv"
WEEKLY_DIR = ROOT / "site" / "content" / "weekly"

# Period order is index order within the trading day, taken from
# trading_day (local 23:00 start, 30-minute steps in UTC): 48 periods, or 50 /
# 46 on the clock-change days. A local label is not an index on its own — it
# repeats 01:00-02:00 on the long day — so a label maps to a list of indices.

# Integer-valued fields: with --exact these must match with tolerance 0.
# Only the periods_above_* counts are extracted from posts today; rank,
# percentile and days_since are listed so they are exact from the day an
# extractor and ground-truth value for them exist.
INTEGER_FIELDS = {"periods_above_150", "periods_above_200", "period_count", "rank", "percentile", "days_since",
                  "trailing_rank", "trailing_rank_of", "seasonal_rank", "seasonal_rank_of"}


def load_ground_truth(conn: sqlite3.Connection, d: date) -> dict | None:
    """Rebuild the DataFrames process.py/bess.py expect, from the DB, and
    compute the same summary + bess_result a fresh pipeline run would produce."""
    ds = d.isoformat()
    price_rows = conn.execute(
        "SELECT period, start_time, dam_price_eur_mwh FROM market_prices WHERE date=? ORDER BY period",
        (ds,),
    ).fetchall()
    if not price_rows:
        return None
    want = expected_periods(d)
    if [r[0] for r in price_rows] != list(range(1, want + 1)):
        raise ValueError(f"market_prices has {len(price_rows)} rows for {ds}, expected periods 1..{want}")

    df = pd.DataFrame(price_rows, columns=["Period", "StartTime", "DAMPrice_EUR_MWh"])
    df["DeliveryDate"] = pd.Timestamp(d)
    # The instant of each period comes from the trading-day mapping, not the stored label.
    df["StartUTC"] = [pd.Timestamp(period_start_utc(d, int(p))) for p in df["Period"]]

    summary = daily_summary(df, d)
    bess_result = simulate_bess(df)

    # start_utc is absent from databases built before the clock-change work.
    has_utc = "start_utc" in {r[1] for r in conn.execute("PRAGMA table_info(system_conditions)")}
    cond_rows = conn.execute(
        f"SELECT start_time, {'start_utc' if has_utc else 'NULL'}, wind_mw, demand_mw, wind_pct "
        "FROM system_conditions WHERE date=? ORDER BY period",
        (ds,),
    ).fetchall()
    if cond_rows:
        cdf = pd.DataFrame(cond_rows, columns=["StartTime", "StartUTC", "WindMW", "DemandMW", "WindGeneration_pct"])
        # Rows stored before start_utc existed: calendar date + local label gives the instant
        # (None inside a clock-change hour, so such a row is left unmatched, not guessed).
        cdf["StartUTC"] = [
            pd.Timestamp(u) if u else calendar_label_to_utc(d, lab)
            for u, lab in zip(cdf["StartUTC"], cdf["StartTime"])
        ]
        cdf = cdf.drop(columns="StartTime").dropna(subset=["StartUTC"])
        merged = pd.merge(df, cdf, on="StartUTC", how="left")
        if merged["WindGeneration_pct"].notna().any():
            summary["wind_pct_mean"] = round(merged["WindGeneration_pct"].mean(), 1)
            summary["wind_pct_min"] = round(float(merged["WindGeneration_pct"].min()), 1)
            summary["wind_pct_max"] = round(float(merged["WindGeneration_pct"].max()), 1)
            summary["demand_mean_mw"] = round(merged["DemandMW"].mean(), 0)

    gt = dict(summary)
    gt["period_count"] = want
    if bess_result:
        gt["bess_charge_mean"] = bess_result["charge_mean"]
        gt["bess_charge_start"] = bess_result["charge_start"]
        gt["bess_discharge_mean"] = bess_result["discharge_mean"]
        gt["bess_discharge_start"] = bess_result["discharge_start"]
        gt["bess_gross_revenue"] = bess_result["gross_revenue"]
        gt["bess_charge_cost"] = bess_result["charge_cost"]
        gt["bess_gross_profit"] = bess_result["gross_profit"]
        gt["bess_spread"] = bess_result["spread"]
        gt["bess_roi"] = round((bess_result["gross_profit"] / bess_result["charge_cost"]) * 100, 1) \
            if bess_result["charge_cost"] else None
    else:
        gt["bess_none"] = True

    return gt


NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
EUR_RE = re.compile(r"€(-?\d+(?:\.\d+)?)")
TIME_RE = re.compile(r"\b([0-2]\d:[0-5]\d)\b")


STATBAR_LABELS = {
    "mean": "mean_price",
    "peak": "peak_price",
    "min": "min_price",
    "spread": "price_range",
}


def extract_statbar(text: str, lineno_of):
    rows = []
    for m in re.finditer(r"\{\{<\s*statbar\s+(.*?)>\}\}", text):
        line = text[: m.start()].count("\n") + 1
        for km in re.finditer(r'(\w+)="([^"]*)"', m.group(1)):
            key, val = km.group(1), km.group(2)
            field = STATBAR_LABELS.get(key)
            if field is None:
                continue
            nm = EUR_RE.search(val) or NUM_RE.search(val)
            if nm:
                rows.append(("statbar", field, float(nm.group(1) if nm.lastindex else nm.group(0)), line))
    return rows


SNAPSHOT_LABELS = {
    "Mean DAM Price": "mean_price",
    "Median Price": "median_price",
    "Std Dev": "std_dev",
    "Peak Price": "peak_price",
    "Min Price": "min_price",
    "Price Range": "price_range",
    "Peak Avg": "peak_mean",
    "Off-peak Avg": "offpeak_mean",
    "Peak/Off-Peak Spread": "peak_offpeak_spread",
    "Wind % of Demand": "wind_pct_mean",
    "Mean Demand": "demand_mean_mw",
}


def extract_table_rows(lines):
    """Return (surface, field, value, lineno) for recognizable table rows."""
    out = []
    for i, line in enumerate(lines, start=1):
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        label = cells[0].strip("* ").strip()

        for snap_label, field in SNAPSHOT_LABELS.items():
            if label.startswith(snap_label):
                val_cell = cells[1]
                nm = EUR_RE.search(val_cell)
                if not nm:
                    nm = NUM_RE.search(val_cell)
                if nm:
                    out.append(("table:snapshot", field, float(nm.group(1) if nm.lastindex else nm.group(0)), i))

        if label.startswith("Periods above €150") or label.startswith("**Periods above €150"):
            nm = re.search(r"(\d+)\s+of\s+(\d+)", "|".join(cells))
            if nm:
                out.append(("table:snapshot", "periods_above_150", float(nm.group(1)), i))
                out.append(("table:snapshot", "period_count", float(nm.group(2)), i))
        if "Periods above €200" in label or "Above €200" in "|".join(cells):
            nm = re.search(r"Above €200.*?(\d+)\s*\(", "|".join(cells))
            if nm:
                out.append(("table:snapshot", "periods_above_200", float(nm.group(1)), i))

        # BESS dispatch table
        clean_label = re.sub(r"[*_]", "", label).strip()
        if clean_label == "Charge":
            price = EUR_RE.search(cells[1])
            t = TIME_RE.search(cells[2]) if len(cells) > 2 else None
            if price:
                out.append(("table:bess", "bess_charge_mean", float(price.group(1)), i))
            if t:
                out.append(("table:bess", "bess_charge_start", t.group(1), i))
        elif clean_label == "Discharge":
            price = EUR_RE.search(cells[1])
            t = TIME_RE.search(cells[2]) if len(cells) > 2 else None
            if price:
                out.append(("table:bess", "bess_discharge_mean", float(price.group(1)), i))
            if t:
                out.append(("table:bess", "bess_discharge_start", t.group(1), i))
        elif clean_label == "Gross profit":
            allnums = EUR_RE.findall("|".join(cells))
            if allnums:
                out.append(("table:bess", "bess_gross_profit", float(allnums[-1]), i))
        elif clean_label == "Price spread":
            price = EUR_RE.search(cells[1]) if len(cells) > 1 else None
            roi = re.search(r"ROI:\s*(-?\d+(?:\.\d+)?)", "|".join(cells))
            if price:
                out.append(("table:bess", "bess_spread", float(price.group(1)), i))
            if roi:
                out.append(("table:bess", "bess_roi", float(roi.group(1)), i))
    return out


INLINE_SUMMARY_RE = re.compile(
    r"\*\*Captured spread:\*\*\s*€(-?\d+(?:\.\d+)?)/MWh.*?"
    r"\*\*Charge:\*\*\s*€(-?\d+(?:\.\d+)?)/MWh\s*\(([0-2]\d:[0-5]\d)\).*?"
    r"\*\*Discharge:\*\*\s*€(-?\d+(?:\.\d+)?)/MWh\s*\(([0-2]\d:[0-5]\d)\)"
)


def extract_inline_summary(lines):
    """The '**Captured spread:** ... **Charge:** ... **Discharge:** ...' bold
    summary line — a third representation of the BESS result, independent of
    the table and the prose body, that no prior check in this project covered."""
    out = []
    for i, line in enumerate(lines, start=1):
        m = INLINE_SUMMARY_RE.search(line)
        if m:
            spread, charge_p, charge_t, discharge_p, discharge_t = m.groups()
            out.append(("inline_summary", "bess_spread", float(spread), i))
            out.append(("inline_summary", "bess_charge_mean", float(charge_p), i))
            out.append(("inline_summary", "bess_charge_start", charge_t, i))
            out.append(("inline_summary", "bess_discharge_mean", float(discharge_p), i))
            out.append(("inline_summary", "bess_discharge_start", discharge_t, i))
    return out


def extract_prose(lines, table_line_nos, frontmatter_range):
    """Extract candidate gross/charge/discharge mentions from prose lines only."""
    out = []
    for i, line in enumerate(lines, start=1):
        if i in table_line_nos or (frontmatter_range and frontmatter_range[0] <= i <= frontmatter_range[1]):
            continue
        if "{{<" in line or line.strip().startswith("!["):
            continue
        gross_m = re.search(r"€(-?\d+(?:\.\d+)?)\s+gross\b", line, re.IGNORECASE)
        if gross_m and "Gross before" not in line:
            out.append(("prose", "bess_gross_profit", float(gross_m.group(1)), i))
        for cm in re.finditer(r"(?<!dis)\bcharg(?:e|ed|ing)[^.]{0,40}?\b([0-2]\d:[0-5]\d)\b", line, re.IGNORECASE):
            out.append(("prose", "bess_charge_start", cm.group(1), i))
        for dm in re.finditer(r"\bdischarg(?:e|ed|ing)[^.]{0,40}?\b([0-2]\d:[0-5]\d)\b", line, re.IGNORECASE):
            out.append(("prose", "bess_discharge_start", dm.group(1), i))
    return out


def _norm(v) -> str:
    """Comparable text for a published/recomputed value (numbers by value, else as text)."""
    try:
        return repr(round(float(v), 6))
    except (TypeError, ValueError):
        return str(v)


def flag_key(post: str, field: str, published, recomputed) -> tuple:
    return (str(post), field, _norm(published), _norm(recomputed))


def load_known(path: Path = KNOWN_PATH) -> dict:
    """{flag_key: reason} from the baseline file; empty if there is none."""
    if not path.exists():
        return {}
    with open(path, newline="") as f:
        return {flag_key(r["post"], r["field"], r["published"], r["recomputed"]): r["reason"]
                for r in csv.DictReader(f)}


def compare_findings(findings, gt: dict, exact: bool) -> list:
    """[surface, field, published, computed, delta, line, note] for each (surface, field, value, line).
    Tolerance is 1.0, or 0 for INTEGER_FIELDS under --exact; strings must match exactly."""
    results = []
    for surface, field, val, ln in findings:
        computed = gt.get(field)
        if computed is None:
            results.append([surface, field, val, "N/A", "", ln, "no_ground_truth"])
            continue
        if isinstance(val, str) or isinstance(computed, str):
            match = str(val) == str(computed)
            results.append([surface, field, val, computed, "" if match else "MISMATCH", ln,
                             "" if match else "string_mismatch"])
        else:
            delta = round(val - computed, 2)
            tol = 0.0 if exact and field in INTEGER_FIELDS else 1.0
            note = "" if abs(delta) <= tol else "MISMATCH"
            results.append([surface, field, val, computed, delta, ln, note])
    return results


# (label prefix, field, kind): longest prefixes first. kinds: num = first number in the value
# cell; rank = "<n> of <m>" -> <field> and <field>_of; date = an ISO date; text = the cell, lowercased.
WEEKLY_ROWS = [
    ("Week mean (c/kWh)", "week_mean_c_per_kwh", "num"),
    ("Week mean", "week_mean", "num"),
    ("Periods above €150", "periods_above_150", "num"),
    ("Periods above €200", "periods_above_200", "num"),
    ("Median daily arb spread", "median_arb_spread", "num"),
    ("Mean wind (MW)", "wind_mw_mean", "num"),
    ("Wind coverage", "wind_coverage_pct", "num"),
    ("Rank vs trailing", "trailing_rank", "rank"),
    ("Dearest since (trailing)", "trailing_dearest_since", "date"),
    ("Cheapest since (trailing)", "trailing_cheapest_since", "date"),
    ("Price verdict (trailing)", "trailing_verdict_price", "text"),
    ("Volatility verdict (trailing)", "trailing_verdict_volatility", "text"),
    ("Rank vs seasonal", "seasonal_rank", "rank"),
    ("Dearest since (seasonal)", "seasonal_dearest_since", "date"),
    ("Cheapest since (seasonal)", "seasonal_cheapest_since", "date"),
    ("Price verdict (seasonal)", "seasonal_verdict_price", "text"),
    ("Volatility verdict (seasonal)", "seasonal_verdict_volatility", "text"),
]
ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def weekly_ground_truth(summary: dict) -> dict:
    """Flatten weekly_summary() into the field names WEEKLY_ROWS uses. A suppressed
    baseline contributes no fields, so a published figure from it has no ground truth."""
    gt = {k: summary[k] for k in ("week_mean", "week_mean_c_per_kwh", "periods_above_150", "periods_above_200",
                                  "median_arb_spread", "wind_mw_mean")}
    gt["wind_coverage_pct"] = round(summary["wind_coverage"] * 100, 1)
    for kind in ("trailing", "seasonal"):
        b = summary[kind]
        if b is None or b["suppressed"]:
            continue
        gt[f"{kind}_rank"], gt[f"{kind}_rank_of"] = b["rank"], b["rank_of"]
        gt[f"{kind}_dearest_since"], gt[f"{kind}_cheapest_since"] = b["dearest_since"], b["cheapest_since"]
        gt[f"{kind}_verdict_price"] = b["verdict_price"]
        gt[f"{kind}_verdict_volatility"] = b["verdict_volatility"]
    return gt


def extract_weekly_rows(lines) -> list:
    out = []
    for i, line in enumerate(lines, start=1):
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        label = cells[0].strip("* ").strip()
        for prefix, field, kind in WEEKLY_ROWS:
            if not label.startswith(prefix):
                continue
            val = cells[1]
            if kind == "num":
                nm = EUR_RE.search(val) or NUM_RE.search(val)
                if nm:
                    out.append(("weekly:table", field, float(nm.group(1) if nm.lastindex else nm.group(0)), i))
            elif kind == "rank":
                nm = re.search(r"(\d+)\s+of\s+(\d+)", val)
                if nm:
                    out.append(("weekly:table", field, float(nm.group(1)), i))
                    out.append(("weekly:table", field + "_of", float(nm.group(2)), i))
            elif kind == "date":
                nm = ISO_DATE_RE.search(val)
                if nm:
                    out.append(("weekly:table", field, nm.group(0), i))
            else:
                out.append(("weekly:table", field, val.strip("* ").lower(), i))
            break
    return out


def audit_weekly_post(post_path: Path, gt: dict, exact: bool = False) -> list:
    return compare_findings(extract_weekly_rows(post_path.read_text().split("\n")), gt, exact)


def weekly_start_of(post_path: Path):
    """week_start from the front matter, or None."""
    text = post_path.read_text()
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    ws = re.search(r"^week_start:\s*[\"']?(\d{4}-\d{2}-\d{2})", m.group(1), re.M)
    return date.fromisoformat(ws.group(1)) if ws else None


def audit_post(post_path: Path, gt: dict, exact: bool = False) -> list:
    text = post_path.read_text()
    lines = text.split("\n")

    fm_range = None
    fm_matches = [i for i, l in enumerate(lines, start=1) if l.strip() == "---"]
    if len(fm_matches) >= 2:
        fm_range = (fm_matches[0], fm_matches[1])

    findings = []

    for surface, field, val, ln in extract_statbar(text, None):
        findings.append((surface, field, val, ln))

    table_rows = extract_table_rows(lines)
    table_line_nos = {ln for _, _, _, ln in table_rows}
    findings.extend(table_rows)

    findings.extend(extract_inline_summary(lines))
    findings.extend(extract_prose(lines, table_line_nos, fm_range))

    results = compare_findings(findings, gt, exact)

    # Structural check: does a published (charge_start, discharge_start) pair,
    # from any surface, respect discharge-after-charge in array-index order?
    charge_starts = [(s, v, ln) for s, f, v, ln in findings if f == "bess_charge_start"]
    discharge_starts = [(s, v, ln) for s, f, v, ln in findings if f == "bess_discharge_start"]
    day = date.fromisoformat(gt["date"])
    for cs, cv, cln in charge_starts:
        cis = period_label_indices(day, cv)
        for ds, dv, dln in discharge_starts:
            dis = period_label_indices(day, dv)
            # A label on the repeated hour fits two indices; the pair is only
            # invalid if no choice of indices puts discharge >= charge + 4 periods.
            if cis and dis and not any(di >= ci + 4 for ci in cis for di in dis):
                results.append([f"{cs}+{ds}", "structural_ordering", f"charge={cv}@L{cln} discharge={dv}@L{dln}",
                                 "discharge >= charge+4 periods", "", f"{cln},{dln}", "INVALID_ORDERING"])

    if gt.get("bess_none"):
        # Ground truth says no viable cycle — any published BESS table/prose is fabricated.
        bess_table_rows = [r for r in table_rows if r[0] == "table:bess"]
        if bess_table_rows or charge_starts or discharge_starts:
            results.append(["ground_truth", "bess_none", "post has BESS content", "simulate_bess()=None", "", "",
                             "FABRICATED_NO_VALID_CYCLE"])

    return results


def main():
    parser = argparse.ArgumentParser(description="Audit published daily posts against data/history.db.")
    parser.add_argument("--allow-skips", action="store_true",
                        help="Exit 0 even if some posts had no ground truth and were skipped.")
    parser.add_argument("--exact", action="store_true",
                        help="Tolerance 0 for integer-valued fields (counts, rank, percentile, "
                             "days_since); other fields keep ±1.0.")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"No {DB_PATH} — run pipeline/store.py first.", file=sys.stderr)
        sys.exit(1)

    failed = False
    conn = sqlite3.connect(DB_PATH)
    all_rows = []
    checked = 0
    skipped = []          # (post, reason)
    no_conditions = []    # checked on prices only; wind/demand figures unverifiable

    for post_dir in sorted(POSTS_DIR.iterdir()):
        if not post_dir.is_dir():
            continue
        try:
            d = date.fromisoformat(post_dir.name)
        except ValueError:
            continue
        idx = post_dir / "index.md"
        if not idx.exists():
            skipped.append((post_dir.name, "no index.md in post directory"))
            continue

        try:
            gt = load_ground_truth(conn, d)
        except ValueError as e:
            skipped.append((post_dir.name, str(e)))
            continue
        if gt is None:
            skipped.append((post_dir.name, "no market_prices rows in history.db for this date"))
            continue

        checked += 1
        if "wind_pct_mean" not in gt:
            no_conditions.append(post_dir.name)
        for row in audit_post(idx, gt, exact=args.exact):
            all_rows.append([d.isoformat()] + row)

    weekly_unaudited = []
    if WEEKLY_DIR.exists():
        for wdir in sorted(WEEKLY_DIR.iterdir()):
            idx = wdir / "index.md"
            if not (wdir.is_dir() and idx.exists()):
                continue
            ws = weekly_start_of(idx)
            if ws is None:
                weekly_unaudited.append(wdir.name)
                continue
            try:
                summary = weekly_summary(ws, conn)
            except ValueError as e:
                skipped.append((f"weekly/{wdir.name}", str(e)))
                continue
            checked += 1
            for row in audit_weekly_post(idx, weekly_ground_truth(summary), exact=args.exact):
                all_rows.append([f"weekly:{ws.isoformat()}"] + row)

    conn.close()

    with open(REPORT_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "surface", "field", "published", "computed", "delta", "line", "note"])
        w.writerows(all_rows)

    flagged = [r for r in all_rows if r[-1]]
    known_map = load_known()
    # row layout: [date, surface, field, published, computed, delta, line, note]
    known = [r for r in flagged if flag_key(r[0], r[2], r[3], r[4]) in known_map]
    new_flags = [r for r in flagged if flag_key(r[0], r[2], r[3], r[4]) not in known_map]
    stale = set(known_map) - {flag_key(r[0], r[2], r[3], r[4]) for r in flagged}
    posts_with_issues = sorted({r[0] for r in flagged})

    print(f"checked {checked} posts, skipped {len(skipped)} (against {DB_PATH})")
    for name, reason in skipped:
        print(f"  SKIPPED {name}: {reason}")
    if weekly_unaudited:
        print(f"  {len(weekly_unaudited)} weekly post(s) have no week_start front matter and were not audited: "
              f"{weekly_unaudited}")
    if no_conditions:
        print(f"  {len(no_conditions)} checked post(s) have no system_conditions in the store, "
              f"so wind/demand figures were not verified: {no_conditions}")
    print(f"Total extracted figures checked: {len(all_rows)}")
    print(f"Flagged rows: {len(flagged)} (known/baselined {len(known)}, not in baseline {len(new_flags)})")
    print(f"Posts with at least one flagged row: {len(posts_with_issues)}")
    print()
    from collections import Counter
    field_counts = Counter(r[2] for r in flagged)
    print("Flags by field:")
    for field, n in field_counts.most_common():
        print(f"  {field:30s} {n}")
    print()
    note_counts = Counter(r[-1] for r in flagged)
    print("Flags by type:")
    for note, n in note_counts.most_common():
        print(f"  {note:30s} {n}")
    print()
    print(f"known (baselined): {len(known)} flagged row(s), from {KNOWN_PATH.name}")
    for r in known:
        print(f"  {r[0]} {r[2]:16s} published={r[3]} recomputed={r[4]}  [{known_map[flag_key(r[0], r[2], r[3], r[4])]}]")
    if stale:
        print(f"  {len(stale)} baseline row(s) no longer flagged (post corrected or data changed): "
              f"{sorted(stale)[:5]}{' ...' if len(stale) > 5 else ''}")
    print()
    print(f"not in baseline: {len(new_flags)} flagged row(s)")
    for r in new_flags:
        print(f"  {r[0]} {r[2]} published={r[3]} recomputed={r[4]} ({r[-1]})")
    print()
    print(f"Full report: {REPORT_PATH}")

    if new_flags:
        print(f"\nFAIL: {len(new_flags)} flagged row(s) not in {KNOWN_PATH.name}.", file=sys.stderr)
        failed = True
    if skipped and not args.allow_skips:
        print(f"\nFAIL: {len(skipped)} post(s) skipped without ground truth "
              f"(pass --allow-skips to accept).", file=sys.stderr)
        failed = True
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
