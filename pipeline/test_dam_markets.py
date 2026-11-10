"""load_dam_data prices the ROI-DA EUR index block by name and refuses a file where NI-DA differs.
Run: python pipeline/test_dam_markets.py   (synthetic files in a temp directory; the real-file tests are skipped
when data/ or /tmp/semo-dl does not hold the files)"""

import glob
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from process import load_dam_data, KNOWN_NI_ROI_ROUNDING
from trading_day import expected_periods, period_starts_utc

DELIVERY = date(2026, 11, 3)


def _cell(v) -> str:
    return f"{v:.2f}".replace(".", ",")


def write_file(tmp: Path, delivery=DELIVERY, ni=None, roi=None, order=("NI-DA", "ROI-DA"), gbp_first=False,
               ni_block=True, roi_block=True) -> Path:
    """A SEM-DA file with one Index prices block per market. Values are cells already (strings) or floats."""
    n = expected_periods(delivery)
    base = [100.0 + p for p in range(1, n + 1)]
    ni = [_cell(v) if not isinstance(v, str) else v for v in (ni if ni is not None else base)]
    roi = [_cell(v) if not isinstance(v, str) else v for v in (roi if roi is not None else base)]
    ts = ";".join(t.strftime("%Y-%m-%dT%H:%M:%SZ") for t in period_starts_utc(delivery))
    lines = ["Auction;SEM-DA", "Auction name;PWR-MRC-D+1", f"Auction date time;{date.fromordinal(delivery.toordinal() - 1)}T11:00:00Z",
             "FX rates", "EUR;GBP;0,83563132"]
    for market, vals, present in (("NI-DA", ni, ni_block), ("ROI-DA", roi, roi_block)):
        lines.append(f"Market;{market}")
        if not present:
            lines.append("Index volumes;30"); lines.append(ts); lines.append(";".join(["1,0"] * n))
            continue
        if gbp_first:
            lines += ["Index prices;30;GBP", ts, ";".join(["1,00"] * n)]
        lines += ["Index prices;30;EUR", ts, ";".join(vals)]
    if order == ("ROI-DA", "NI-DA"):                       # the markets the other way round
        head, ni_part, roi_part = lines[:5], None, None
        i = lines.index("Market;ROI-DA")
        lines = head + lines[i:] + lines[5:i]
    path = tmp / "MarketResult_SEM-DA_PWR-MRC-D+1_test.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def raises(path, *needles) -> str:
    try:
        load_dam_data(path)
    except ValueError as e:
        msg = str(e)
        for n in needles:
            assert n in msg, (n, msg)
        return msg
    raise AssertionError("load_dam_data accepted the file")


def test_agreeing_markets_load_the_roi_prices():
    with tempfile.TemporaryDirectory() as t:
        df = load_dam_data(write_file(Path(t)))
        assert len(df) == 48 and df["DAMPrice_EUR_MWh"].tolist() == [100.0 + p for p in range(1, 49)]


def test_a_gbp_block_is_never_read_as_the_price():
    with tempfile.TemporaryDirectory() as t:
        df = load_dam_data(write_file(Path(t), gbp_first=True))
        assert df["DAMPrice_EUR_MWh"].iloc[0] == 101.0


def test_split_market_raises_naming_the_date_and_every_differing_period():
    base = [100.0 + p for p in range(1, 49)]
    ni = list(base); ni[6] += 5; ni[19] -= 40.25
    with tempfile.TemporaryDirectory() as t:
        msg = raises(write_file(Path(t), ni=ni), "2026-11-03", "period 7 (NI-DA 112,00 vs ROI-DA 107,00)",
                     "20 (NI-DA 79,75 vs ROI-DA 120,00)", "split")
        assert "period 8" not in msg and "21 (" not in msg, msg


