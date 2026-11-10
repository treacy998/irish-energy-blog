"""raw_gap.py: list the delivery dates the raw repo lacks, verify this machine's files, push them.
Run: python pipeline/test_raw_gap.py   (temp directories and a local bare repo as the raw remote; no network)"""

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import raw_archive as ra
import raw_gap
from test_ci_retry import eirgrid_body
from test_dam_markets import write_file
from trading_day import expected_periods

D0 = date(2026, 11, 1)                   # the raw repo holds everything up to and including this delivery date


def put_semo(root: Path, d: date, bad_market=False):
    base = [100.0 + p for p in range(1, expected_periods(d) + 1)]
    ni = list(base)
    if bad_market:
        ni[6] += 7
    with tempfile.TemporaryDirectory() as t:
        src = write_file(Path(t), delivery=d, ni=ni, roi=base)
        stamp = f"{d - timedelta(days=1):%Y%m%d}"
        dest = root / "data" / f"MarketResult_SEM-DA_PWR-MRC-D+1_{stamp}110000_{stamp}115501.csv"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return dest


def put_eirgrid(root: Path, d: date, quarters=96, demand_quarters=None):
    for area, q in (("wind", quarters), ("demand", demand_quarters if demand_quarters is not None else quarters)):
        p = root / "data" / "eirgrid_raw" / d.isoformat() / f"{area}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(eirgrid_body(d.isoformat(), area, 100.0, q))


def put_day(root: Path, d: date, **kw):
    put_semo(root, d)
    put_eirgrid(root, d, **kw)


@contextlib.contextmanager
def env():
    """A bare raw repo already holding D0-1..D0, and a 'laptop' data dir holding D0-1..D0+3."""
    saved = (ra.DATA_DIR, ra.MANIFEST, os.environ.get("RAW_ARCHIVE_REMOTE"))
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        e = type("Env", (), {})()
        e.tmp, e.laptop = tmp, tmp / "laptop"
        e.remote = tmp / "raw.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(e.remote)], check=True)
        os.environ["RAW_ARCHIVE_REMOTE"] = str(e.remote)
        ra.MANIFEST = tmp / "manifest.sha256"
        ra.MANIFEST.write_text("")
        seed = tmp / "seed"
        for k in (1, 0):
            put_day(seed, D0 - timedelta(days=k))
        ra.DATA_DIR = seed / "data"
        ra.push_files(sorted(p for p in (seed / "data").rglob("*") if p.is_file()), str(e.remote), "seed", {})
        for k in (1, 0, -1, -2, -3):
            put_day(e.laptop, D0 - timedelta(days=k))
        ra.DATA_DIR = e.laptop / "data"
        e.head = lambda: subprocess.run(["git", "-C", str(e.remote), "rev-parse", "main"], capture_output=True, text=True).stdout.strip()
        e.listing = lambda: set(ra.list_archive(str(e.remote)))
        try:
            yield e
        finally:
            ra.DATA_DIR, ra.MANIFEST = saved[0], saved[1]
            if saved[2] is None:
                os.environ.pop("RAW_ARCHIVE_REMOTE", None)
            else:
                os.environ["RAW_ARCHIVE_REMOTE"] = saved[2]


def run(argv):
    out, code = io.StringIO(), 0
    with contextlib.redirect_stdout(out):
        try:
            code = raw_gap.main(argv)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue()


def test_missing_lists_every_date_and_kind_the_archive_lacks():
    listing = {raw_gap.semo_prefix(date(2026, 11, 1)) + "110000_x.csv", raw_gap.eirgrid_rel(date(2026, 11, 1), "wind"),
               raw_gap.eirgrid_rel(date(2026, 11, 1), "demand"), raw_gap.eirgrid_rel(date(2026, 11, 2), "wind")}
    assert raw_gap.missing(listing, date(2026, 11, 1), date(2026, 11, 3)) == [
        (date(2026, 11, 2), ["semo", "demand"]), (date(2026, 11, 3), ["semo", "wind", "demand"])]
    assert raw_gap.first_eirgrid_date(listing) == date(2026, 11, 1)


def test_list_names_the_gap_and_the_files_to_push_without_touching_the_remote():
    with env() as e:
        before = e.head()
        code, out = run(["list", "--to", str(D0 + timedelta(days=3))])
        assert code == 0 and e.head() == before
        assert "lacks files for 3 delivery date(s)" in out and str(D0 + timedelta(days=1)) in out and str(D0 + timedelta(days=3)) in out
        assert str(D0) not in out.split("this machine")[0], out
        assert out.count("OK ") == 9 and "  python pipeline/raw_gap.py push --to 2026-11-04" in out
        sha = ra.sha256(raw_gap.local_path(D0 + timedelta(days=1), "wind", ra.DATA_DIR))
        assert f"{sha}  data/eirgrid_raw/2026-11-02/wind.json" in out         # the manifest's own line format


