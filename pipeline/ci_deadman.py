#!/usr/bin/env python3
"""
ci_deadman.py — deadman.yml's checks. Independent of archive.yml and weekly.yml: it only looks at what they should have left.

    python pipeline/ci_deadman.py              # the raw repo has yesterday's files
    python pipeline/ci_deadman.py --weekly     # ...and the last Sunday's weekly post is on master or in an open PR

Raw: yesterday's (Irish calendar) SEMOpx DA file, wind and demand are in the raw repo, and the two EirGrid files hold every
half-hour the day can supply. Weekly (deadman.yml adds --weekly on Tuesdays): site/content/weekly/<last Sunday>/index.md
exists in the checkout (the default branch) or the branch weekly/<last Sunday> has an open pull request.
Every problem is printed as ::error:: and the exit status is 1, so the run fails and GitHub emails the repo's owners.
"""

import argparse
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import raw_archive as ra                               # noqa: E402
import raw_gap                                         # noqa: E402
from fetch import path_halfhours                       # noqa: E402
from trading_day import placeable_halfhours            # noqa: E402

ROOT = Path(__file__).parent.parent


def check_raw(remote: str, today: date) -> list[str]:
    y = today - timedelta(days=1)
    lacking = dict(raw_gap.missing(set(ra.list_archive(remote)), y, y)).get(y, [])
    problems = [f"the raw repo has no {k} file for {y}" for k in lacking]
    have = [k for k in ("wind", "demand") if k not in lacking]
    if have:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t) / "raw"
            ra.clone(remote, tmp, sparse=[f"/data/eirgrid_raw/{y}/*"])
            need = placeable_halfhours(y)
            for k in have:
                n = path_halfhours(tmp / raw_gap.eirgrid_rel(y, k), k)
                if n < need:
                    problems.append(f"the raw repo's {k} file for {y} holds {n}/{need} half-hours")
    return problems


def last_sunday(today: date) -> date:
    return today - timedelta(days=(today.weekday() + 1) % 7 or 7)


def open_pr_for(branch: str) -> bool:
    r = subprocess.run(["gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number", "--jq", "length"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"::error::cannot list pull requests: {r.stderr.strip()}")
    return r.stdout.strip() not in ("", "0")


def check_weekly(today: date, content_root: Path, open_pr=open_pr_for) -> list[str]:
    sunday = last_sunday(today)
    post = content_root / "weekly" / sunday.isoformat() / "index.md"
    if post.exists() or open_pr(f"weekly/{sunday}"):
        return []
    return [f"no weekly post for the week ending {sunday}: {post.relative_to(content_root.parent.parent)} is not on the "
            f"default branch and weekly/{sunday} has no open pull request (did weekly.yml run?)"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("--weekly", action="store_true", help="Also check the last Sunday's weekly post.")
    ap.add_argument("--today", metavar="YYYY-MM-DD", help="Override today (Irish calendar), for testing.")
    ap.add_argument("--remote", help="Raw repo URL or path (default as raw_archive.py).")
    args = ap.parse_args()
    today = date.fromisoformat(args.today) if args.today else raw_gap.yesterday() + timedelta(days=1)
    problems = check_raw(ra.remote_url(args.remote), today)
    if args.weekly:
        problems += check_weekly(today, ROOT / "site" / "content")
    for p in problems:
        print(f"::error::{p}")
    if not problems:
        print(f"ok: the raw repo has {today - timedelta(days=1)}" + (f"; the weekly post for {last_sunday(today)} is on master or in a PR" if args.weekly else ""))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
