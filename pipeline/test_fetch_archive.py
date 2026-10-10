"""Tests that a non-empty raw EirGrid archive is never replaced by an empty response.
Run: python pipeline/test_fetch_archive.py   (temp directory only; requests.get is faked, no network)"""

import hashlib
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fetch

D = date(2026, 10, 2)
GOOD = json.dumps({"Rows": [{"EffectiveTime": "02-Oct-2026 00:00:00", "FieldName": "SYSTEM_DEMAND", "Region": "ROI", "Value": 3700}]})
EMPTY = '{"Rows":[]}'


class FakeResp:
    status_code = 200

    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass

    def json(self):
        return json.loads(self.text)


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def with_response(text, fn):
    saved = fetch.requests.get
    fetch.requests.get = lambda *a, **k: FakeResp(text)
    try:
        return fn()
    finally:
        fetch.requests.get = saved


def archive(tmp: Path, content: str | None) -> Path:
    p = fetch.archive_path(D, "demand", tmp)
    if content is not None:
        p.parent.mkdir(parents=True)
        p.write_text(content)
    return p


def test_empty_response_never_replaces_a_non_empty_archive_in_any_mode():
    for label, call in (
        ("run_daily default (overwrite_raw=True)", lambda t: fetch.fetch_area(D, "demand", out_dir=t)),
        ("fetch_wind_and_demand default", lambda t: fetch.fetch_wind_and_demand(D, out_dir=t)),
        ("backfill (overwrite_raw=False)", lambda t: fetch.fetch_area(D, "demand", out_dir=t, overwrite_raw=False)),
        ("heal (overwrite_raw=False, raise_errors)", lambda t: fetch.fetch_area(D, "demand", out_dir=t, overwrite_raw=False, raise_errors=True)),
    ):
        with tempfile.TemporaryDirectory() as t:
            p = archive(Path(t), GOOD)
            before = md5(p)
            with_response(EMPTY, lambda: call(Path(t)))
            assert md5(p) == before and archive_rows(p) == 1, label


def archive_rows(p: Path) -> int:
    return fetch.archive_row_count(p)


def test_non_json_response_does_not_replace_a_non_empty_archive_either():
    with tempfile.TemporaryDirectory() as t:
        p = archive(Path(t), GOOD)
        before = md5(p)
        saved = fetch.requests.get
        class Html(FakeResp):
            def json(self):
                raise ValueError("not json")
        fetch.requests.get = lambda *a, **k: Html("<html>maintenance</html>")
        try:
            fetch.fetch_area(D, "demand", out_dir=t)
        finally:
            fetch.requests.get = saved
        assert md5(p) == before


def test_a_response_with_rows_still_fills_a_missing_or_empty_archive():
    for start in (None, EMPTY):
        for overwrite in (True, False):
            with tempfile.TemporaryDirectory() as t:
                p = archive(Path(t), start)
                with_response(GOOD, lambda: fetch.fetch_area(D, "demand", out_dir=t, overwrite_raw=overwrite))
                assert p.read_text() == GOOD, (start, overwrite)


def test_run_daily_default_still_records_an_empty_response_where_there_is_no_archive():
    with tempfile.TemporaryDirectory() as t:
        p = archive(Path(t), None)
        with_response(EMPTY, lambda: fetch.fetch_area(D, "demand", out_dir=t))
        assert p.read_text() == EMPTY                       # unchanged behaviour: the failed fetch is on record
        p2 = archive(Path(t) / "b", None)
        with_response(EMPTY, lambda: fetch.fetch_area(D, "demand", out_dir=Path(t) / "b", overwrite_raw=False))
        assert not p2.exists()                              # backfill/heal still write nothing


def test_run_daily_default_replaces_a_non_empty_archive_with_a_non_empty_response():
    with tempfile.TemporaryDirectory() as t:
        p = archive(Path(t), GOOD)
        newer = GOOD.replace("3700", "3800")
        with_response(newer, lambda: fetch.fetch_area(D, "demand", out_dir=t))
        assert p.read_text() == newer


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
