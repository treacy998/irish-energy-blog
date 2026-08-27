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

    python pipeline/audit/audit_posts.py

Ground truth source: data/history.db (market_prices, system_conditions).
Falls back to skipping dates not yet in the store (prints to stderr).
"""

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

DB_PATH = ROOT / "data" / "history.db"
POSTS_DIR = ROOT / "site" / "content" / "daily"
REPORT_PATH = ROOT / "audit_report.csv"

# Canonical SEM-DA period order: period 1 = 23:00 the previous evening.
# Used to check discharge-after-charge structurally, not by clock-time string.
PERIOD_ORDER = []
h, m = 23, 0
for _ in range(48):
    PERIOD_ORDER.append(f"{h:02d}:{m:02d}")
    m += 30
    if m == 60:
        m = 0
        h = (h + 1) % 24


def period_index(t: str) -> int | None:
    return PERIOD_ORDER.index(t) if t in PERIOD_ORDER else None


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

    df = pd.DataFrame(price_rows, columns=["Period", "StartTime", "DAMPrice_EUR_MWh"])
    df["DeliveryDate"] = pd.Timestamp(d)

    summary = daily_summary(df, d)
    bess_result = simulate_bess(df)

    cond_rows = conn.execute(
        "SELECT start_time, wind_mw, demand_mw, wind_pct FROM system_conditions WHERE date=? ORDER BY period",
        (ds,),
    ).fetchall()
    if cond_rows:
        cdf = pd.DataFrame(cond_rows, columns=["StartTime", "WindMW", "DemandMW", "WindGeneration_pct"])
        merged = pd.merge(df, cdf, on="StartTime", how="left")
        if merged["WindGeneration_pct"].notna().any():
            summary["wind_pct_mean"] = round(merged["WindGeneration_pct"].mean(), 1)
            summary["wind_pct_min"] = round(float(merged["WindGeneration_pct"].min()), 1)
            summary["wind_pct_max"] = round(float(merged["WindGeneration_pct"].max()), 1)
            summary["demand_mean_mw"] = round(merged["DemandMW"].mean(), 0)

    gt = dict(summary)
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
            nm = re.search(r"(\d+)\s+of\s+48", "|".join(cells))
            if nm:
                out.append(("table:snapshot", "periods_above_150", float(nm.group(1)), i))
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


def audit_post(post_path: Path, gt: dict) -> list:
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
            note = "" if abs(delta) <= 1.0 else "MISMATCH"
            results.append([surface, field, val, computed, delta, ln, note])

    # Structural check: does a published (charge_start, discharge_start) pair,
    # from any surface, respect discharge-after-charge in array-index order?
    charge_starts = [(s, v, ln) for s, f, v, ln in findings if f == "bess_charge_start"]
    discharge_starts = [(s, v, ln) for s, f, v, ln in findings if f == "bess_discharge_start"]
    for cs, cv, cln in charge_starts:
        ci = period_index(cv)
        for ds, dv, dln in discharge_starts:
            di = period_index(dv)
            if ci is not None and di is not None and di < ci + 4:
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
    if not DB_PATH.exists():
        print(f"No {DB_PATH} — run pipeline/store.py first.", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    all_rows = []
    skipped = []

    for post_dir in sorted(POSTS_DIR.iterdir()):
        if not post_dir.is_dir():
            continue
        try:
            d = date.fromisoformat(post_dir.name)
        except ValueError:
            continue
        idx = post_dir / "index.md"
        if not idx.exists():
            continue

        gt = load_ground_truth(conn, d)
        if gt is None:
            skipped.append(post_dir.name)
            continue

        for row in audit_post(idx, gt):
            all_rows.append([d.isoformat()] + row)

    conn.close()

    with open(REPORT_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "surface", "field", "published", "computed", "delta", "line", "note"])
        w.writerows(all_rows)

    flagged = [r for r in all_rows if r[-1]]
    posts_with_issues = sorted({r[0] for r in flagged})

    print(f"Audited {len(list(POSTS_DIR.iterdir())) - len(skipped)} posts against {DB_PATH}")
    if skipped:
        print(f"Skipped (no ground truth in DB): {len(skipped)} — {skipped}")
    print(f"Total extracted figures checked: {len(all_rows)}")
    print(f"Flagged rows: {len(flagged)}")
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
    print(f"Full report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
