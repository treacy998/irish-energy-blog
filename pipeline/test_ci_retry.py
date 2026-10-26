"""Test that a CI run which dies after the raw push and before the content push is retried cleanly:
the retry generates from the archived raw bytes (no fresh fetch for the day), the raw push sees no
hash conflict, and the post is byte-identical.
Run: python pipeline/test_ci_retry.py   (temp directories and a local bare git repo; requests.get is faked, no network)

Real: ci_daily.main, raw_archive restore/push (git), fetch.fetch_wind_and_demand, run_daily.main.
Stubbed: the SEMOpx download, the DAM CSV parse, the chart/post scaffold (writes a post that embeds the
EirGrid frame it was given, so a different EirGrid response would change the post bytes)."""

import argparse
import contextlib
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


def eirgrid_body(day: str, area: str, base: float) -> str:
    """One calendar day of hourly rows (the 30-minute resampler fills between them)."""
    d = date.fromisoformat(day).strftime("%d-%b-%Y")
    fields = ["WIND_ACTUAL", "WIND_FCAST"] if area == "wind" else ["SYSTEM_DEMAND"]
    rows = [{"EffectiveTime": f"{d} {h:02d}:00:00", "FieldName": f, "Region": "ROI",
             "Value": (base + h) if f != "SYSTEM_DEMAND" else 4000.0 + h}
            for h in range(24) for f in fields]
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


def test_retry_after_raw_push_without_content_push_is_clean_and_byte_identical():
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        data, content, root = tmp / "data", tmp / "site" / "content", tmp
        manifest = tmp / "data-manifest.sha256"
        manifest.write_text("")
        remote = tmp / "raw.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
        os.environ["RAW_ARCHIVE_REMOTE"] = str(remote)

        saved = {m: {n: getattr(m, n) for n in names} for m, names in (
            (ci_daily, ("DATA_DIR", "CONTENT_DIR", "update_manifest", "fetch_semo", "subprocess")),
            (run_daily, ("DATA_DIR", "CONTENT_DIR", "CHART_DIR", "fetch_semo", "load_dam_data", "scaffold_daily",
                         "upload_charts_for_date")),
            (raw_archive, ("DATA_DIR", "MANIFEST")),
            (fetch, ("requests",)),
        )}
        requests_made = []
        body = {"base": 100.0}

        def get(url, params=None, timeout=None):
            day = datetime.strptime(params["dateFrom"], "%d-%b-%Y").date().isoformat()
            area = "wind" if params["chartType"] == "wind" else "demand"
            requests_made.append((day, area))
            # Only the target day's answer is revised; earlier days are history a previous run archived.
            return FakeResp(eirgrid_body(day, area, body["base"] if day == ISO else 100.0))

        def semo(delivery_date=None, out_dir=None):
            stamp = f"{delivery_date - timedelta(days=1):%Y%m%d}"
            p = Path(out_dir) / f"MarketResult_SEM-DA_PWR-MRC-D+1_{stamp}100000_{stamp}105501.csv"
            Path(out_dir).mkdir(parents=True, exist_ok=True)
            if not p.exists():
                p.write_text(f"fixture {stamp}\n")
            return p

        def scaffold(delivery_date, explicit_file=None, title="", eirgrid_df=None, **k):
            post = content / "daily" / ISO / "index.md"
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
                        except SystemExit as e:
                            self.returncode = e.code or 0
                finally:
                    sys.argv = old
                self.stdout = iter(buf.getvalue().splitlines(keepends=True))

            def wait(self):
                return self.returncode

        class FakeSubprocess:
            Popen = InProcessRunDaily
            def __getattr__(self, name):
                return getattr(subprocess, name)
        fake_subprocess = FakeSubprocess()

        try:
            ci_daily.DATA_DIR = run_daily.DATA_DIR = raw_archive.DATA_DIR = data
            ci_daily.CONTENT_DIR = run_daily.CONTENT_DIR = content
            run_daily.CHART_DIR = tmp / "charts"
            raw_archive.MANIFEST = manifest
            ci_daily.update_manifest = lambda raw: update_manifest(raw, manifest, root)
            ci_daily.fetch_semo = run_daily.fetch_semo = semo
            run_daily.load_dam_data = lambda p: price_df(DAY)
            run_daily.scaffold_daily = scaffold
            run_daily.upload_charts_for_date = lambda p: None
            ci_daily.subprocess = fake_subprocess
            fetch.requests = type("R", (), {"get": staticmethod(get), "RequestException": Exception,
                                            "HTTPError": Exception})

            # Run 1: fresh runner. Generate, then push raw, then die before the content push.
            code, out = run_ci(["--date", ISO, "--restore-raw"])
            assert code is None and "STATUS=generated" in out, (code, out)
            post = content / "daily" / ISO / "index.md"
            first = post.read_bytes()
            raw_archive.cmd_push(argparse.Namespace(date=ISO, remote=str(remote)))
            # The runner is ephemeral: content, data/ and the uncommitted manifest change are gone.
            shutil.rmtree(content); shutil.rmtree(data); manifest.write_text("")

            # EirGrid has since revised its answer for the day.
            body["base"] = 250.0
            requests_made.clear()

            # Run 2: the retry.
            code, out = run_ci(["--date", ISO, "--restore-raw"])
            assert code is None and "STATUS=generated" in out, (code, out)
            assert post.read_bytes() == first, "retry produced a different post"
            assert (ISO, "wind") not in requests_made and (ISO, "demand") not in requests_made, \
                f"retry fetched the target day afresh: {requests_made}"

            # And the raw push now agrees with the archive instead of conflicting.
            raw_archive.cmd_push(argparse.Namespace(date=ISO, remote=str(remote)))
        finally:
            for m, names in saved.items():
                for n, v in names.items():
                    setattr(m, n, v)
            os.environ.pop("RAW_ARCHIVE_REMOTE", None)


if __name__ == "__main__":
    test_retry_after_raw_push_without_content_push_is_clean_and_byte_identical()
    print("ok test_retry_after_raw_push_without_content_push_is_clean_and_byte_identical")
