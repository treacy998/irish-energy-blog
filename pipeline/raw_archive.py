#!/usr/bin/env python3
"""
raw_archive.py — keep the raw SEMOpx / EirGrid files behind published posts in a separate private repo.

data/ is gitignored and a CI runner is ephemeral, so without this the checksums in
pipeline/data-manifest.sha256 would point at files that exist nowhere after the job. The raw repo
mirrors the layout of data/ (paths start with data/, so `sha256sum -c pipeline/data-manifest.sha256`
works from its root). It is append-only by convention: a file already in it is never replaced, with one exception
(see may_supersede): an incomplete, unmanifested EirGrid file may be superseded once by a complete one.

    raw_archive.py restore --date 2026-10-09   # sparse-fetch what that day's run needs into data/
    raw_archive.py push --date 2026-10-09      # add this run's manifest-listed files; refuse any change
    raw_archive.py seed                        # one-off: push all of local data/ (not history.db)
    raw_archive.py verify                      # fresh clone, then sha256sum -c against the manifest
    raw_archive.py materialise --from 2026-10-14 --to 2026-10-28 --dest DIR
                                               # restore the archived raw for that range into DIR/data, check
                                               # every file against the manifest, build a throwaway DIR/history.db
                                               # (offline: the archive is the only source). Used as an audit gate.

Remote: --remote PATH_OR_URL, else $RAW_ARCHIVE_REMOTE (used by tests), else https://github.com/$DATA_REPO.git (DATA_REPO defaults to
treacy998/inis-energy-data). With DATA_REPO_TOKEN set, HTTPS requests carry it as a basic-auth
header passed through the environment (never on a command line, never in a URL).
"""

import argparse
import base64
import contextlib
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fetch import path_halfhours                     # noqa: E402
from trading_day import placeable_halfhours          # noqa: E402

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
MANIFEST = Path(__file__).parent / "data-manifest.sha256"
DEFAULT_REPO = "treacy998/inis-energy-data"
HISTORY_DAYS = 6          # keep in step with ci_daily.HISTORY_DAYS
SEED_BATCH = 100          # files per commit/push in seed, to keep each push small
BRANCH = "main"


def remote_url(arg: str | None) -> str:
    return arg or os.environ.get("RAW_ARCHIVE_REMOTE") or f"https://github.com/{os.environ.get('DATA_REPO') or DEFAULT_REPO}.git"


def git_env() -> dict:
    env = dict(os.environ)
    token = os.environ.get("DATA_REPO_TOKEN")
    if token:
        basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="http.https://github.com/.extraheader",
                   GIT_CONFIG_VALUE_0=f"Authorization: Basic {basic}", GIT_TERMINAL_PROMPT="0")
    return env


def git(*args, cwd=None, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, env=git_env(), capture_output=True, text=True)
    if check and r.returncode != 0:
        # stderr only; the token travels in the environment so it cannot appear here
        raise SystemExit(f"git {args[0]} failed: {r.stderr.strip()}")
    return r


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_entries() -> dict[str, str]:
    out = {}
    for line in MANIFEST.read_text().splitlines():
        if line.strip():
            digest, rel = line.split("  ", 1)
            out[rel] = digest
    return out


def is_raw_data(rel: str) -> bool:
    return rel.startswith(("data/MarketResult_", "data/eirgrid_raw/")) or rel == "data/semo_dam_sample.csv"


EIRGRID_RAW = re.compile(r"data/eirgrid_raw/(\d{4}-\d{2}-\d{2})/(wind|demand)\.json$")


def eirgrid_completeness(rel: str, path: Path) -> tuple[int, int] | None:
    """(half-hours present, half-hours the date can supply) for an EirGrid raw file; None for any other file."""
    m = EIRGRID_RAW.search(rel)
    if not m:
        return None
    return path_halfhours(path, m.group(2)), placeable_halfhours(date.fromisoformat(m.group(1)))


