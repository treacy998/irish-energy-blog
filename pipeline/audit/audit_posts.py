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
verdict from it is flagged.
Every post (daily and weekly) is also checked for empty_section: a ## or ### heading with no visible body
before the next heading (HTML comments and bare "**Label:**" lines don't count; the weekly Commentary
placeholder is exempt while draft: true).
Weekly posts without week_start are listed, not audited. Every number in an audited weekly
post's "## Commentary" section must match a weekly_summary figure at the precision written, or
it is flagged unverified_commentary_number (dates, years, ordinals and HTML comments are exempt).

--exact sets the tolerance to 0 for integer-valued fields (INTEGER_FIELDS:
counts, rank, percentile, days_since) in daily posts. Every other numeric field keeps the
default ±1.0 tolerance, which would hide an off-by-one in a count. Weekly posts need no
flag: their rank, since, verdict and count fields are always compared exactly.
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
# cell; rank = "<n> of <m>" -> <field> and <field>_of; date = an ISO date; text = the cell, lowercased;
# verdict_spread = text before any "(" plus the € amount inside it as median_arb_spread.
WEEKLY_ROWS = [
    ("Week mean (c/kWh)", "week_mean_c_per_kwh", "num"),
    ("Week mean", "week_mean", "num"),
    ("Periods above €150", "periods_above_150", "num"),
    ("Periods above €200", "periods_above_200", "num"),
    ("Median daily arb spread", "median_arb_spread", "num"),
    ("Median daily spread", "median_arb_spread", "num"),
    ("Mean wind (MW)", "wind_mw_mean", "num"),
    ("Trailing median wind (MW)", "wind_mw_trailing_median", "num"),
    ("Wind coverage", "wind_coverage_pct", "num"),
    ("Rank vs trailing", "trailing_rank", "rank"),
    ("Dearest since (trailing)", "trailing_dearest_since", "date"),
    ("Cheapest since (trailing)", "trailing_cheapest_since", "date"),
    ("Price verdict (trailing)", "trailing_verdict_price", "text"),
    ("Volatility verdict (trailing)", "trailing_verdict_volatility", "verdict_spread"),
    ("Rank vs seasonal", "seasonal_rank", "rank"),
    ("Dearest since (seasonal)", "seasonal_dearest_since", "date"),
    ("Cheapest since (seasonal)", "seasonal_cheapest_since", "date"),
    ("Price verdict (seasonal)", "seasonal_verdict_price", "text"),
    ("Volatility verdict (seasonal)", "seasonal_verdict_volatility", "verdict_spread"),
]
ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def weekly_ground_truth(summary: dict) -> dict:
    """Flatten weekly_summary() into the field names WEEKLY_ROWS uses. A suppressed
    baseline contributes no fields, so a published figure from it has no ground truth."""
    gt = {k: summary[k] for k in ("week_mean", "week_mean_c_per_kwh", "periods_above_150", "periods_above_200",
                                  "median_arb_spread", "wind_mw_mean", "wind_mw_trailing_median")}
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
            # The opening rank sentence: "4th dearest of the last 14 weeks" / "Dearest of the last 14 weeks".
            m = re.search(r"(?:\b(\d+)(?:st|nd|rd|th) dearest|\b(Dearest)) of the last (\d+) weeks", line)
            if m:
                out.append(("weekly:sentence", "trailing_rank", float(m.group(1)) if m.group(1) else 1.0, i))
                out.append(("weekly:sentence", "trailing_rank_of", float(m.group(3)), i))
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
            elif kind == "verdict_spread":
                out.append(("weekly:table", field, val.split("(")[0].strip("* ").lower(), i))
                eur = EUR_RE.search(val)
                if eur:
                    out.append(("weekly:table", "median_arb_spread", float(eur.group(1)), i))
            else:
                out.append(("weekly:table", field, val.strip("* ").lower(), i))
            break
    return out


# ── Commentary numbers ───────────────────────────────────────────────────────
# Every number the author writes in a weekly post's "## Commentary" section must equal some
# weekly_summary() figure at the precision it is written with (18.42 must be 18.42, 1743 may
# be 1743.1 rounded). Dates, years, ordinals and the text of HTML comments are not figures.
COMMENTARY_HEADING_RE = re.compile(r"^##\s+Commentary\s*$")
_MONTH = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|"
          r"Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)")
_ORD = r"(?:st|nd|rd|th)"
COMMENTARY_NOT_FIGURES = [
    re.compile(r"\]\([^)]*\)"),                                    # link targets
    re.compile(r"https?://\S+"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),                           # ISO dates
    re.compile(rf"\b\d{{1,2}}{_ORD}?\s+{_MONTH}\b"),                # 5 October, 28th Sep
    re.compile(rf"\b{_MONTH}\s+\d{{1,2}}{_ORD}?\b"),                # October 5
    re.compile(rf"\b\d+{_ORD}\b"),                                 # ordinals: 4th
]
COMMENTARY_NUMBER_RE = re.compile(r"(?<![\w.])-?\d+(?:,\d{3})*(?:\.\d+)?")
# weekly_summary keys whose €/MWh values the post also shows in c/kWh (÷ 10)
_PRICE_KEYS = {"week_mean", "previous_week_mean", "median_arb_spread", "daily_means", "mean", "means",
               "median_week_mean"}


