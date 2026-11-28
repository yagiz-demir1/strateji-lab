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


def test_annual_volatility_hand_calculated():
    """[1.0, 1.1, 0.99] serisinde volatilite elle hesaplanan değere eşit olmalıdır."""
    # Günlük getiriler: +0.10, -0.10
    # Standart sapma (ddof=1): sqrt((0.1² + 0.1²) / 1) = 0.141421
    # Yıllık: 0.141421 × √252 (15.874508) = 2.244994
    equity = pd.Series([1.0, 1.1, 0.99])
    assert pytest.approx(annual_volatility(equity), abs=1e-4) == 2.2450


def test_sharpe_hand_calculated():
    """[1.0, 1.1, 1.21, 1.089] serisinde Sharpe elle hesaplanan değere eşit olmalıdır."""
    # Günlük getiriler: +0.10, +0.10, -0.10 → ortalama 0.033333
    # Standart sapma (ddof=1): sqrt((0.066667² + 0.066667² + 0.133333²) / 2) = 0.115470
    # Sharpe: 0.033333 / 0.115470 × √252 = 0.288675 × 15.874508 = 4.582576
    equity = pd.Series([1.0, 1.1, 1.21, 1.089])
    assert pytest.approx(sharpe(equity), abs=1e-4) == 4.5826
