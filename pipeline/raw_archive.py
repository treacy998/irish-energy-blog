#!/usr/bin/env python3
"""
raw_archive.py — keep the raw SEMOpx / EirGrid files behind published posts in a separate private repo.

data/ is gitignored and a CI runner is ephemeral, so without this the checksums in
pipeline/data-manifest.sha256 would point at files that exist nowhere after the job. The raw repo
mirrors the layout of data/ (paths start with data/, so `sha256sum -c pipeline/data-manifest.sha256`
works from its root). It is append-only by convention: a file already in it is never replaced.

    raw_archive.py restore --date 2026-10-09   # sparse-fetch what that day's run needs into data/
    raw_archive.py push --date 2026-10-09      # add this run's manifest-listed files; refuse any change
    raw_archive.py seed                        # one-off: push all of local data/ (not history.db)
    raw_archive.py verify                      # fresh clone, then sha256sum -c against the manifest

Remote: --remote PATH_OR_URL, else $RAW_ARCHIVE_REMOTE (used by tests), else https://github.com/$DATA_REPO.git (DATA_REPO defaults to
treacy998/inis-energy-data). With DATA_REPO_TOKEN set, HTTPS requests carry it as a basic-auth
header passed through the environment (never on a command line, never in a URL).
"""

import argparse
import base64
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

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
        added, conflicts = [], []
        for f in wanted:
            rel = f.relative_to(DATA_DIR.parent)
            dest = tmp / rel
            if dest.exists():
                if sha256(dest) != sha256(f):
                    conflicts.append(rel.as_posix())
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            added.append(rel.as_posix())
        if conflicts:
            raise SystemExit("raw files differ from the archived copy (not replacing):\n  " + "\n  ".join(conflicts))
        if not added:
            print("raw repo already holds every file")
            return
        git("add", "-A", cwd=tmp)
        git("-c", "user.name=raw-archive", "-c", "user.email=raw-archive@users.noreply.github.com",
            "commit", "-q", "-m", f"raw files for {args.date or 'run'}: {len(added)} added", cwd=tmp)
        git("push", "-q", "origin", f"HEAD:{BRANCH}", cwd=tmp)
    print(f"pushed {len(added)} raw files to the raw repo")


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
    (the manifest holds one stray Claude settings file) are reported, not checked."""
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("--remote", help="Raw repo URL or path (default: https://github.com/$DATA_REPO.git).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("restore", cmd_restore), ("push", cmd_push), ("seed", cmd_seed), ("verify", cmd_verify)):
        p = sub.add_parser(name)
        if name in ("restore", "push"):
            p.add_argument("--date", required=name == "restore", metavar="YYYY-MM-DD")
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    args.remote = remote_url(args.remote)
    args.fn(args)


if __name__ == "__main__":
    main()
