"""
storage.py — Upload/download chart PNGs via Vercel Blob.

Set BLOB_READ_WRITE_TOKEN (from Vercel dashboard → Storage → Blob → Token) to
activate blob mode. Without it every function is a no-op and charts are served
from git as before.

Activation checklist:
    1. Create a Blob store in the Vercel dashboard.
    2. Copy the BLOB_READ_WRITE_TOKEN and set it:
         - Locally:  export BLOB_READ_WRITE_TOKEN=vercel_blob_...
         - Vercel:   Project Settings → Environment Variables → BLOB_READ_WRITE_TOKEN
    3. Bulk-upload all existing charts:
         python pipeline/storage.py upload
    4. In .gitignore, uncomment the PNG line.
    5. Remove PNGs from git index:
         git rm --cached "site/static/charts/**/*.png"
    6. Commit and push — Vercel will download from blob at build time.

CLI:
    python pipeline/storage.py upload   # upload all local PNGs to blob
    python pipeline/storage.py download # download all blob PNGs (used by Vercel build)
"""

import os
import sys
from pathlib import Path

import requests

CHART_DIR = Path(__file__).parent.parent / "site" / "static" / "charts"
BLOB_API   = "https://blob.vercel-storage.com"


def _token() -> str | None:
    return os.environ.get("BLOB_READ_WRITE_TOKEN")


def upload_png(path: Path) -> str | None:
    """Upload a single PNG to Vercel Blob. Returns public URL or None if no token."""
    token = _token()
    if not token:
        return None

    date_dir = path.parent.name          # e.g. "2026-05-04"
    pathname = f"charts/{date_dir}/{path.name}"

    resp = requests.put(
        f"{BLOB_API}/{pathname}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "image/png",
            "x-allow-overwrite": "1",
        },
        data=path.read_bytes(),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["url"]


def upload_charts_for_date(chart_day_dir: Path) -> None:
    """Upload all PNGs in one date's chart directory. No-op if token not set."""
    if not _token():
        return

    pngs = sorted(chart_day_dir.glob("*.png"))
    if not pngs:
        return

    print(f"  Uploading {len(pngs)} PNGs to Vercel Blob...")
    for png in pngs:
        try:
            upload_png(png)
            print(f"    ✓ {png.name}")
        except Exception as e:
            print(f"    ✗ {png.name} ({e})")


def _list_blob_charts() -> list[dict]:
    """Return all blob entries under the charts/ prefix."""
    token = _token()
    if not token:
        return []

    blobs, cursor = [], None
    while True:
        params = {"prefix": "charts/", "limit": 1000}
        if cursor:
            params["cursor"] = cursor
        resp = requests.get(
            BLOB_API,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        blobs.extend(data.get("blobs", []))
        cursor = data.get("cursor")
        if not cursor:
            break
    return blobs


def bulk_upload() -> None:
    """Upload every PNG under site/static/charts/ to Vercel Blob."""
    if not _token():
        print("Error: BLOB_READ_WRITE_TOKEN not set.")
        print("Get it from Vercel dashboard → Storage → Blob → Token.")
        sys.exit(1)

    date_dirs = sorted(d for d in CHART_DIR.glob("*/") if d.is_dir())
    if not date_dirs:
        print("No chart directories found in site/static/charts/")
        return

    total = sum(1 for d in date_dirs for _ in d.glob("*.png"))
    print(f"Uploading {total} PNGs across {len(date_dirs)} dates...\n")

    done = 0
    for date_dir in date_dirs:
        pngs = sorted(date_dir.glob("*.png"))
        if not pngs:
            continue
        print(f"  {date_dir.name} ({len(pngs)} charts)")
        for png in pngs:
            try:
                upload_png(png)
                done += 1
                print(f"    ✓ {png.name}")
            except Exception as e:
                print(f"    ✗ {png.name} ({e})")

    print(f"\n{done}/{total} PNGs uploaded.")
    print("\nNext steps:")
    print("  1. In .gitignore, uncomment:  # site/static/charts/**/*.png")
    print('  2. git rm --cached "site/static/charts/**/*.png"')
    print("  3. git commit -m 'Move chart PNGs to Vercel Blob storage'")
    print("  4. Add BLOB_READ_WRITE_TOKEN to Vercel project env vars and redeploy.")


def bulk_download() -> None:
    """Download all chart PNGs from Vercel Blob (called by Vercel build command)."""
    if not _token():
        print("BLOB_READ_WRITE_TOKEN not set — skipping blob download, using git-tracked charts.")
        return

    blobs = _list_blob_charts()
    if not blobs:
        print("No charts found in Vercel Blob storage.")
        return

    print(f"Downloading {len(blobs)} charts from Vercel Blob...")
    done = 0
    for blob in blobs:
        # pathname is like "charts/2026-05-04/dam-2026-05-04.png"
        rel = Path(blob["pathname"]).relative_to("charts")   # e.g. 2026-05-04/dam-...png
        local = CHART_DIR / rel
        local.parent.mkdir(parents=True, exist_ok=True)
        try:
            r = requests.get(blob["url"], timeout=30)
            r.raise_for_status()
            local.write_bytes(r.content)
            done += 1
        except Exception as e:
            print(f"  ✗ {blob['pathname']} ({e})")

    print(f"Downloaded {done}/{len(blobs)} charts.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "upload":
        bulk_upload()
    elif cmd == "download":
        bulk_download()
    else:
        print(__doc__)
        sys.exit(1)
