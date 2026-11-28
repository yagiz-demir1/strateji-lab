"""Faz 1 uçtan uca (end-to-end) doğrulama testleri.

Bütün stratejilerin örnek veri dosyalarıyla hatasız çalıştığını ve rapor ürettiğini doğrular.
"""

import pytest
from pathlib import Path
from stratlab.run import main
from stratlab.strategies import STRATEGIES

# Faz 1 kapsamında test edilecek stratejiler ve veri setleri
STRATEGY_NAMES = list(STRATEGIES.keys())
FIXTURES = ["yukselen", "dalgali"]

@pytest.mark.parametrize("strategy_name", STRATEGY_NAMES)
@pytest.mark.parametrize("fixture_name", FIXTURES)
def test_phase1_end_to_end_execution_and_reporting(strategy_name, fixture_name, tmp_path):
    """Her strateji ve fikstür kombinasyonu için backtest çalışmalı ve rapor dosyası oluşmalıdır."""
    # Raporların ve önbelleğin yazılacağı geçici klasörler
    reports_dir = tmp_path / "reports"
    cache_dir = tmp_path / "cache"
    
    # Test verisini sağlayan mock kaynak
    from tests.helpers import load_fixture
    def mock_source(ticker, start, end):
        return load_fixture(fixture_name)

    # Komut satırı argümanları
    # Not: ticker adı rapor dosya adını etkiler
    ticker_code = fixture_name.upper()
    args = [
        "--ticker", ticker_code,
        "--strategy", strategy_name,
        "--start", "2025-01-01",
        "--end", "2025-03-26",
        "--reports-dir", str(reports_dir),
        "--cache-dir", str(cache_dir)
    ]

    # CLI'ı çalıştır
    # main fonksiyonu başarılıysa 0 döndürür
    exit_code = main(args, source=mock_source)

    # 1. Kontrol: Program hatasız sonlanmalı
    assert exit_code == 0, f"{strategy_name} stratejisi {fixture_name} verisiyle hata verdi."

    # 2. Kontrol: Rapor dosyası beklenen isimle oluşmalı
    report_filename = f"{ticker_code}_{strategy_name}.md"
    report_path = reports_dir / report_filename
    assert report_path.exists(), f"Rapor dosyası oluşturulamadı: {report_path}"

    # 3. Kontrol: Rapor içeriği temel bölümleri içermeli
    content = report_path.read_text(encoding="utf-8")
    assert f"# {ticker_code} – {strategy_name}" in content
    assert "| Metrik |" in content
    assert "## İşlem İstatistikleri" in content
    assert "İşlem Sayısı:" in content
    assert "İsabet Oranı:" in content
