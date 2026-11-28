'''G-028 karşılaştırma sayfası için otomatik testler.'''

import pandas as pd
import pytest
from stratlab.ui.compare import comparison_frame, beat_count, sharpe_diff_pivot


def test_comparison_frame_filters_and_sorts():
    """comparison_frame hatasız satırları seçer, yeterli işlem sütununu ekler ve Sharpe farkına göre sıralar."""
    runs_data = [
        {
            "ticker": "THYAO.IS",
            "grp": "bist",
            "strategy": "ma_crossover",
            "total_return": 0.20,
            "bench_total_return": 0.10,
            "sharpe": 1.2,
            "bench_sharpe": 0.8,
            "max_drawdown": -0.15,
            "trades": 35,
            "error": None,
        },
        {
            "ticker": "ASELS.IS",
            "grp": "bist",
            "strategy": "macd",
            "total_return": 0.05,
            "bench_total_return": 0.15,
            "sharpe": 0.5,
            "bench_sharpe": 1.0,
            "max_drawdown": -0.20,
            "trades": 29,
            "error": None,
        },
        {
            "ticker": "AAPL",
            "grp": "nasdaq",
            "strategy": "ma_crossover",
            "total_return": 0.30,
            "bench_total_return": 0.20,
            "sharpe": 1.5,
            "bench_sharpe": 1.1,
            "max_drawdown": -0.10,
            "trades": 40,
            "error": None,
        },
        {
            "ticker": "MSFT",
            "grp": "nasdaq",
            "strategy": "macd",
            "total_return": 0.10,
            "bench_total_return": 0.10,
            "sharpe": 0.8,
            "bench_sharpe": 0.9,
            "max_drawdown": -0.12,
            "trades": 31,
            "error": None,
        },
        {
            "ticker": "BAD.IS",
            "grp": "bist",
            "strategy": "ma_crossover",
            "total_return": None,
            "bench_total_return": None,
            "sharpe": None,
            "bench_sharpe": None,
            "max_drawdown": None,
            "trades": None,
            "error": "Bağlantı hatası",
        },
    ]
    runs_df = pd.DataFrame(runs_data)

    frame = comparison_frame(runs_df)
    assert len(frame) == 4

    expected_cols = [
        "Grup",
        "Varlık",
        "Strateji",
        "Strateji getirisi",
        "Al-tut getirisi",
        "Getiri farkı",
        "Sharpe",
        "Al-tut Sharpe",
        "Sharpe farkı",
        "En büyük düşüş",
        "İşlem",
        "Yeterli işlem",
    ]
    for col in expected_cols:
        assert col in frame.columns

    sharpe_diffs = frame["Sharpe farkı"].tolist()
    assert sharpe_diffs == sorted(sharpe_diffs, reverse=True)

    asels_row = frame[frame["Varlık"].str.contains("ASELS")]
    assert bool(asels_row["Yeterli işlem"].iloc[0]) is False

    thyao_row = frame[frame["Varlık"].str.contains("THYAO")]
    assert bool(thyao_row["Yeterli işlem"].iloc[0]) is True

    bist_frame = comparison_frame(runs_df, groups=["bist"])
    assert len(bist_frame) == 2
    assert (bist_frame["Grup"] == "bist").all()


def test_beat_count_and_sharpe_pivot():
    """beat_count ve sharpe_diff_pivot fonksiyonları doğru özetleri üretmelidir."""
    runs_data = [
        {
            "ticker": "THYAO.IS",
            "grp": "bist",
            "strategy": "ma_crossover",
            "total_return": 0.20,
            "bench_total_return": 0.10,
            "sharpe": 1.2,
            "bench_sharpe": 0.8,
            "max_drawdown": -0.15,
            "trades": 35,
            "error": None,
        },
        {
            "ticker": "THYAO.IS",
            "grp": "bist",
            "strategy": "macd",
            "total_return": 0.05,
            "bench_total_return": 0.15,
            "sharpe": 0.5,
            "bench_sharpe": 1.0,
            "max_drawdown": -0.20,
            "trades": 30,
            "error": None,
        },
        {
            "ticker": "AAPL",
            "grp": "nasdaq",
            "strategy": "ma_crossover",
            "total_return": 0.30,
            "bench_total_return": 0.20,
            "sharpe": 1.1,
            "bench_sharpe": 1.1,
            "max_drawdown": -0.10,
            "trades": 40,
            "error": None,
        },
        {
            "ticker": "AAPL",
            "grp": "nasdaq",
            "strategy": "macd",
            "total_return": 0.10,
            "bench_total_return": 0.10,
            "sharpe": 0.7,
            "bench_sharpe": 0.9,
            "max_drawdown": -0.12,
            "trades": 31,
            "error": None,
        },
        {
            "ticker": "BAD.IS",
            "grp": "bist",
            "strategy": "ma_crossover",
            "total_return": None,
            "bench_total_return": None,
            "sharpe": None,
            "bench_sharpe": None,
            "max_drawdown": None,
            "trades": None,
            "error": "Hata",
        },
    ]
    runs_df = pd.DataFrame(runs_data)
    frame = comparison_frame(runs_df)

    # 4 hatasız satırdan sadece THYAO.IS + ma_crossover'da Sharpe (1.2) > Al-tut Sharpe (0.8)
    beaten, total = beat_count(frame)
    assert beaten == 1
    assert total == 4

    pivot = sharpe_diff_pivot(frame)
    assert isinstance(pivot, pd.DataFrame)
    assert pivot.shape == (2, 2)