def may_supersede(rel: str, archived: Path, new: Path, entries: dict[str, str]) -> tuple[bool, str]:
    """May `new` replace the archived copy of `rel`? Only if the archived EirGrid file is incomplete, no
    manifest entry pins its bytes (it does not back a published post), and `new` is complete.
    Returns (allowed, reason); the reason is logged either way."""
    old, fresh = eirgrid_completeness(rel, archived), eirgrid_completeness(rel, new)
    if old is None:
        return False, "not an EirGrid file"
    if old[0] >= old[1]:
        return False, f"archived file is complete ({old[0]}/{old[1]} half-hours)"
    if entries.get(rel) == sha256(archived):
        return False, f"archived file is incomplete ({old[0]}/{old[1]}) but the manifest references it"
    if fresh[0] < fresh[1]:
        return False, f"new file is incomplete too ({fresh[0]}/{fresh[1]} half-hours)"
    return True, f"archived {old[0]}/{old[1]} half-hours, not in the manifest; new {fresh[0]}/{fresh[1]}"


def clone(remote: str, dest: Path, sparse: list[str] | None = None) -> bool:
    """Clone the raw repo. Returns False if it is empty (no branch yet)."""
    args = ["clone", "-q", "--depth", "1"]
    if sparse is not None:
        args += ["--filter=blob:none", "--no-checkout"]
    git(*args, remote, str(dest))
    if git("rev-parse", "--verify", "-q", "HEAD", cwd=dest, check=False).returncode != 0:
        return False
    if sparse is not None:
        git("sparse-checkout", "set", "--no-cone", *sparse, cwd=dest)
        git("checkout", "-q", cwd=dest)
    return True


def needed_paths(target: date) -> list[str]:
    """What a run for `target` reads from the archive: the SEMOpx files of the 6 days before it and the
    previous day's EirGrid archive, plus the target day's own SEMOpx file and EirGrid archive. The
    latter two exist only if an earlier run archived them and died before publishing; the run then
    generates from those bytes instead of fetching afresh (see ci_daily.py)."""
    pats = [f"/data/MarketResult_SEM-DA_PWR-MRC-D+1_{(target - timedelta(days=k + 1)):%Y%m%d}*.csv"
            for k in range(0, HISTORY_DAYS + 1)]
    pats.append(f"/data/eirgrid_raw/{target - timedelta(days=1)}/*")
    pats.append(f"/data/eirgrid_raw/{target}/*")
    return pats


def copy_new(src_root: Path, files: list[Path]) -> int:
    n = 0
    for f in files:
        dest = DATA_DIR / f.relative_to(src_root / "data")
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        n += 1
    return n


def cmd_restore(args):
    target = date.fromisoformat(args.date)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t) / "raw"
        if not clone(remote_url(args.remote), tmp, sparse=needed_paths(target)):
            print("raw repo is empty; nothing to restore")
            return
        n = copy_new(tmp, [p for p in (tmp / "data").rglob("*") if p.is_file()])
    print(f"restored {n} raw files into data/ for {target}")


def cmd_push(args):
    """Add the manifest-listed raw files that exist in data/. A file already in the raw repo with a
    different hash aborts the run: raw archives are provenance and are never replaced."""
    entries = manifest_entries()
    wanted = [DATA_DIR.parent / rel for rel in sorted(entries) if is_raw_data(rel) and (DATA_DIR.parent / rel).is_file()]
    if not wanted:
        raise SystemExit("no manifest-listed raw files found in data/ to archive")
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t) / "raw"
        non_empty = clone(remote_url(args.remote), tmp)
        if not non_empty:
            git("checkout", "-q", "-b", BRANCH, cwd=tmp)
        added, replaced, conflicts = [], [], []
        for f in wanted:
            rel = f.relative_to(DATA_DIR.parent)
            dest = tmp / rel
            if dest.exists():
                if sha256(dest) != sha256(f):
                    ok, why = may_supersede(rel.as_posix(), dest, f, entries)
                    if not ok:
                        conflicts.append(f"{rel.as_posix()} ({why})")
                        continue
                    print(f"replacing {rel.as_posix()}: {why}; sha256 {sha256(dest)} -> {sha256(f)}")
                    shutil.copy2(f, dest)
                    replaced.append(rel.as_posix())
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            added.append(rel.as_posix())
        if conflicts:
            raise SystemExit("raw files differ from the archived copy (not replacing):\n  " + "\n  ".join(conflicts))
        if not added and not replaced:
            print("raw repo already holds every file")
            return
        git("add", "-A", cwd=tmp)
        git("-c", "user.name=raw-archive", "-c", "user.email=raw-archive@users.noreply.github.com",
            "commit", "-q", "-m", f"raw files for {args.date or 'run'}: {len(added)} added, {len(replaced)} replaced"
            + "".join(f"\nreplaced: {r}" for r in replaced), cwd=tmp)
        git("push", "-q", "origin", f"HEAD:{BRANCH}", cwd=tmp)
    print(f"pushed {len(added)} raw files to the raw repo ({len(replaced)} replaced)")


