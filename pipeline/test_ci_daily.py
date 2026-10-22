"""Tests for the CI daily helpers: manifest merge and ci_daily's no-op / no-wind paths.
Run: python pipeline/test_ci_daily.py   (temp directories only; no network — fetches and run_daily are stubbed)"""

import contextlib
import io
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ci_daily
from update_manifest import ManifestConflict, read_manifest, update_manifest

failures = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


# ── manifest ────────────────────────────────────────────────────────────────
with tempfile.TemporaryDirectory() as t:
    root = Path(t)
    (root / "data").mkdir()
    manifest = root / "m.sha256"
    old = "a" * 64 + "  data/old_file_not_on_disk.csv\n"
    manifest.write_text(old)
    f1, f2 = root / "data" / "b.csv", root / "data" / "a.csv"
    f1.write_text("one"); f2.write_text("two")

    added = update_manifest([f1, f2, root / "data" / "missing.csv"], manifest, root)
    check("adds present files, skips absent", added == ["data/b.csv", "data/a.csv"], added)
    entries = read_manifest(manifest)
    check("keeps entries whose file is not on disk", entries.get("data/old_file_not_on_disk.csv") == "a" * 64)
    check("sorted by path", list(entries) == sorted(entries), list(entries))

    before = manifest.read_text()
    check("second identical run adds nothing", update_manifest([f1, f2], manifest, root) == [])
    check("second identical run leaves the file byte-identical", manifest.read_text() == before)

    f1.write_text("changed")
    try:
        update_manifest([f1], manifest, root)
        check("changed raw file is a conflict", False)
    except ManifestConflict:
        check("changed raw file is a conflict", True)
    check("conflict writes nothing", manifest.read_text() == before)

# ── ci_daily ────────────────────────────────────────────────────────────────
def run_ci(argv, content: Path):
    saved = (ci_daily.CONTENT_DIR, sys.argv)
    ci_daily.CONTENT_DIR = content
    sys.argv = ["ci_daily.py", *argv]
    out, code = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(out):
            try:
                ci_daily.main()
            except SystemExit as e:
                code = e.code
    finally:
        ci_daily.CONTENT_DIR, sys.argv = saved
    return code, out.getvalue()


with tempfile.TemporaryDirectory() as t:
    content = Path(t) / "site" / "content"
    day = date(2026, 10, 9)
    post = content / "daily" / day.isoformat() / "index.md"
    post.parent.mkdir(parents=True)
    post.write_text("existing")
    ci_daily.fetch_semo = lambda *a, **k: (_ for _ in ()).throw(AssertionError("network used"))
    code, out = run_ci(["--date", day.isoformat()], content)
    check("existing post: exit 0, STATUS=noop, no fetch", code is None and "STATUS=noop" in out, (code, out))
    check("existing post untouched", post.read_text() == "existing")

    # no-wind post is removed and fails, unless allowed
    day2 = date(2026, 10, 10)
    post2 = content / "daily" / day2.isoformat() / "index.md"
    ci_daily.fetch_semo = lambda *a, **k: None
    ci_daily.fetch_area = lambda *a, **k: None
    ci_daily.archive_row_count = lambda p: 1

    class FakeProc:
        stdout = iter(["  ok\n"])
        returncode = 0
        def wait(self):
            post2.parent.mkdir(parents=True, exist_ok=True)
            post2.write_text("---\n---\nno wind rows here\n")
            return 0

    ci_daily.subprocess.Popen = lambda *a, **k: FakeProc()
    code, out = run_ci(["--date", day2.isoformat()], content)
    check("no-wind post: exit 1", code == 1, (code, out))
    check("no-wind post: removed", not post2.parent.exists())

    ci_daily.update_manifest = lambda raw: []
    FakeProc.stdout = iter(["  ok\n"])
    code, out = run_ci(["--date", day2.isoformat(), "--allow-no-wind"], content)
    check("--allow-no-wind keeps it", code is None and "STATUS=generated" in out and post2.exists(), (code, out))

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
