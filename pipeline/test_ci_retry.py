"""CI retry behaviour against a local bare git repo standing in for the raw archive (requests.get is faked,
no network). Run: python pipeline/test_ci_retry.py

1. A run that dies after the raw push and before the content push is retried cleanly: the retry
   generates from the archived raw bytes (no fresh fetch for the day), the raw push sees no hash
   conflict, and the post is byte-identical.
2. An archived EirGrid file that is incomplete (partial or empty) and unmanifested is not evidence:
   the run fetches live, publishes, and the raw push supersedes the archived file once.
3. If the manifest references that incomplete file, the run is refused and the archive is untouched.
4. may_supersede / cmd_push: complete archived files and incomplete new files are never replaced.

Real: ci_daily.main, raw_archive restore/push (git), fetch.fetch_wind_and_demand, run_daily.main.
Stubbed: the SEMOpx download, the DAM CSV parse, the chart/post scaffold (writes a post that embeds the
EirGrid frame it was given, so a different EirGrid response would change the post bytes)."""

import argparse
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ci_daily
import fetch
import raw_archive
import run_daily
from test_store_only import price_df
from update_manifest import update_manifest

DAY = date(2026, 10, 5)
ISO = DAY.isoformat()


class FakeResp:
    status_code = 200

    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass

    def json(self):
        return json.loads(self.text)


def eirgrid_body(day: str, area: str, base: float, quarters: int = 96) -> str:
    """One calendar day of 15-minute rows (96 = complete; fewer is a feed saved before it was published)."""
    d = date.fromisoformat(day).strftime("%d-%b-%Y")
    fields = ["WIND_ACTUAL", "WIND_FCAST"] if area == "wind" else ["SYSTEM_DEMAND"]
    rows = [{"EffectiveTime": f"{d} {q // 4:02d}:{q % 4 * 15:02d}:00", "FieldName": f, "Region": "ROI",
             "Value": (base + q / 4) if f != "SYSTEM_DEMAND" else 4000.0 + q / 4}
            for q in range(quarters) for f in fields]
    return json.dumps({"Rows": rows})


def run_ci(argv):
    saved = sys.argv
    sys.argv = ["ci_daily.py", *argv]
    out, code = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(out):
            try:
                ci_daily.main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = saved
    return code, out.getvalue()



class Env:
    """A temp checkout, data dir and bare raw repo with the SEMOpx download, scaffold and EirGrid requests faked."""


