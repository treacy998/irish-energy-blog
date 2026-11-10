#!/usr/bin/env python3
"""
raw_gap.py — find the delivery dates the raw repo lacks and push this machine's raw files for them.

    raw_gap.py list [--from D] [--to D]            # what the raw repo lacks, and what this machine holds for it
    raw_gap.py push [--from D] [--to D] [--dry-run] [--allow-incomplete]

For each delivery date D the archive needs three files: the SEMOpx DA file (trade date D-1, so its name carries
D-1), data/eirgrid_raw/D/wind.json and data/eirgrid_raw/D/demand.json. --to defaults to yesterday (Irish
calendar); --from to the first date the raw repo holds an EirGrid directory for (before that there is none to lack).

Every local file is verified before anything is pushed, in the manifest's own format ("<sha256>  data/...", as in
pipeline/data-manifest.sha256, printed for each file):
  * if the manifest pins the path, the sha256 must equal the pinned one, or the file is refused;
  * a SEMOpx file must parse with process.load_dam_data (ROI-DA price, NI-DA agrees, 48/50/46 periods) and be D's;
  * an EirGrid file must hold every half-hour D can supply. An incomplete or empty one is reported and NOT pushed
    unless --allow-incomplete (archive.yml's heal pass fetches those; raw_archive.may_supersede lets a complete
    file replace an unmanifested incomplete one once).
push adds the verified files in one commit through raw_archive.push_files (never replaces an archived file) and
needs git credentials for the raw repo. --dry-run does everything but the push. Remote as raw_archive.py.
"""

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import raw_archive as ra                              # noqa: E402
from fetch import path_halfhours                      # noqa: E402
from trading_day import placeable_halfhours           # noqa: E402

KINDS = ("semo", "wind", "demand")


def yesterday() -> date:
    return datetime.now(ZoneInfo("Europe/Dublin")).date() - timedelta(days=1)


def semo_prefix(d: date) -> str:
    return f"data/MarketResult_SEM-DA_PWR-MRC-D+1_{(d - timedelta(days=1)):%Y%m%d}"


def eirgrid_rel(d: date, kind: str) -> str:
    return f"data/eirgrid_raw/{d}/{kind}.json"


def has(listing: set[str], d: date, kind: str) -> bool:
    if kind == "semo":
        return any(p.startswith(semo_prefix(d)) for p in listing)
    return eirgrid_rel(d, kind) in listing


def first_eirgrid_date(listing: set[str]) -> date | None:
    days = [ra.EIRGRID_RAW.match(p).group(1) for p in listing if ra.EIRGRID_RAW.match(p)]
    return date.fromisoformat(min(days)) if days else None


def missing(listing: set[str], start: date, end: date) -> list[tuple[date, list[str]]]:
    """[(delivery date, [kinds the archive lacks])] for every date in start..end that lacks something."""
    out, d = [], start
    while d <= end:
        kinds = [k for k in KINDS if not has(listing, d, k)]
        if kinds:
            out.append((d, kinds))
        d += timedelta(days=1)
    return out


def local_path(d: date, kind: str, data_dir: Path) -> Path | None:
    if kind == "semo":
        found = sorted(data_dir.glob(f"MarketResult_SEM-DA_PWR-MRC-D+1_{(d - timedelta(days=1)):%Y%m%d}*.csv"))
        return found[-1] if found else None
    p = data_dir / "eirgrid_raw" / d.isoformat() / f"{kind}.json"
    return p if p.is_file() else None


@dataclass
class Item:
    d: date
    kind: str
    rel: str
    path: Path | None
    sha: str = ""
    status: str = "ok"          # ok | absent | refused | incomplete
    note: str = ""


