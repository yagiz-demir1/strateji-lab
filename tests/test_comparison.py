"""Strateji ve al-tut karşılaştırma tablosu için testler (G-025)."""

import pandas as pd
import pytest
from stratlab.reports.comparison import comparison_table
from stratlab.ui.logic import run_selected


def test_comparison_table_structure_and_values():
    """comparison_table doğru sütunları, satırları ve fark hesaplamasını üretmelidir."""
    strategy_equity = pd.Series([1.0, 1.1, 1.21])
    benchmark_equity = pd.Series([1.0, 1.05, 1.1025])
    
    table = comparison_table(strategy_equity, benchmark_equity)
    
    assert isinstance(table, pd.DataFrame)
    assert list(table.columns) == ["Strateji", "Al-tut", "Fark"]
    expected_index = ["Toplam Getiri", "Yıllık Getiri", "Yıllık Volatilite", "Sharpe Oranı", "En Büyük Düşüş"]
    assert list(table.index) == expected_index
    
    # Toplam Getiri kontrolü: Strateji = 0.21, Al-tut = 0.1025, Fark = 0.1075
    assert pytest.approx(table.loc["Toplam Getiri", "Strateji"], abs=1e-9) == 0.21
    assert pytest.approx(table.loc["Toplam Getiri", "Al-tut"], abs=1e-9) == 0.1025
    assert pytest.approx(table.loc["Toplam Getiri", "Fark"], abs=1e-9) == 0.1075


def test_run_selected_includes_comparison(tmp_path):
    """run_selected sonucu 'comparison' anahtarını (5 satır x 3 sütun DataFrame) içermelidir."""
    def mock_source(ticker, start, end):
        dates = pd.date_range(start, periods=5)
        return pd.DataFrame({
            "open": [10, 11, 12, 13, 14],
            "high": [11, 12, 13, 14, 15],
            "low": [9, 10, 11, 12, 13],
            "close": [10.0, 11.0, 12.0, 13.0, 14.0],
            "volume": [1000, 1000, 1000, 1000, 1000]
        }, index=dates)

    result = run_selected(
        ticker="TEST",
        strategy="ma_crossover",
        start="2024-01-01",
        end="2024-01-05",
        cost_bps=0.0,
        source=mock_source,
        cache_dir=str(tmp_path),
    )
    
    assert "comparison" in result
    comp_df = result["comparison"]
    assert isinstance(comp_df, pd.DataFrame)
    assert comp_df.shape == (5, 3)
