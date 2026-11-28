"""Temel performans metrikleri (G-006) için birim testler.

Sermaye eğrisi (equity curve) üzerinden toplam getiri, yıllık getiri,
volatilite, Sharpe oranı ve en büyük düşüşü (drawdown) doğrular.
"""

import numpy as np
import pandas as pd
import pytest
from stratlab.metrics import (
    total_return,
    annual_return,
    annual_volatility,
    sharpe,
    max_drawdown,
)


def test_total_return_calculation():
    """Toplam getiri [1.0, 1.1, 1.21] serisi için 0.21 olmalıdır."""
    equity = pd.Series([1.0, 1.1, 1.21])
    # Bitme şartı: total_return([1.0, 1.1, 1.21]) = 0.21
    assert pytest.approx(total_return(equity), abs=1e-4) == 0.21


def test_total_return_empty_or_single_value():
    """Boş veya tek değerli serilerde toplam getiri 0.0 olmalıdır."""
    assert total_return(pd.Series([1.0])) == 0.0
    assert total_return(pd.Series([], dtype=float)) == 0.0


def test_max_drawdown_calculation():
    """En büyük düşüş [1.0, 1.2, 0.9, 1.1] serisi için -0.25 olmalıdır."""
    equity = pd.Series([1.0, 1.2, 0.9, 1.1])
    # Tavan 1.2, taban 0.9. Düşüş: (0.9 / 1.2) - 1 = -0.25
    # Bitme şartı: max_drawdown([1.0, 1.2, 0.9, 1.1]) = -0.25
    assert pytest.approx(max_drawdown(equity), abs=1e-4) == -0.25


def test_max_drawdown_monotonic_increasing():
    """Sürekli artan eğrilerde en büyük düşüş 0.0 olmalıdır."""
    equity = pd.Series([1.0, 1.1, 1.2, 1.3])
    assert pytest.approx(max_drawdown(equity), abs=1e-4) == 0.0


def test_annual_return_calculation():
    """Yıllık getiri 252 iş günü üzerinden doğru hesaplanmalıdır."""
    # 253 satır = 252 getiri günü. 1.0'dan 2.0'a çıkış %100 getiri.
    dates = pd.date_range("2025-01-01", periods=253, freq="B")
    equity = pd.Series(np.linspace(1.0, 2.0, 253), index=dates)
    res = annual_return(equity)
    assert pytest.approx(res, abs=1e-4) == 1.0


def test_annual_volatility_zero_for_constant_returns():
    """Getirileri hep 0 olan seride volatilite 0 olmalıdır."""
    # Bitme şartı: Getirileri hep 0 olan bir seride volatilite 0.
    equity = pd.Series([1.0, 1.0, 1.0, 1.0])
    assert pytest.approx(annual_volatility(equity), abs=1e-4) == 0.0


def test_sharpe_nan_for_zero_volatility():
    """Volatilitenin 0 olduğu durumda Sharpe oranı NaN olmalıdır."""
    # Bitme şartı: Getirileri hep 0 olan bir seride Sharpe NaN.
    equity = pd.Series([1.0, 1.0, 1.0, 1.0])
    assert np.isnan(sharpe(equity))


def test_sharpe_calculation_with_random_data():
    """Sharpe oranı geçerli veriler için sayısal bir değer döndürmelidir."""
    np.random.seed(42)
    daily_returns = np.random.normal(0.0005, 0.01, 252)
    equity = pd.Series(np.cumprod(1 + np.insert(daily_returns, 0, 0)))
    s_ratio = sharpe(equity)
    assert isinstance(s_ratio, float)
    assert not np.isnan(s_ratio)
