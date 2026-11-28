"""MACD stratejisi için testler (G-016).

MACD çizgisinin sinyal çizgisini yukarı kestiğinde ve üstünde kaldığında
alımda kalma (1), aksi durumlarda nakitte kalma (0) kurallarını kontrol eder.
"""

import numpy as np
import pandas as pd
import pytest

from stratlab.indicators.macd import macd
from stratlab.strategies.macd_strategy import cross_positions, macd_positions


def test_cross_positions_hand_calculated_example():
    """Görevdeki elle hesaplanmış örnek doğrulanmalıdır:
    a = [1, 2, 3, 2], b = [2, 2, 1, 3] -> [0, 0, 1, 0].
    """
    a = pd.Series([1, 2, 3, 2])
    b = pd.Series([2, 2, 1, 3])
    expected = [0, 0, 1, 0]

    result = cross_positions(a, b)

    assert isinstance(result, pd.Series)
    assert list(result) == expected


def test_cross_positions_handles_nan_values():
    """Serilerden en az biri NaN olduğunda sonuç 0 olmalıdır."""
    a = pd.Series([np.nan, 5.0, 2.0, np.nan, 4.0])
    b = pd.Series([3.0, np.nan, 1.0, np.nan, 2.0])
    expected = [0, 0, 1, 0, 1]

    result = cross_positions(a, b)

    assert list(result) == expected


def test_cross_positions_returns_series_with_zero_or_one():
    """cross_positions sadece 0 ve 1 değerlerini içeren bir Series döndürmelidir."""
    a = pd.Series([10.0, 20.0, 30.0])
    b = pd.Series([20.0, 20.0, 10.0])
    result = cross_positions(a, b)

    assert isinstance(result, pd.Series)
    assert len(result) == len(a)
    assert set(result.unique()).issubset({0, 1})


def test_macd_positions_equals_cross_positions():
    """macd_positions(close) çıktısı cross_positions(macd, signal) ile tam olarak aynı olmalıdır."""
    # 40 günlük fiyat serisi
    close = pd.Series(
        [10.0 + i * 0.5 if i < 20 else 20.0 - (i - 20) * 0.4 for i in range(40)]
    )
    fast, slow, signal = 12, 26, 9

    macd_df = macd(close, fast=fast, slow=slow, signal=signal)
    expected = cross_positions(macd_df["macd"], macd_df["signal"])
    actual = macd_positions(close, fast=fast, slow=slow, signal=signal)

    pd.testing.assert_series_equal(actual, expected)


def test_macd_positions_constant_prices_all_zeros():
    """Fiyatın hiç değişmediği seride MACD ve sinyal 0 olacağından (a > b sağlanmaz) pozisyonlar hep 0 olmalıdır."""
    close = pd.Series([100.0] * 40)
    positions = macd_positions(close, fast=12, slow=26, signal=9)

    assert (positions == 0).all()
