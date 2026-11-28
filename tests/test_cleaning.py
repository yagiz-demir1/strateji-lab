"""Veri temizliği (G-023) için testler.

Kapanış fiyatı olmayan veya pozitif olmayan (sıfır/negatif) günlerin
ayıklanmasını ve raporlanmasını kontrol eder.
"""

import pandas as pd
import pytest
import numpy as np
from stratlab.data.cleaning import clean_prices
from stratlab.ui.logic import run_selected
from stratlab.run import main


def test_clean_prices_removes_invalid_rows():
    """Kapanışı NaN, 0 veya negatif olan satırlar atılmalı ve Türkçe notlar dönmelidir."""
    dates = pd.date_range("2020-04-17", periods=5)
    df = pd.DataFrame({
        "open": [10, 10, 10, 10, 10],
        "high": [11, 11, 11, 11, 11],
        "low": [9, 9, 9, 9, 9],
        "close": [10.0, -5.0, 0.0, np.nan, 12.0],
        "volume": [100, 100, 100, 100, 100]
    }, index=dates)
    
    cleaned_df, notes = clean_prices(df)
    
    # 2 satır kalmalı (10.0 ve 12.0)
    assert len(cleaned_df) == 2
    assert list(cleaned_df["close"]) == [10.0, 12.0]
    
    # G-023 şartı: Her neden için bir not. 
    # "1 gün atıldı: kapanış ≤ 0 (2020-04-20)" gibi.
    assert len(notes) == 2
    assert any("kapanış ≤ 0" in note for note in notes)
    assert any("kapanış boş" in note for note in notes)


def test_clean_prices_returns_empty_notes_for_clean_data():
    """Bütün kapanışları > 0 olan veride hiçbir satır atılmamalı ve not listesi boş olmalı."""
    dates = pd.date_range("2024-01-01", periods=3)
    df = pd.DataFrame({
        "open": [10, 11, 12],
        "high": [11, 12, 13],
        "low": [9, 10, 11],
        "close": [10.5, 11.5, 12.5],
        "volume": [100, 100, 100]
    }, index=dates)
    
    cleaned_df, notes = clean_prices(df)
    
    assert len(cleaned_df) == 3
    assert len(notes) == 0
    pd.testing.assert_frame_equal(cleaned_df, df)


def test_run_selected_uses_cleaning_and_includes_notes():
    """run_selected sonucu 'notes' anahtarını içermeli ve hatalı veride getiriler makul olmalıdır."""
    def mock_bad_source(ticker, start, end):
        # 2020-04-20 tarihinde negatif kapanış (WTI örneği)
        dates = pd.date_range(start, periods=5)
        return pd.DataFrame({
            "open": [100, 100, 100, 100, 100],
            "high": [110, 110, 110, 110, 110],
            "low": [90, 90, 90, 90, 90],
            "close": [100.0, -37.63, 100.0, 100.0, 100.0],
            "volume": [1000, 1000, 1000, 1000, 1000]
        }, index=dates)

    result = run_selected(
        ticker="CL=F",
        strategy="ma_crossover",
        start="2020-04-19",
        end="2020-04-24",
        cost_bps=0.0,
        source=mock_bad_source
    )
    
    # G-023: "run_selected sonucuna 'notes' anahtarı eklenir"
    assert "notes" in result
    assert isinstance(result["notes"], list)
    assert len(result["notes"]) > 0
    
    # Negatif fiyat temizlendiği için getiriler -%100'ün altına düşmemeli
    assert result["metrics"]["Toplam Getiri"] > -1.0
    assert result["metrics"]["Al-tut Toplam Getiri"] > -1.0


def test_cli_includes_data_notes_in_report(tmp_path):
    """Komut satırı raporu veri notlarını '## Veri notları' başlığıyla içermelidir."""
    reports_dir = tmp_path / "reports"
    
    def mock_bad_source(ticker, start, end):
        dates = pd.date_range(start, periods=3)
        return pd.DataFrame({
            "open": [10, 10, 10],
            "high": [11, 11, 11],
            "low": [9, 9, 9],
            "close": [10.0, np.nan, 11.0],
            "volume": [100, 100, 100]
        }, index=dates)

    args = [
        "--ticker", "BAD_DATA",
        "--strategy", "ma_crossover",
        "--start", "2024-01-01",
        "--reports-dir", str(reports_dir)
    ]

    exit_code = main(args, source=mock_bad_source)
    assert exit_code == 0
    
    report_file = reports_dir / "BAD_DATA_ma_crossover.md"
    content = report_file.read_text(encoding="utf-8")
    
    # G-023: başlık ve not içeriği raporda olmalı
    assert "## Veri notları" in content
    assert "kapanış boş" in content


def test_cli_no_data_notes_header_if_clean(tmp_path):
    """Temiz veriyle çalışıldığında raporda Veri notları başlığı bulunmamalıdır."""
    reports_dir = tmp_path / "reports"
    
    def mock_clean_source(ticker, start, end):
        dates = pd.date_range(start, periods=3)
        return pd.DataFrame({
            "open": [10, 11, 12],
            "high": [11, 12, 13],
            "low": [9, 10, 11],
            "close": [10.5, 11.5, 12.5],
            "volume": [100, 100, 100]
        }, index=dates)

    args = [
        "--ticker", "CLEAN_DATA",
        "--strategy", "ma_crossover",
        "--start", "2024-01-01",
        "--reports-dir", str(reports_dir)
    ]

    main(args, source=mock_clean_source)
    
    report_file = reports_dir / "CLEAN_DATA_ma_crossover.md"
    content = report_file.read_text(encoding="utf-8")
    
    assert "## Veri notları" not in content
