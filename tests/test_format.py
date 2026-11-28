"""Sayı ve yüzde formatlama fonksiyonları için testler (G-024)."""

import numpy as np
import pytest
from stratlab.reports.format import fmt_pct, fmt_num

def test_fmt_pct_basic():
    """Pozitif yüzdeyi Türkçe formatta yazmalıdır."""
    assert fmt_pct(0.2112) == "%21,12"

def test_fmt_pct_negative():
    """Negatif yüzdeyi Türkçe formatta (işaret başta) yazmalıdır."""
    assert fmt_pct(-0.25) == "-%25,00"

def test_fmt_pct_negative_zero_suppression():
    """Eksi sıfır durumunda eksi işareti gösterilmemelidir."""
    # -0.00001 * 100 = -0.001 -> yuvarlanınca 0.00
    assert fmt_pct(-0.00001) == "%0,00"

def test_fmt_pct_thousands_separator():
    """Yüzde değerinde binlik ayırıcı (nokta) kullanılmalıdır."""
    # 12.345 * 100 = 1234.5 -> %1.234,50
    assert fmt_pct(12.345) == "%1.234,50"

def test_fmt_pct_nan():
    """NaN değeri için tire (–) döndürmelidir."""
    assert fmt_pct(np.nan) == "–"

def test_fmt_num_basic():
    """Sayıları Türkçe formatta (ondalık virgül) yazmalıdır."""
    assert fmt_num(1.234) == "1,23"

def test_fmt_num_negative_zero():
    """Sayısal değerlerde eksi sıfır gösterilmemelidir."""
    assert fmt_num(-0.004) == "0,00"

def test_fmt_num_nan():
    """NaN sayısal değeri için tire (–) döndürmelidir."""
    assert fmt_num(np.nan) == "–"

def test_fmt_pct_isabet_orani_check():
    """İsabet oranı gibi değerler için %50,00 gibi format üretmelidir."""
    assert fmt_pct(0.5) == "%50,00"


def test_fmt_infinite_values_return_dash():
    """Sonsuz değerler (ör. sıfır volatilitede) hata vermeden tire (–) olarak yazılır."""
    assert fmt_pct(float("inf")) == "–"
    assert fmt_num(float("-inf")) == "–"


def test_cli_report_writes_hit_rate_in_turkish_format(tmp_path):
    """Komut satırı raporunda isabet oranı Türkçe biçimde (ör. %50,00) yazılır."""
    import re
    import pandas as pd
    from stratlab.run import main

    def wave_source(ticker, start, end):
        dates = pd.bdate_range(start, periods=300)
        close = 100 + 10 * np.sin(np.arange(300) / 8.0)
        return pd.DataFrame(
            {"open": close, "high": close, "low": close, "close": close, "volume": 1000},
            index=dates,
        )

    args = ["--ticker", "WAVE", "--strategy", "macd", "--start", "2024-01-01", "--end", "2025-03-01",
            "--reports-dir", str(tmp_path / "reports"), "--cache-dir", str(tmp_path / "cache")]
    assert main(args, source=wave_source) == 0
    content = (tmp_path / "reports" / "WAVE_macd.md").read_text(encoding="utf-8")
    match = re.search(r"\*\*İsabet Oranı:\*\* (\S+)", content)
    assert match is not None
    assert re.fullmatch(r"%\d{1,3}(\.\d{3})*,\d{2}", match.group(1))