def verify(d: date, kind: str, data_dir: Path, entries: dict[str, str]) -> Item:
    path = local_path(d, kind, data_dir)
    rel = path.relative_to(data_dir.parent).as_posix() if path else (semo_prefix(d) + "*.csv" if kind == "semo" else eirgrid_rel(d, kind))
    if path is None:
        return Item(d, kind, rel, None, status="absent", note="not on this machine")
    it = Item(d, kind, rel, path, sha=ra.sha256(path))
    if rel in entries and entries[rel] != it.sha:
        it.status, it.note = "refused", f"sha256 differs from the manifest's {entries[rel][:12]}"
        return it
    it.note = "pinned by the manifest, matches" if rel in entries else "not pinned by the manifest"
    if kind == "semo":
        from process import MarketSplitError, load_dam_data
        try:
            df = load_dam_data(path)
        except MarketSplitError as e:
            it.status, it.note = "refused", f"MARKET SPLIT {e.delivery_date}: periods {', '.join(map(str, e.periods))} ({e})"
            return it
        except ValueError as e:
            it.status, it.note = "refused", f"does not parse: {e}"
            return it
        if df["DeliveryDate"].iloc[0].date() != d:
            it.status, it.note = "refused", f"is for {df['DeliveryDate'].iloc[0].date()}, not {d}"
    else:
        have, need = path_halfhours(path, kind), placeable_halfhours(d)
        if have < need:
            it.status, it.note = "incomplete", f"{have}/{need} half-hours"
    return it


def plan(listing: set[str], start: date, end: date, data_dir: Path, entries: dict[str, str]) -> list[Item]:
    return [verify(d, k, data_dir, entries) for d, kinds in missing(listing, start, end) for k in kinds]


def window(args, listing: set[str]) -> tuple[date, date]:
    start = date.fromisoformat(args.start) if args.start else first_eirgrid_date(listing)
    if start is None:
        raise SystemExit("the raw repo holds no EirGrid files; pass --from")
    return start, date.fromisoformat(args.to) if args.to else yesterday()


def report(items: list[Item], gaps: list) -> None:
    print(f"the raw repo lacks files for {len(gaps)} delivery date(s):")
    for d, kinds in gaps:
        print(f"  {d}: {', '.join(kinds)}")
    print("\nthis machine, verified (manifest format: <sha256>  path):")
    for it in items:
        print(f"  {it.status.upper():10s} {it.d} {it.kind:6s} {it.note}")
        if it.sha:
            print(f"    {it.sha}  {it.rel}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("--remote", help="Raw repo URL or path (default as raw_archive.py).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "push"):
        p = sub.add_parser(name)
        p.add_argument("--from", dest="start", metavar="YYYY-MM-DD")
        p.add_argument("--to", metavar="YYYY-MM-DD")
        if name == "push":
            p.add_argument("--dry-run", action="store_true")
            p.add_argument("--allow-incomplete", action="store_true")
    args = ap.parse_args(argv)
    remote = ra.remote_url(args.remote)
    listing = set(ra.list_archive(remote))
    start, end = window(args, listing)
    gaps = missing(listing, start, end)
    items = plan(listing, start, end, ra.DATA_DIR, ra.manifest_entries())
    report(items, gaps)
    refused = [i for i in items if i.status == "refused"]
    if args.cmd == "list":
        if gaps:
            print(f"\nto push the verified files:\n  python pipeline/raw_gap.py push --to {end}")
        return 0
    if refused:
        print(f"\nnothing pushed: {len(refused)} file(s) refused")
        return 1
    ok = [i for i in items if i.status == "ok" or (i.status == "incomplete" and args.allow_incomplete)]
    skipped = [i for i in items if i not in ok]
    if skipped:
        print(f"\nnot pushed: {len(skipped)} ({', '.join(f'{i.d} {i.kind} {i.status}' for i in skipped)})")
    if not ok:
        print("nothing to push")
        return 0
    if args.dry_run:
        print(f"\ndry run: would push {len(ok)} file(s) ({sum(i.path.stat().st_size for i in ok) / 1e6:.1f} MB) in one commit")
        return 0
    ra.push_files([i.path for i in ok], remote, f"{start}..{end} (raw_gap)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
