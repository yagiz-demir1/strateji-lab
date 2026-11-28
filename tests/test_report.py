"""Markdown raporlama modülü için testler. (G-008)

Backtest sonuçlarını al-tut benchmark'ı ile karşılaştıran raporun
yapısını ve hesaplanan değerlerin doğruluğunu kontrol eder.
"""

import pandas as pd
import pytest
from stratlab.reports.markdown import make_report


def test_make_report_structure():
    """Rapor Markdown formatında başlık, tablo ve metrik isimlerini içermelidir."""
    # Basit test verisi
    strategy = pd.Series([1.0, 1.1, 1.21])
    benchmark = pd.Series([1.0, 1.05, 1.10])

    report = make_report("Test Stratejisi", strategy, benchmark)

    assert isinstance(report, str)
    assert "# Test Stratejisi" in report
    # Tablo başlıkları
    assert "| Metrik | Strateji | Al-tut | Fark |" in report
    # Metrik isimleri (G-006)
    assert "Toplam Getiri" in report
    assert "Yıllık Getiri" in report
    assert "Yıllık Volatilite" in report
    assert "Sharpe Oranı" in report
    assert "En Büyük Düşüş" in report


def test_make_report_calculation_and_formatting():
    """Rapordaki değerler doğru hesaplanmalı ve %2 formatında olmalıdır."""
    # Toplam getiri: Strateji %21.00, Al-tut %10.00. Fark %11.00
    strategy = pd.Series([1.0, 1.1, 1.21])
    benchmark = pd.Series([1.0, 1.05, 1.10])

    report = make_report("Hesaplama Testi", strategy, benchmark)

    # Yüzdelik değerlerin formatta varlığını kontrol et
    assert "%21.00" in report
    assert "%10.00" in report
    assert "%11.00" in report


def test_make_report_sharpe_and_drawdown_values():
    """Yüzde olmayan metriklerin (Sharpe) ve negatif değerlerin (MDD) formatını kontrol eder."""
    # MDD: (0.9 / 1.2) - 1 = -0.25 -> -%25.00
    strategy = pd.Series([1.0, 1.2, 0.9, 1.1])
    # Al-tut sabit kalsın
    benchmark = pd.Series([1.0, 1.0, 1.0, 1.0])

    report = make_report("Detay Testi", strategy, benchmark)

    # En büyük düşüş kontrolü
    assert "-%25.00" in report
    # Sharpe oranı tablodaki yerini kontrol et
    assert "Sharpe Oranı" in report