def cmd_seed(args):
    files = sorted(p for p in DATA_DIR.glob("MarketResult_*.csv")) + [DATA_DIR / "semo_dam_sample.csv"]
    files += sorted(p for p in (DATA_DIR / "eirgrid_raw").rglob("*") if p.is_file())
    files = [p for p in files if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    print(f"seeding {len(files)} files, {total / 1e6:.1f} MB (history.db and data/.claude are not included)")
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t) / "raw"
        if not clone(remote_url(args.remote), tmp):
            git("checkout", "-q", "-b", BRANCH, cwd=tmp)
        pending = 0
        for i in range(0, len(files), SEED_BATCH):
            batch = files[i:i + SEED_BATCH]
            for f in batch:
                dest = tmp / f.relative_to(DATA_DIR.parent)
                if dest.exists():
                    if sha256(dest) != sha256(f):
                        raise SystemExit(f"{dest.relative_to(tmp)} already in the raw repo with different content")
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                pending += 1
            git("add", "-A", cwd=tmp)
            if git("diff", "--cached", "--quiet", cwd=tmp, check=False).returncode != 0:
                git("-c", "user.name=raw-archive", "-c", "user.email=raw-archive@users.noreply.github.com",
                    "commit", "-q", "-m", f"seed: files {i + 1}-{i + len(batch)} of {len(files)}", cwd=tmp)
                git("push", "-q", "origin", f"HEAD:{BRANCH}", cwd=tmp)
                print(f"  pushed {min(i + SEED_BATCH, len(files))}/{len(files)}")
    print(f"seeded; {pending} new files")


def cmd_verify(args):
    """Fresh clone, then sha256sum -c against the blog repo's manifest. Entries that are not raw data
    are reported, not checked."""
    entries = manifest_entries()
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t) / "raw"
        if not clone(remote_url(args.remote), tmp):
            raise SystemExit("raw repo is empty")
        checkable = {r: h for r, h in entries.items() if is_raw_data(r)}
        skipped = sorted(set(entries) - set(checkable))
        listing = Path(t) / "manifest.checked"
        listing.write_text("".join(f"{h}  {r}\n" for r, h in sorted(checkable.items())))
        r = subprocess.run(["sha256sum", "-c", str(listing)], cwd=tmp, capture_output=True, text=True)
    bad = [l for l in r.stdout.splitlines() if not l.endswith(": OK")]
    print(f"checked {len(checkable)} manifest entries from a fresh clone: {len(checkable) - len(bad)} OK, {len(bad)} not OK")
    for l in bad[:20]:
        print("  " + l)
    for s in skipped:
        print(f"  not raw data, not checked: {s}")
    sys.exit(1 if bad else 0)


def window_paths(start: date, end: date) -> list[str]:
    """Sparse-checkout patterns for the raw behind deliveries start..end: each day's SEMOpx file (trade date =
    delivery - 1) and each day's EirGrid archive, plus the day before `start` (its evening half-hours)."""
    pats, d = [], start
    while d <= end:
        pats.append(f"/data/MarketResult_SEM-DA_PWR-MRC-D+1_{(d - timedelta(days=1)):%Y%m%d}*.csv")
        d += timedelta(days=1)
    d = start - timedelta(days=1)
    while d <= end:
        pats.append(f"/data/eirgrid_raw/{d}/*")
        d += timedelta(days=1)
    return pats


SEMO_RAW = re.compile(r"data/MarketResult_SEM-DA_PWR-MRC-D\+1_(\d{8})")


def in_window(rel: str, start: date, end: date) -> bool:
    """Is this manifest path one that materialise(start, end) is meant to restore?"""
    m = SEMO_RAW.match(rel)
    if m:
        return start <= datetime.strptime(m.group(1), "%Y%m%d").date() + timedelta(days=1) <= end
    m = EIRGRID_RAW.match(rel)
    return bool(m) and start - timedelta(days=1) <= date.fromisoformat(m.group(1)) <= end