def test_ui_comparison_page_apptest(tmp_path):
    """Streamlit uygulamasının karşılaştırma sayfası hatasız açılır ve tabloyu gösterir."""
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    from stratlab.results.db import save_run

    db_path = str(tmp_path / "results.sqlite")
    save_run(
        db_path,
        {
            "ticker": "THYAO.IS",
            "grp": "bist",
            "strategy": "ma_crossover",
            "total_return": 0.20,
            "bench_total_return": 0.10,
            "sharpe": 1.2,
            "bench_sharpe": 0.8,
            "max_drawdown": -0.15,
            "trades": 35,
            "error": None,
        },
    )

    page_path = Path(__file__).parent.parent / "src" / "stratlab" / "ui" / "pages" / "1_Karsilastirma.py"
    at = AppTest.from_file(str(page_path), default_timeout=30)
    at.run()
    # Veritabanı yolunu test veritabanına ayarla
    at.sidebar.text_input[0].set_value(db_path).run()

    assert not at.exception
    assert len(at.error) == 0


def _summary_texts(at):
    """Sayfadaki başlık ve uyarı metinlerini tek listede toplar."""
    return [e.value for e in at.subheader] + [e.value for e in at.warning]


def test_ui_comparison_page_shows_tables_and_beat_line(tmp_path):
    """Veritabanı varken özet satırı, karşılaştırma tablosu ve Sharpe farkı tablosu görünür."""
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    from stratlab.results.db import save_run

    db_path = str(tmp_path / "results.sqlite")
    for ticker, strategy, sh, b_sh in [("THYAO.IS", "macd", 1.2, 0.8), ("AAPL", "macd", 0.5, 0.9)]:
        save_run(db_path, {"ticker": ticker, "grp": "bist" if ticker.endswith(".IS") else "nasdaq",
                           "strategy": strategy, "period": "gelistirme", "total_return": 0.2,
                           "bench_total_return": 0.1, "sharpe": sh, "bench_sharpe": b_sh,
                           "max_drawdown": -0.1, "trades": 40})

    page_path = Path(__file__).parent.parent / "src" / "stratlab" / "ui" / "pages" / "1_Karsilastirma.py"
    at = AppTest.from_file(str(page_path), default_timeout=30)
    at.run()
    at.sidebar.text_input[0].set_value(db_path).run()

    assert not at.exception
    assert "Al-tut'u Sharpe'ta geçen: 1 / 2" in _summary_texts(at)
    assert len(at.dataframe) == 2
    assert len(at.dataframe[0].value) == 2


def test_ui_comparison_page_warns_without_database(tmp_path):
    """Veritabanı yoksa hata değil, toplu çalıştırma uyarısı gösterilir ve dosya oluşturulmaz."""
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    db_path = tmp_path / "yok.sqlite"
    page_path = Path(__file__).parent.parent / "src" / "stratlab" / "ui" / "pages" / "1_Karsilastirma.py"
    at = AppTest.from_file(str(page_path), default_timeout=30)
    at.run()
    at.sidebar.text_input[0].set_value(str(db_path)).run()

    assert not at.exception
    assert len(at.error) == 0
    assert any("Önce toplu çalıştırma yapın" in w.value for w in at.warning)
    assert not db_path.exists()


def test_comparison_frame_keeps_latest_run_for_duplicates():
    """Aynı varlık ve strateji iki kez kaydedildiyse en son kayıt kullanılır ve pivot hata vermez."""
    base = {"grp": "bist", "ticker": "THYAO.IS", "strategy": "macd", "period": "gelistirme",
            "total_return": 0.1, "bench_total_return": 0.1, "bench_sharpe": 0.5,
            "max_drawdown": -0.1, "trades": 40, "error": None}
    runs = pd.DataFrame([{**base, "id": 1, "sharpe": 0.2}, {**base, "id": 2, "sharpe": 0.9}])
    frame = comparison_frame(runs)
    assert len(frame) == 1
    assert frame["Sharpe"].iloc[0] == 0.9
    assert sharpe_diff_pivot(frame).shape == (1, 1)
