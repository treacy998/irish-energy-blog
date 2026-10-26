#!/usr/bin/env python3
"""
probe_eirgrid.py — DIAGNOSTIC. Ask EirGrid's dashboard for wind and demand the way fetch.py does and
print what came back, to tell an environment problem (an IP range, a header) from an intermittent feed.

    python pipeline/probe_eirgrid.py                      # 2026-10-23 and 2026-10-24, 6 rounds, 30 s apart
    python pipeline/probe_eirgrid.py --dates 2026-10-23 --rounds 3 --interval 10 --show-ip

One row per request: UTC time, date, area, HTTP status, elapsed, body bytes, data rows, non-null rows of
the area's main series, and whichever of a fixed list of rate-limit / CDN / cache headers were present.
Nothing is written to disk, and no cookie, token or Set-Cookie header is read or printed. The query and
timeout are fetch.py's, and no headers are added, so the User-Agent is requests' default.
"""

import argparse
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from fetch import EIRGRID_BASE, PRIMARY_FIELD, TIMEOUT

HEADERS_SEEN = ("Retry-After", "CF-Ray", "CF-Cache-Status", "X-Cache", "X-Cache-Status", "Age", "Via",
                "Server", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-Served-By")


def params(day: date, area: str) -> dict:
    """The same query as fetch._fetch_area."""
    d = day.strftime("%d-%b-%Y")
    return {"region": "ROI", "chartType": "generation" if area == "demand" else area, "dateRange": "day",
            "dateFrom": d, "dateTo": d, "areas": "windactual,windforecast" if area == "wind" else "demandactual,demandforecast"}


def probe_once(day: date, area: str) -> dict:
    t0 = time.monotonic()
    out = {"time": datetime.now(timezone.utc).strftime("%H:%M:%S"), "date": day.isoformat(), "area": area,
           "status": "-", "ms": "-", "bytes": 0, "rows": 0, "main": 0, "headers": "", "note": ""}
    try:
        r = requests.get(EIRGRID_BASE, params=params(day, area), timeout=TIMEOUT)
        out.update(status=r.status_code, ms=int((time.monotonic() - t0) * 1000), bytes=len(r.content))
        out["headers"] = " ".join(f"{h}={r.headers[h]}" for h in HEADERS_SEEN if h in r.headers)
        try:
            rows = r.json().get("Rows") or []
            out["rows"] = len(rows)
            out["main"] = sum(1 for x in rows if x.get("FieldName") == PRIMARY_FIELD[area] and x.get("Value") is not None)
        except ValueError:
            out["note"] = "non-JSON body"
    except requests.RequestException as e:
        out.update(ms=int((time.monotonic() - t0) * 1000), note=f"{type(e).__name__}: {str(e)[:80]}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("--dates", nargs="+", default=["2026-10-23", "2026-10-24"], metavar="YYYY-MM-DD")
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--interval", type=float, default=30.0, help="seconds between rounds")
    ap.add_argument("--show-ip", action="store_true", help="print this machine's public IP first (api.ipify.org)")
    args = ap.parse_args()
    if args.show_ip:
        try:
            print("public IP:", requests.get("https://api.ipify.org", timeout=10).text.strip())
        except requests.RequestException as e:
            print("public IP: unavailable", e)
    print(f"requests {requests.__version__}; User-Agent {requests.utils.default_user_agent()}; timeout {TIMEOUT}s")
    cols = ("round", "time", "date", "area", "status", "ms", "bytes", "rows", "main", "headers", "note")
    print(" | ".join(cols))
    results = []
    for n in range(1, args.rounds + 1):
        for d in args.dates:
            for area in ("demand", "wind"):
                r = probe_once(date.fromisoformat(d), area)
                results.append(r)
                print(" | ".join(str(x) for x in (n, *(r[c] for c in cols[1:]))), flush=True)
        if n < args.rounds:
            time.sleep(args.interval)
    print("\nsummary (requests with the day's main series present / requests):")
    for d in args.dates:
        for area in ("demand", "wind"):
            rs = [r for r in results if r["date"] == d and r["area"] == area]
            full = sum(1 for r in rs if r["main"] >= 96)
            empty = sum(1 for r in rs if r["status"] == 200 and r["rows"] == 0)
            err = sum(1 for r in rs if r["status"] != 200)
            print(f"  {d} {area}: {full}/{len(rs)} complete, {empty} empty 200, {err} non-200 or failed")


if __name__ == "__main__":
    main()
