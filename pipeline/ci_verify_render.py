#!/usr/bin/env python3
"""
ci_verify_render.py — check a built Hugo site for one daily post.

    hugo --source site -d "$OUT" && python pipeline/ci_verify_render.py 2026-10-09 "$OUT"

Asserts the rendered daily page carries `noindex, follow`, and a link to the weekly that covers its
day (by week_start in the weekly's front matter) exactly when one exists, otherwise no weekly link.
Exit 1 on any miss.
"""

import re
import sys
from datetime import date, timedelta
from pathlib import Path

CONTENT = Path(__file__).parent.parent / "site" / "content"
WEEKLY_HREF = re.compile(r'href="[^"]*/weekly/(\d{4}/\d{2}/\d{2})/"')


def covering_weekly(day: date):
    """The `date:` of the weekly whose week_start..+6 contains day, or None."""
    for md in sorted((CONTENT / "weekly").glob("*/index.md")):
        text = md.read_text()
        start = re.search(r"^week_start:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
        pub = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
        if start and pub:
            s = date.fromisoformat(start.group(1))
            if s <= day <= s + timedelta(days=6):
                return pub.group(1)
    return None


def main():
    day, public = date.fromisoformat(sys.argv[1]), Path(sys.argv[2])
    page = public / "daily" / f"{day:%Y/%m/%d}" / "index.html"
    if not page.exists():
        print(f"FAIL: {page} not rendered")
        sys.exit(1)
    html = page.read_text()
    problems = []
    if not re.search(r'<meta name="?robots"? content="?noindex, follow"?', html):
        problems.append("missing <meta name=robots content='noindex, follow'>")
    expect = covering_weekly(day)
    found = sorted(set(WEEKLY_HREF.findall(html)))
    want = [expect.replace("-", "/")] if expect else []
    if found != want:
        problems.append(f"weekly pointer: expected {want or 'none'}, found {found or 'none'}")
    if problems:
        print(f"FAIL {day}: " + "; ".join(problems))
        sys.exit(1)
    print(f"ok {day}: noindex, follow; weekly pointer {want[0] if want else 'none (no weekly covers this day)'}")


if __name__ == "__main__":
    main()