def summary_figures(summary: dict) -> list:
    """Every number weekly_summary() holds, plus the forms the post prints: €/MWh ÷ 10 as c/kWh,
    wind coverage as a percentage, the week-on-week change in percent. Absolute values: a
    spread written as 'minus €8' still matches 8."""
    out = []

    def walk(v, key=None):
        if isinstance(v, bool) or v is None or isinstance(v, str):
            return
        if isinstance(v, (int, float)):
            out.append(abs(float(v)))
            if key in _PRICE_KEYS:
                out.append(abs(v) / 10)
        elif isinstance(v, dict):
            for k, x in v.items():
                walk(x, k)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x, key)

    walk(summary)
    out += [150.0, 200.0]                           # the €/MWh thresholds behind periods_above_150 / _200
    if summary.get("wind_coverage") is not None:
        out.append(summary["wind_coverage"] * 100)
    prev = summary.get("previous_week_mean")
    if prev:
        out.append(abs(summary["week_mean"] / prev - 1) * 100)
    return out


def _matches_at_precision(token: str, figures: list) -> bool:
    text = token.replace(",", "").lstrip("-")
    decimals = len(text.split(".")[1]) if "." in text else 0
    return any(f"{f:.{decimals}f}" == f"{float(text):.{decimals}f}" for f in figures)


def commentary_numbers(text: str) -> list:
    """[(token, line_number)] for each figure-like number in the '## Commentary' section."""
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    out, inside = [], False
    for ln, line in enumerate(text.split("\n"), start=1):
        if line.startswith("#"):
            inside = bool(COMMENTARY_HEADING_RE.match(line))
            continue
        if not inside:
            continue
        for rx in COMMENTARY_NOT_FIGURES:
            line = rx.sub(lambda m: " " * len(m.group(0)), line)
        for m in COMMENTARY_NUMBER_RE.finditer(line):
            token = m.group(0)
            if re.fullmatch(r"(?:19|20)\d\d", token):                  # a year
                continue
            out.append((token, ln))
    return out


HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
BARE_LABEL_RE = re.compile(r"^\s*\*\*[^*\n]+:\*\*\s*$", re.M)   # "**Renewing:**" with nothing after it


def empty_sections(text: str) -> list:
    """(heading, line) for every ## / ### heading with no visible body before the next heading.
    HTML comments, whitespace and bare "**Label:**" lines do not count as body. The weekly post's
    Commentary placeholder is exempt while the post is still draft: true."""
    lines = text.split("\n")
    body_start = 0
    fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
    is_draft = bool(fm and re.search(r"^draft:\s*true\b", fm.group(1), re.M))
    if fm:
        body_start = text[:fm.end()].count("\n")
    heads = [(i, m.group(2).strip()) for i, l in enumerate(lines) if i >= body_start
             and (m := re.match(r"^(#{2,3})\s+(.+?)\s*$", l))]
    rows = []
    for n, (i, title) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        # a comment can span lines, so strip comments from the whole section, not per line
        body = BARE_LABEL_RE.sub("", HTML_COMMENT_RE.sub("", "\n".join(lines[i + 1:end])))
        if body.strip():
            continue
        if is_draft and title == "Commentary":
            continue
        rows.append((title, i + 1))
    return rows


def audit_empty_sections(post_path: Path) -> list:
    return [[f"section:{title}", "empty_section", title, "N/A", "", ln, "empty_section"]
            for title, ln in empty_sections(post_path.read_text())]


def audit_commentary(post_path: Path, summary: dict) -> list:
    """audit rows ([surface, field, published, computed, delta, line, note]) for every commentary
    number that matches no weekly_summary figure."""
    figures = summary_figures(summary)
    return [["weekly:commentary", "unverified_commentary_number", token, "N/A", "", ln, "unverified_commentary_number"]
            for token, ln in commentary_numbers(post_path.read_text()) if not _matches_at_precision(token, figures)]


def audit_weekly_post(post_path: Path, gt: dict, exact: bool = True, summary: dict | None = None) -> list:
    """Rank, count (periods_above_*), since and verdict fields are exact by default: a weekly
    post's rank is a fact, so a rank of 5 where the store says 4 is a flag, with or without --exact.
    With summary given, the commentary section's numbers are checked against it too."""
    rows = compare_findings(extract_weekly_rows(post_path.read_text().split("\n")), gt, exact)
    if summary is not None:
        rows += audit_commentary(post_path, summary)
    return rows + audit_empty_sections(post_path)


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

    results = compare_findings(findings, gt, exact) + audit_empty_sections(post_path)

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
    parser.add_argument("--content-root", type=Path, metavar="DIR",
                        help="Audit the posts under DIR/daily and DIR/weekly instead of site/content "
                             "(a missing subdirectory is treated as having no posts).")
    parser.add_argument("--exact", action="store_true",
                        help="Daily posts: tolerance 0 for integer-valued fields (counts, rank, percentile, "
                             "days_since); other fields keep ±1.0. Weekly posts are always exact.")
    args = parser.parse_args()
    posts_dir, weekly_dir = POSTS_DIR, WEEKLY_DIR
    if args.content_root:
        posts_dir, weekly_dir = args.content_root / "daily", args.content_root / "weekly"

    if not DB_PATH.exists():
        print(f"No {DB_PATH} — run pipeline/store.py first.", file=sys.stderr)
        sys.exit(1)

    failed = False
    conn = sqlite3.connect(DB_PATH)
    all_rows = []
    checked = 0
    skipped = []          # (post, reason)
    no_conditions = []    # checked on prices only; wind/demand figures unverifiable

    for post_dir in sorted(posts_dir.iterdir() if posts_dir.exists() else []):
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
    if weekly_dir.exists():
        for wdir in sorted(weekly_dir.iterdir()):
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
            for row in audit_weekly_post(idx, weekly_ground_truth(summary), summary=summary):
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