def test_verify_statuses():
    with env() as e:
        d1, d2, d3 = (D0 + timedelta(days=k) for k in (1, 2, 3))
        put_eirgrid(e.laptop, d2, demand_quarters=0)                          # empty demand
        put_semo(e.laptop, d3, bad_market=True)                               # NI-DA disagrees with ROI-DA
        shutil.rmtree(e.laptop / "data" / "eirgrid_raw" / d3.isoformat())     # and no EirGrid files
        (e.laptop / "data" / "eirgrid_raw" / d1.isoformat() / "wind.json").write_text(eirgrid_body(d1.isoformat(), "wind", 100.0, 60))
        entries = {"data/eirgrid_raw/2026-11-03/demand.json": "0" * 64}
        got = {(i.d, i.kind): i for i in raw_gap.plan(e.listing(), d1, d3, ra.DATA_DIR, entries)}
        assert got[(d1, "semo")].status == "ok" and got[(d1, "demand")].status == "ok"
        assert got[(d1, "wind")].status == "incomplete" and "/48 half-hours" in got[(d1, "wind")].note
        assert got[(d2, "demand")].status == "refused" and "differs from the manifest" in got[(d2, "demand")].note
        assert got[(d3, "semo")].status == "refused" and "NI-DA and ROI-DA" in got[(d3, "semo")].note
        assert got[(d3, "wind")].status == "absent"
        assert got[(d2, "wind")].status == "ok"
        entries = {"data/eirgrid_raw/2026-11-02/demand.json": ra.sha256(e.laptop / "data/eirgrid_raw/2026-11-02/demand.json")}
        assert raw_gap.verify(d1, "demand", ra.DATA_DIR, entries).note == "pinned by the manifest, matches"


def test_a_semo_file_for_another_date_is_refused():
    with env() as e:
        wrong = put_semo(e.laptop, D0 + timedelta(days=2))
        right = raw_gap.local_path(D0 + timedelta(days=1), "semo", ra.DATA_DIR)
        shutil.copy2(wrong, right)                                            # D0+2's content under D0+1's name
        it = raw_gap.verify(D0 + timedelta(days=1), "semo", ra.DATA_DIR, {})
        assert it.status == "refused" and "is for 2026-11-03" in it.note, it


def test_dry_run_verifies_but_pushes_nothing():
    with env() as e:
        before = e.head()
        code, out = run(["push", "--dry-run", "--to", str(D0 + timedelta(days=3))])
        assert code == 0 and e.head() == before and "dry run: would push 9 file(s)" in out, out


def test_push_adds_the_verified_files_in_one_commit_and_is_idempotent():
    with env() as e:
        to = str(D0 + timedelta(days=3))
        code, out = run(["push", "--to", to])
        assert code == 0 and "pushed 9 raw files" in out, out
        have = e.listing()
        assert raw_gap.missing(have, D0, date.fromisoformat(to)) == []
        n = subprocess.run(["git", "-C", str(e.remote), "rev-list", "--count", "main"], capture_output=True, text=True).stdout.strip()
        assert n == "2", n                                                    # the seed commit and one push
        head = e.head()
        code, out = run(["push", "--to", to])
        assert code == 0 and e.head() == head and "lacks files for 0" in out and "nothing to push" in out, out


def test_incomplete_files_are_held_back_unless_allowed():
    with env() as e:
        d1 = D0 + timedelta(days=1)
        put_eirgrid(e.laptop, d1, demand_quarters=0)
        code, out = run(["push", "--to", str(d1)])
        assert code == 0 and "not pushed: 1 (2026-11-02 demand incomplete)" in out and "pushed 2 raw files" in out, out
        assert raw_gap.eirgrid_rel(d1, "demand") not in e.listing()
        code, out = run(["push", "--allow-incomplete", "--to", str(d1)])
        assert code == 0 and "pushed 1 raw files" in out and raw_gap.eirgrid_rel(d1, "demand") in e.listing(), out


def test_a_refused_file_stops_the_whole_push():
    with env() as e:
        put_semo(e.laptop, D0 + timedelta(days=2), bad_market=True)
        before = e.head()
        code, out = run(["push", "--to", str(D0 + timedelta(days=3))])
        assert code == 1 and e.head() == before and "nothing pushed: 1 file(s) refused" in out, out


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