@contextlib.contextmanager
def ci_env(manifest_text: str = ""):
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        e = Env()
        e.tmp, e.data, e.content, e.root = tmp, tmp / "data", tmp / "site" / "content", tmp
        e.manifest = tmp / "data-manifest.sha256"
        e.manifest.write_text(manifest_text)
        e.remote = tmp / "raw.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(e.remote)], check=True)
        os.environ["RAW_ARCHIVE_REMOTE"] = str(e.remote)
        e.requests_made, e.body = [], {"base": 100.0, "quarters": 96}

        saved = {m: {n: getattr(m, n) for n in names} for m, names in (
            (ci_daily, ("DATA_DIR", "CONTENT_DIR", "update_manifest", "fetch_semo", "subprocess")),
            (run_daily, ("DATA_DIR", "CONTENT_DIR", "CHART_DIR", "fetch_semo", "load_dam_data", "scaffold_daily",
                         "upload_charts_for_date")),
            (raw_archive, ("DATA_DIR", "MANIFEST")),
            (fetch, ("requests",)),
        )}

        def get(url, params=None, timeout=None):
            day = datetime.strptime(params["dateFrom"], "%d-%b-%Y").date().isoformat()
            area = "wind" if params["chartType"] == "wind" else "demand"
            e.requests_made.append((day, area))
            # Only the target day's answer is revised; earlier days are history a previous run archived.
            return FakeResp(eirgrid_body(day, area, e.body["base"] if day == ISO else 100.0,
                                         e.body["quarters"] if day == ISO else 96))

        def semo(delivery_date=None, out_dir=None):
            stamp = f"{delivery_date - timedelta(days=1):%Y%m%d}"
            p = Path(out_dir) / f"MarketResult_SEM-DA_PWR-MRC-D+1_{stamp}100000_{stamp}105501.csv"
            Path(out_dir).mkdir(parents=True, exist_ok=True)
            if not p.exists():
                p.write_text(f"fixture {stamp}\n")
            return p

        def scaffold(delivery_date, explicit_file=None, title="", eirgrid_df=None, **k):
            post = e.content / "daily" / ISO / "index.md"
            post.parent.mkdir(parents=True, exist_ok=True)
            post.write_text(f"---\ntitle: {title}\n---\nWind % of Demand\n{eirgrid_df.to_csv(index=False)}")

        class InProcessRunDaily:
            """Stands in for the run_daily.py subprocess: runs run_daily.main() with the same argv."""
            def __init__(self, cmd, **kw):
                argv = [*cmd[2:], "--db", str(tmp / "history.db")]
                old, buf = sys.argv, io.StringIO()
                sys.argv = ["run_daily.py", *argv]
                self.returncode = 0
                try:
                    with contextlib.redirect_stdout(buf):
                        try:
                            run_daily.main()
                        except SystemExit as ex:
                            self.returncode = ex.code or 0
                finally:
                    sys.argv = old
                self.stdout = iter(buf.getvalue().splitlines(keepends=True))

            def wait(self):
                return self.returncode

        class FakeSubprocess:
            Popen = InProcessRunDaily
            def __getattr__(self, name):
                return getattr(subprocess, name)

        try:
            ci_daily.DATA_DIR = run_daily.DATA_DIR = raw_archive.DATA_DIR = e.data
            ci_daily.CONTENT_DIR = run_daily.CONTENT_DIR = e.content
            run_daily.CHART_DIR = tmp / "charts"
            raw_archive.MANIFEST = e.manifest
            ci_daily.update_manifest = lambda raw: update_manifest(raw, e.manifest, e.root)
            ci_daily.fetch_semo = run_daily.fetch_semo = semo
            run_daily.load_dam_data = lambda p: price_df(DAY)
            run_daily.scaffold_daily = scaffold
            run_daily.upload_charts_for_date = lambda p: None
            ci_daily.subprocess = FakeSubprocess()
            fetch.requests = type("R", (), {"get": staticmethod(get), "RequestException": Exception,
                                            "HTTPError": Exception})
            e.push = lambda: raw_archive.cmd_push(argparse.Namespace(date=ISO, remote=str(e.remote)))
            e.seed = lambda: raw_archive.cmd_seed(argparse.Namespace(remote=str(e.remote)))
            e.post = e.content / "daily" / ISO / "index.md"
            e.archived = lambda rel: subprocess.run(["git", "--git-dir", str(e.remote), "show", f"main:{rel}"],
                                                    capture_output=True, text=True, check=True).stdout
            e.wipe_runner = lambda: [shutil.rmtree(p, ignore_errors=True) for p in (e.content, e.data)]
            yield e
        finally:
            for m, names in saved.items():
                for n, v in names.items():
                    setattr(m, n, v)
            os.environ.pop("RAW_ARCHIVE_REMOTE", None)


def seed_archive(e, wind_quarters=96, demand_quarters=96):
    """Put EirGrid raw files for the target day (and the day before) into the raw repo, as a seed would."""
    for day in (ISO, (DAY - timedelta(days=1)).isoformat()):
        for area, q in (("wind", wind_quarters), ("demand", demand_quarters)):
            f = e.data / "eirgrid_raw" / day / f"{area}.json"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(eirgrid_body(day, area, 100.0, q) if q else json.dumps({"Rows": []}))
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        e.seed()
    e.wipe_runner()


RAW_DEMAND = f"data/eirgrid_raw/{ISO}/demand.json"


def test_retry_after_raw_push_without_content_push_is_clean_and_byte_identical():
    with ci_env() as e:
        # Run 1: fresh runner. Generate, then push raw, then die before the content push.
        code, out = run_ci(["--date", ISO, "--restore-raw"])
        assert code is None and "STATUS=generated" in out, (code, out)
        first = e.post.read_bytes()
        e.push()
        # The runner is ephemeral: content, data/ and the uncommitted manifest change are gone.
        e.wipe_runner(); e.manifest.write_text("")

        # EirGrid has since revised its answer for the day.
        e.body["base"] = 250.0
        e.requests_made.clear()

        # Run 2: the retry.
        code, out = run_ci(["--date", ISO, "--restore-raw"])
        assert code is None and "STATUS=generated" in out, (code, out)
        assert e.post.read_bytes() == first, "retry produced a different post"
        assert (ISO, "wind") not in e.requests_made and (ISO, "demand") not in e.requests_made, \
            f"retry fetched the target day afresh: {e.requests_made}"

        # And the raw push now agrees with the archive instead of conflicting.
        e.push()