def test_roi_is_selected_by_name_not_position():
    d = date(2025, 12, 17)                                  # 57,01 / 57,00 in period 11 is a listed rounding difference
    n = expected_periods(d)
    base = [100.0 + p for p in range(1, n + 1)]
    ni = [_cell(v) for v in base]; roi = list(ni)
    ni[10], roi[10] = "57,01", "57,00"
    with tempfile.TemporaryDirectory() as t:
        for order in (("NI-DA", "ROI-DA"), ("ROI-DA", "NI-DA")):
            df = load_dam_data(write_file(Path(t), delivery=d, ni=ni, roi=roi, order=order))
            assert df["DAMPrice_EUR_MWh"].iloc[10] == 57.00, order       # ROI, whichever block comes first


def test_a_listed_period_with_any_other_values_still_raises():
    d = date(2025, 12, 17)
    base = [_cell(100.0 + p) for p in range(1, expected_periods(d) + 1)]
    for ni_cell, roi_cell in (("57,02", "57,00"), ("57,01", "57,01"), ("58,00", "57,00"), ("57,00", "57,01")):
        ni, roi = list(base), list(base)
        ni[10], roi[10] = ni_cell, roi_cell
        with tempfile.TemporaryDirectory() as t:
            if ni_cell == roi_cell:
                assert load_dam_data(write_file(Path(t), delivery=d, ni=ni, roi=roi)) is not None
            else:
                raises(write_file(Path(t), delivery=d, ni=ni, roi=roi), "2025-12-17", "period 11")
    ni, roi = list(base), list(base)                          # the listed pair in a different period is not listed
    ni[11], roi[11] = "57,01", "57,00"
    with tempfile.TemporaryDirectory() as t:
        raises(write_file(Path(t), delivery=d, ni=ni, roi=roi), "period 12")


def test_missing_market_blocks_raise():
    with tempfile.TemporaryDirectory() as t:
        raises(write_file(Path(t), roi_block=False), "ROI-DA")
    with tempfile.TemporaryDirectory() as t:
        raises(write_file(Path(t), ni_block=False), "NI-DA", "2026-11-03")


def test_a_short_ni_block_names_the_missing_period():
    base = [100.0 + p for p in range(1, 49)]
    with tempfile.TemporaryDirectory() as t:
        raises(write_file(Path(t), ni=base[:47]), "2026-11-03", "period 48 (NI-DA missing vs ROI-DA 148,00)")


def _real_files(pattern):
    return sorted(glob.glob(pattern))


def test_the_listed_rounding_files_in_data_load_with_the_roi_price():
    data = Path(__file__).parent.parent / "data"
    want = {"20251216": ((11, 57.00)), "20260307": (45, 173.08), "20260316": (33, 85.66), "20260322": (39, 178.71)}
    found = 0
    for tag, (period, roi_price) in want.items():
        files = _real_files(str(data / f"MarketResult_SEM-DA_PWR-MRC-D+1_{tag}*.csv"))
        if not files:
            continue
        found += 1
        assert load_dam_data(Path(files[-1])).set_index("Period").loc[period, "DAMPrice_EUR_MWh"] == roi_price, tag
    if not found:
        print("  (skipped: no real data/ files)")
    assert len(KNOWN_NI_ROI_ROUNDING) == len(want)


def test_the_three_downloaded_semopx_files_load_and_agree():
    expected = {"20261029": 239.6442, "20261030": 339.0954, "20261102": 488.4533}   # deliveries 10-30, 10-31, 11-03
    files = _real_files("/tmp/semo-dl/MarketResult_SEM-DA_PWR-MRC-D+1_*.csv")
    if not files:
        print("  (skipped: /tmp/semo-dl has no files)")
        return
    for f in files:
        tag = Path(f).name.split("_")[-2][:8]
        if tag in expected:
            df = load_dam_data(Path(f))
            assert len(df) == 48 and abs(df["DAMPrice_EUR_MWh"].mean() - expected[tag]) < 1e-3, (tag, df["DAMPrice_EUR_MWh"].mean())


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
