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


def test_rsi_wilder_classic_example():
    """Wilder'ın klasik RSI örneği ile hesaplama doğrulanır (G-022)."""
    # 33 kapanış fiyatı
    prices = [
        44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08,
        45.89, 46.03, 45.61, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64,
        46.21, 46.25, 45.71, 46.45, 45.78, 45.35, 44.03, 44.18, 44.22, 44.57,
        43.42, 42.66, 43.13
    ]
    series = pd.Series(prices)
    window = 14
    result = rsi(series, window=window)

    # İlk 14 değer (0-13) NaN olmalı
    assert result.iloc[:14].isna().all()

    # Beklenen RSI değerleri (indeks 14'ten itibaren)
    expected = [
        70.46, 66.25, 66.48, 69.35, 66.29, 57.92, 62.88, 63.21, 56.01, 62.34,
        54.67, 50.39, 40.02, 41.49, 41.90, 45.50, 37.32, 33.09, 37.79
    ]

    # İlk değerin (indeks 14) elle hesabı:
    # 1. İlk 14 değişim (t=1..14):
    #    Gain: [0, 0.06, 0, 0.72, 0.50, 0.27, 0.32, 0.42, 0.24, 0, 0.14, 0, 0.67, 0] -> Ort: 0.238571
    #    Loss: [0.25, 0, 0.54, 0, 0, 0, 0, 0, 0, 0.19, 0, 0.42, 0, 0] -> Ort: 0.100000
    # 2. RS = 0.238571 / 0.10 = 2.38571
    # 3. RSI = 100 - 100 / (1 + 2.38571) = 70.46

    actual = result.iloc[14:].values
    assert len(actual) == len(expected)
    # Wilder yöntemi hassas olduğu için ±0.01 tolerans ile kontrol edilir
    np.testing.assert_allclose(actual, expected, atol=0.01)