def test_incomplete_unmanifested_archive_is_fetched_live_and_superseded_once():
    for archived_quarters in (0, 40):                  # an empty feed, and a partial one
        with ci_env() as e:
            seed_archive(e, demand_quarters=archived_quarters)
            code, out = run_ci(["--date", ISO, "--restore-raw"])
            assert code is None and "STATUS=generated" in out, (archived_quarters, code, out)
            assert (ISO, "demand") in e.requests_made, "the incomplete archived demand was not fetched live"
            assert (ISO, "wind") not in e.requests_made, "a complete archived file was fetched again"
            assert fetch.archived_halfhours(DAY, "demand", e.data) == 48
            with contextlib.redirect_stdout(io.StringIO()) as log:
                e.push()
            assert "replacing " + RAW_DEMAND in log.getvalue() and "->" in log.getvalue()
            assert len(json.loads(e.archived(RAW_DEMAND))["Rows"]) == 96
            # once: a later run finds a complete archive and fetches nothing for the day
            e.wipe_runner(); e.manifest.write_text(""); e.requests_made.clear()
            code, out = run_ci(["--date", ISO, "--restore-raw"])
            assert code is None and (ISO, "demand") not in e.requests_made, (code, e.requests_made)


def test_incomplete_archive_referenced_by_the_manifest_is_refused():
    with ci_env() as e:
        seed_archive(e, demand_quarters=0)
        pinned = hashlib.sha256(json.dumps({"Rows": []}).encode()).hexdigest()
        e.manifest.write_text(f"{pinned}  {RAW_DEMAND}\n")
        code, out = run_ci(["--date", ISO, "--restore-raw"])
        assert code == 1 and "manifest" in out, (code, out)
        assert json.loads(e.archived(RAW_DEMAND)) == {"Rows": []}, "the archived file was touched"
        # and the push itself refuses, naming the reason, when the local file differs from the pinned one
        (e.data / "eirgrid_raw" / ISO).mkdir(parents=True, exist_ok=True)
        (e.data / "eirgrid_raw" / ISO / "demand.json").write_text(eirgrid_body(ISO, "demand", 100.0))
        (e.data / "eirgrid_raw" / ISO / "wind.json").write_text(eirgrid_body(ISO, "wind", 100.0))
        e.manifest.write_text(f"{pinned}  {RAW_DEMAND}\n")
        try:
            e.push()
            raise AssertionError("push replaced a manifest-referenced file")
        except SystemExit as ex:
            assert "references it" in str(ex), ex
        assert json.loads(e.archived(RAW_DEMAND)) == {"Rows": []}


def test_may_supersede_never_replaces_complete_files_or_with_incomplete_ones():
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        rel = RAW_DEMAND
        full, partial, empty = (d / "full.json", d / "partial.json", d / "empty.json")
        full.write_text(eirgrid_body(ISO, "demand", 100.0))
        partial.write_text(eirgrid_body(ISO, "demand", 100.0, 40))
        empty.write_text(json.dumps({"Rows": []}))
        ok = raw_archive.may_supersede
        assert ok(rel, empty, full, {})[0] and ok(rel, partial, full, {})[0]
        revised = d / "revised.json"
        revised.write_text(eirgrid_body(ISO, "demand", 250.0))                 # complete, but different bytes
        assert not ok(rel, full, revised, {})[0] and "is complete" in ok(rel, full, revised, {})[1]
        assert not ok(rel, full, partial, {})[0]
        assert not ok(rel, empty, partial, {})[0] and "incomplete too" in ok(rel, empty, partial, {})[1]
        assert not ok(rel, empty, full, {rel: raw_archive.sha256(empty)})[0]
        assert ok(rel, empty, full, {rel: raw_archive.sha256(full)})[0]       # the manifest pins the new file, not the old
        assert not ok("data/MarketResult_x.csv", empty, full, {})[0]           # SEMOpx files are never superseded


def test_fetch_keeps_the_archived_file_when_live_is_no_better():
    with ci_env() as e:
        f = e.data / "eirgrid_raw" / ISO / "demand.json"
        f.parent.mkdir(parents=True)
        f.write_text(eirgrid_body(ISO, "demand", 100.0, 40))
        before = f.read_text()
        e.body["quarters"] = 8                                  # live is even thinner
        with contextlib.redirect_stdout(io.StringIO()):
            fetch.fetch_wind_and_demand(DAY, out_dir=e.data, prefer_archive=True)
        assert f.read_text() == before and (ISO, "demand") in e.requests_made


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
