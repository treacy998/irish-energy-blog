"""
fetch.py — Download SEMO and EirGrid data.

PHASE A (current): Manual download.
    1. Go to https://www.sem-o.com/market-data/
    2. Download Day-Ahead Market results CSV
    3. Save to data/ folder

PHASE B (future): Automate with requests.
    SEMO publishes DAM results at predictable URLs.
    EirGrid Smart Grid Dashboard has an API.
    Uncomment and adapt the functions below when ready.
"""

import sys
from pathlib import Path
from datetime import date, timedelta

DATA_DIR = Path(__file__).parent.parent / "data"


def check_data_exists(target_date: date) -> bool:
    """Check if we have data for the target date."""
    # Adjust this pattern to match your actual SEMO filename convention
    patterns = [
        f"semo_dam_{target_date.isoformat()}.csv",
        "semo_dam_sample.csv",  # fallback for demo
    ]
    for p in patterns:
        if (DATA_DIR / p).exists():
            return True
    return False


# ─── PHASE B STUBS ──────────────────────────────────────────────
#
# def fetch_semo_dam(target_date: date) -> Path:
#     """Fetch DAM results from SEMO reporting portal."""
#     import requests
#     url = f"https://reports.sem-o.com/..."  # build URL for target date
#     resp = requests.get(url)
#     resp.raise_for_status()
#     outpath = DATA_DIR / f"semo_dam_{target_date.isoformat()}.csv"
#     outpath.write_bytes(resp.content)
#     return outpath
#
# def fetch_eirgrid_wind(target_date: date) -> Path:
#     """Fetch wind generation data from EirGrid."""
#     import requests
#     url = "https://www.smartgriddashboard.com/..."
#     ...
# ────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    yesterday = date.today() - timedelta(days=1)
    target = yesterday

    if check_data_exists(target):
        print(f"Data for {target} found in {DATA_DIR}")
    else:
        print(f"No data for {target}.")
        print(f"Download DAM results from https://www.sem-o.com/market-data/")
        print(f"Save to: {DATA_DIR}/semo_dam_{target.isoformat()}.csv")
        sys.exit(1)