def build_throwaway_db(dest: Path, start: date, end: date) -> dict:
    """history.db in dest, built with store.py's own backfill functions from dest/data alone. No network:
    store.fetch_area is replaced so a date whose archive is missing is reported, never fetched."""
    import store                                    # heavy imports (pandas, process); only materialise needs them
    db = dest / "history.db"
    conn = store.build_db(db)
    prices = store.backfill_market_prices(conn, dest / "data")
    saved, store.fetch_area = store.fetch_area, (lambda *a, **k: None)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            res = store.backfill_system_conditions(conn, start, end, out_dir=dest / "data", retries=0)
    finally:
        store.fetch_area = saved
    days = conn.execute("SELECT count(DISTINCT date) FROM market_prices").fetchone()[0]
    conn.close()
    return {"db": db, "price_rows": prices, "price_days": days, "condition_rows": res.rows,
            "wind_failed": res.wind_failed, "demand_missing": res.demand_missing}


def cmd_materialise(args):
    """Restore the archived raw for deliveries --from..--to into DEST/data (a fresh directory), verify every
    restored file against the manifest, and build DEST/history.db from it. Fails (nonzero, nothing built) if
    a restored file's hash differs from its manifest entry, or a manifest-pinned file for the range is
    missing from the archive. Files the manifest does not pin (older than its first entry, or in a gap) are
    restored and counted, not trusted blindly: the summary says how many."""
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.to)
    if end < start:
        raise SystemExit("--to is before --from")
    dest = Path(args.dest).resolve()
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit(f"{dest} is not empty; materialise builds a throwaway store in a fresh directory")
    (dest / "data").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t) / "raw"
        if not clone(remote_url(args.remote), tmp, sparse=window_paths(start, end)):
            raise SystemExit("raw repo is empty")
        src = [p for p in (tmp / "data").rglob("*") if p.is_file()] if (tmp / "data").exists() else []
        for f in src:
            out = dest / f.relative_to(tmp)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out)
    entries = manifest_entries()
    restored = {p.relative_to(dest).as_posix(): p for p in (dest / "data").rglob("*") if p.is_file()}
    mismatched = sorted(r for r, p in restored.items() if r in entries and entries[r] != sha256(p))
    absent = sorted(r for r in entries if is_raw_data(r) and in_window(r, start, end) and r not in restored)
    pinned = sum(1 for r in restored if r in entries)
    if mismatched or absent:
        for r in mismatched:
            print(f"HASH MISMATCH {r}: archive {sha256(restored[r])}, manifest {entries[r]}")
        for r in absent:
            print(f"MISSING FROM ARCHIVE {r}: pinned by the manifest")
        raise SystemExit(f"materialise {start}..{end}: {len(mismatched)} hash mismatch(es), {len(absent)} manifest file(s) missing")
    built = build_throwaway_db(dest, start, end)
    print(f"materialised {len(restored)} raw files for {start}..{end} into {dest}/data: {pinned} pinned by the manifest and "
          f"matching, {len(restored) - pinned} not pinned by it")
    print(f"built {built['db'].name}: {built['price_rows']} price rows over {built['price_days']} days, "
          f"{built['condition_rows']} system_conditions rows")
    if built["wind_failed"]:
        w = built["wind_failed"]
        print(f"  no archived EirGrid wind for {len(w)} date(s) ({w[0]}..{w[-1]}): their wind/demand figures have no archived ground truth")
    if built["demand_missing"]:
        print(f"  demand incomplete for {len(built['demand_missing'])} date(s): {built['demand_missing'][:5]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("--remote", help="Raw repo URL or path (default: https://github.com/$DATA_REPO.git).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("restore", cmd_restore), ("push", cmd_push), ("seed", cmd_seed), ("verify", cmd_verify),
                     ("materialise", cmd_materialise)):
        p = sub.add_parser(name)
        if name in ("restore", "push"):
            p.add_argument("--date", required=name == "restore", metavar="YYYY-MM-DD")
        if name == "materialise":
            p.add_argument("--from", dest="start", required=True, metavar="YYYY-MM-DD", help="First delivery date.")
            p.add_argument("--to", required=True, metavar="YYYY-MM-DD", help="Last delivery date.")
            p.add_argument("--dest", required=True, metavar="DIR", help="A new, empty directory for data/ and history.db.")
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    args.remote = remote_url(args.remote)
    args.fn(args)


if __name__ == "__main__":
    main()
