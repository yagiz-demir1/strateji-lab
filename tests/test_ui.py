"""Streamlit arayüzü ve mantığı için testler (G-019)."""

import pytest
import pandas as pd
from pathlib import Path
from streamlit.testing.v1 import AppTest
from stratlab.ui.logic import run_selected


def test_run_selected_returns_expected_structure(tmp_path):
    """run_selected fonksiyonu strateji ve al-tut equity verilerini ve metrikleri döndürmelidir."""
    # Sahte veri
    dates = pd.date_range("2024-01-01", periods=30)
    fake_df = pd.DataFrame({
        "open": [100.0] * 30,
        "high": [101.0] * 30,
        "low": [99.0] * 30,
        "close": [100.0 + i for i in range(30)],
        "volume": [1000] * 30
    }, index=dates)
    
    source = lambda t, s, e: fake_df
    
    result = run_selected(
        ticker="THYAO.IS",
        strategy="ma_crossover",
        start="2024-01-01",
        end="2024-01-30",
        cost_bps=10.0,
        source=source,
        cache_dir=str(tmp_path / "cache"),
    )
    
    assert "strat_equity" in result
    assert "bench_equity" in result
    assert "metrics" in result
    assert isinstance(result["strat_equity"], pd.Series)
    assert isinstance(result["bench_equity"], pd.Series)
    assert isinstance(result["metrics"], dict)
    
    # Metriklerin varlığını kontrol et
    expected_metrics = [
        "Toplam Getiri", 
        "Al-tut Toplam Getiri", 
        "Yıllık Getiri", 
        "Yıllık Volatilite", 
        "Sharpe Oranı", 
        "En Büyük Düşüş", 
        "İşlem Sayısı", 
        "İsabet Oranı"
    ]
    for m in expected_metrics:
        assert m in result["metrics"]


def test_ui_app_basic_elements():
    """Streamlit uygulamasının temel bileşenlerinin varlığını kontrol eder."""
    app_path = Path(__file__).parent.parent / "src" / "stratlab" / "ui" / "app.py"
    at = AppTest.from_file(str(app_path))
    at.run()

    # Kenar çubuğu kontrolleri
    # selectbox'lar
    labels = [s.label for s in at.sidebar.selectbox]
    assert any("Varlık" in l or "Ticker" in l for l in labels)
    assert any("Strateji" in l for l in labels)
    
    # date_input'lar
    date_labels = [d.label for d in at.sidebar.date_input]
    assert any("Başlangıç" in l for l in date_labels)
    
    # number_input'lar
    num_labels = [n.label for n in at.sidebar.number_input]
    assert any("Maliyet" in l or "baz puan" in l for l in num_labels)
    
    # Uygulama hatasız açılmalı ve kenar çubuğunda tek bir "Çalıştır" düğmesi olmalı
    assert not at.exception
    assert len(at.sidebar.button) == 1
    assert at.sidebar.button[0].label == "Çalıştır"
