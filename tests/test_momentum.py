"""12-1 Momentum stratejisi için testler (G-014)."""

import pandas as pd
import pytest
from stratlab.strategies.momentum import momentum_positions


def test_momentum_returns_series_with_zero_or_one():
    """momentum_positions fonksiyonu sadece 0 veya 1 değerlerini içeren bir Series döndürmelidir."""
    close = pd.Series(range(1, 301))
    positions = momentum_positions(close, lookback=252, skip=21)

    assert isinstance(positions, pd.Series)
    assert len(positions) == len(close)
    assert set(positions.unique()).issubset({0, 1})


def test_momentum_initial_days_are_zero():
    """İlk lookback gün boyunca pozisyon 0 olmalıdır."""
    lookback = 10
    skip = 2
    close = pd.Series(range(1, 21))
    positions = momentum_positions(close, lookback=lookback, skip=skip)

    assert (positions.iloc[:lookback] == 0).all()


def test_momentum_rising_series():
    """Sürekli yükselen bir seride ilk lookback günden sonra bütün pozisyonlar 1 olmalıdır."""
    lookback = 10
    skip = 2
    close = pd.Series(range(1, 31))
    positions = momentum_positions(close, lookback=lookback, skip=skip)

    assert (positions.iloc[lookback:] == 1).all()


def test_momentum_falling_series():
    """Sürekli düşen bir seride bütün pozisyonlar 0 olmalıdır."""
    lookback = 10
    skip = 2
    close = pd.Series(range(30, 0, -1))
    positions = momentum_positions(close, lookback=lookback, skip=skip)

    assert (positions == 0).all()


def test_momentum_logic_verification():
    """Belirli bir t anındaki getiri hesabı ve pozisyon kararı doğrulanmalıdır."""
    close = pd.Series([100, 105, 110, 90, 95, 120, 80])
    positions = momentum_positions(close, lookback=5, skip=2)
    assert positions.iloc[5] == 0

    close2 = pd.Series([100, 90, 80, 110, 120, 130, 140])
    positions2 = momentum_positions(close2, lookback=5, skip=2)
    assert positions2.iloc[5] == 1


def test_momentum_invalid_parameters_raise_value_error():
    """skip >= lookback veya geçersiz periyotlar durumunda ValueError fırlatılmalıdır."""
    close = pd.Series(range(1, 20))

    with pytest.raises(ValueError):
        momentum_positions(close, lookback=10, skip=10)

    with pytest.raises(ValueError):
        momentum_positions(close, lookback=10, skip=11)

    with pytest.raises(ValueError):
        momentum_positions(close, lookback=0, skip=2)


def test_momentum_example_from_task():
    """Görevdeki örnek girdi ve çıktı doğrulanmalıdır."""
    close = pd.Series(range(1, 301))
    positions = momentum_positions(close, lookback=252, skip=21)

    assert (positions.iloc[:252] == 0).all()
    assert (positions.iloc[252:] == 1).all()
