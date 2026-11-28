"""Basit ve üstel hareketli ortalama (SMA, EMA) göstergelerini test eder."""

import numpy as np
import pandas as pd
import pytest
from stratlab.indicators.moving_averages import ema, sma


def test_sma_returns_series_with_same_length():
    """SMA fonksiyonu girdiyle aynı uzunlukta bir pandas Series döndürmelidir."""
    data = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    result = sma(data, window=3)
    assert isinstance(result, pd.Series)
    assert len(result) == len(data)


def test_sma_calculation_values():
    """SMA hesaplaması: [1..10] serisinde window=3 için ilk 2 değer NaN, son değer 9.0 olmalı."""
    data = pd.Series(range(1, 11), dtype=float)
    result = sma(data, window=3)
    assert np.isnan(result.iloc[0])
    assert np.isnan(result.iloc[1])
    assert not np.isnan(result.iloc[2])
    assert pytest.approx(result.iloc[-1]) == 9.0


def test_sma_example_values():
    """Örnek girdi [1, 2, 3, 4] ve window=2 için [NaN, 1.5, 2.5, 3.5] üretilmeli."""
    data = pd.Series([1.0, 2.0, 3.0, 4.0])
    result = sma(data, window=2)
    assert np.isnan(result.iloc[0])
    expected = [np.nan, 1.5, 2.5, 3.5]
    pd.testing.assert_series_equal(result, pd.Series(expected), check_names=False)


@pytest.mark.parametrize("window", [0, -1, -5])
def test_sma_invalid_window_raises_value_error(window):
    """window < 1 durumunda SMA ValueError fırlatmalıdır."""
    data = pd.Series([1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        sma(data, window=window)


def test_ema_returns_series_with_same_length():
    """EMA fonksiyonu girdiyle aynı uzunlukta bir pandas Series döndürmelidir."""
    data = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    result = ema(data, window=3)
    assert isinstance(result, pd.Series)
    assert len(result) == len(data)


def test_ema_calculation_values():
    """EMA hesaplaması: [1, 2, 3] ve window=2 için yaklaşık [1.0, 1.6667, 2.5556] olmalıdır."""
    data = pd.Series([1.0, 2.0, 3.0])
    result = ema(data, window=2)
    expected = [1.0, 1.6667, 2.5556]
    for r_val, e_val in zip(result, expected):
        assert pytest.approx(r_val, abs=1e-4) == e_val


@pytest.mark.parametrize("window", [0, -1, -5])
def test_ema_invalid_window_raises_value_error(window):
    """window < 1 durumunda EMA ValueError fırlatmalıdır."""
    data = pd.Series([1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        ema(data, window=window)
