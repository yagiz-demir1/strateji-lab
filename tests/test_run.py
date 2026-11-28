"""G-018: Komut satırı arayüzü (CLI) için backtest testleri.

Stratejilerin komut satırından çalıştırılmasını, rapor üretilmesini,
veri temizliğini ve hatalı parametre yönetimini doğrular.
"""

import os
import pytest
import pandas as pd
from pathlib import Path
from stratlab.run import main


def create_fake_source(df: pd.DataFrame):
    """load_prices için sahte veri kaynağı döndüren yardımcı fonksiyon."""
    return lambda ticker, start, end: df


@pytest.fixture
def sample_data():
    """Testler için 60 günlük basit bir fiyat serisi. SMA ve RSI için yeterli veri."""
    dates = pd.date_range("2024-01-01", periods=60)
    # Fiyat sürekli artıyor (yükselen trend)
    return pd.DataFrame(
        {
            "open": [float(i + 100) for i in range(60)],
            "high": [float(i + 101) for i in range(60)],
            "low": [float(i + 99) for i in range(60)],
            "close": [float(i + 100) for i in range(60)],
            "volume": [1000] * 60,
        },
        index=dates,
    )


def test_main_creates_report_file(tmp_path, sample_data):
    """Geçerli argümanlarla main fonksiyonu rapor dosyası oluşturmalı ve içeriği doğru olmalıdır."""
    reports_dir = tmp_path / "reports"
    source = create_fake_source(sample_data)

    args = [
        "--ticker",
        "THYAO.IS",
        "--strategy",
        "ma_crossover",
        "--start",
        "2024-01-01",
        "--reports-dir",
        str(reports_dir),
    ]

    exit_code = main(args, source=source)

    assert exit_code == 0
    report_path = reports_dir / "THYAO.IS_ma_crossover.md"
    assert report_path.exists()

    content = report_path.read_text(encoding="utf-8")
    assert "# THYAO.IS – ma_crossover" in content

    # G-017 metriklerinin (işlem sayısı ve isabet oranı) eklendiğini kontrol et
    assert "İşlem Sayısı" in content
    assert "İsabet Oranı" in content


def test_main_unknown_strategy_returns_2(sample_data):
    """Bilinmeyen bir strateji adı verildiğinde fonksiyon 2 koduyla dönmelidir."""
    source = create_fake_source(sample_data)
    args = ["--ticker", "AAPL", "--strategy", "gecersiz_strat", "--start", "2024-01-01"]

    exit_code = main(args, source=source)
    assert exit_code == 2


def test_main_handles_nan_prices_in_data(tmp_path, sample_data):
    """Kapanış fiyatında NaN olan satırlar temizlenerek hesaplama yapılabilmelidir."""
    # Verinin ortasına 5 günlük NaN ekleyelim
    data_with_nan = sample_data.copy()
    data_with_nan.iloc[10:15, data_with_nan.columns.get_loc("close")] = float("nan")

    reports_dir = tmp_path / "reports"
    source = create_fake_source(data_with_nan)

    args = [
        "--ticker",
        "NAN_TEST",
        "--strategy",
        "ma_crossover",
        "--start",
        "2024-01-01",
        "--reports-dir",
        str(reports_dir),
    ]

    exit_code = main(args, source=source)
    assert exit_code == 0

    report_path = reports_dir / "NAN_TEST_ma_crossover.md"
    content = report_path.read_text(encoding="utf-8")

    # NaN'lar temizlenmişse metrikler hesaplanabilmiş olmalı
    assert "| Toplam Getiri | %" in content
    assert "| Toplam Getiri | N/A" not in content


def test_main_cli_execution_simulation(tmp_path, sample_data):
    """Farklı strateji adlarının (STRATEGIES sözlüğündekiler) çalıştığını doğrular."""
    source = create_fake_source(sample_data)
    reports_dir = tmp_path / "reports"

    for strat_name in ["ma_crossover", "rsi_reversion", "momentum_12_1", "bollinger_breakout", "macd"]:
        args = [
            "--ticker",
            "TEST",
            "--strategy",
            strat_name,
            "--start",
            "2024-01-01",
            "--reports-dir",
            str(reports_dir),
        ]
        exit_code = main(args, source=source)
        assert exit_code == 0
        assert (reports_dir / f"TEST_{strat_name}.md").exists()
