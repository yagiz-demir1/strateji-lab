"""RSI (Göreceli Güç Endeksi) göstergesini test eder."""

import numpy as np
import pandas as pd
import pytest
from stratlab.indicators.rsi import rsi


def test_rsi_returns_series_with_same_length():
    """RSI fonksiyonu girdiyle aynı uzunlukta pandas Series döndürmelidir."""
    data = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0])
    result = rsi(data, window=14)
    assert isinstance(result, pd.Series)
    assert len(result) == len(data)


def test_rsi_initial_values_are_nan():
    """İlk window kadar değer NaN olmalıdır."""
    data = pd.Series(range(1, 31), dtype=float)
    result = rsi(data, window=14)
    assert result.iloc[:14].isna().all()
    assert not result.iloc[14:].isna().any()


def test_rsi_bounds():
    """Tanımlı bütün RSI değerleri 0 ile 100 arasında olmalıdır."""
    data = pd.Series([10, 12, 11, 15, 14, 18, 17, 20, 19, 22, 21, 25, 24, 28, 27, 30], dtype=float)
    result = rsi(data, window=14).dropna()
    assert (result >= 0.0).all()
    assert (result <= 100.0).all()


def test_rsi_strictly_increasing_series():
    """Her gün yükselen bir seride RSI son değeri 100 olmalıdır."""
    data = pd.Series(range(1, 31), dtype=float)
    result = rsi(data, window=14)
    assert pytest.approx(result.iloc[-1]) == 100.0


def test_rsi_strictly_decreasing_series():
    """Her gün düşen bir seride RSI son değeri 0 olmalıdır."""
    data = pd.Series(range(30, 0, -1), dtype=float)
    result = rsi(data, window=14)
    assert pytest.approx(result.iloc[-1]) == 0.0


def test_rsi_constant_series_has_nan():
    """Hiç değişmeyen bir seride RSI değerleri NaN olmalıdır."""
    data = pd.Series([50.0] * 20)
    result = rsi(data, window=14)
    assert result.isna().all()


@pytest.mark.parametrize("window", [0, 1, -1])
def test_rsi_invalid_window_raises_value_error(window):
    """window < 2 durumunda ValueError fırlatılmalıdır."""
    data = pd.Series(range(1, 20), dtype=float)
    with pytest.raises(ValueError):
        rsi(data, window=window)
