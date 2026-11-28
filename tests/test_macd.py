"""MACD (Moving Average Convergence Divergence) gostergesi icin testler (G-012)."""

import pandas as pd
import pytest
import numpy as np
from stratlab.indicators.macd import macd

def test_macd_returns_dataframe_with_correct_columns():
    """macd fonksiyonu macd, signal, hist sutunlari olan bir DataFrame dondurmelidir."""
    close = pd.Series([10.0] * 50)
    result = macd(close, fast=12, slow=26, signal=9)
    
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["macd", "signal", "hist"]
    assert len(result) == len(close)

def test_macd_constant_series_is_zero():
    """Sabit bir fiyat serisinde macd, signal ve hist degerleri 0 olmalidir."""
    close = pd.Series([100.0] * 50)
    result = macd(close, fast=12, slow=26, signal=9)
    
    # EMA(100) - EMA(100) = 0. EMA(0) = 0.
    assert (result["macd"] == 0.0).all()
    assert (result["signal"] == 0.0).all()
    assert (result["hist"] == 0.0).all()

def test_macd_invalid_periods_raises_value_error():
    """fast >= slow veya periyotlar < 1 durumunda ValueError firlatilmalidir."""
    close = pd.Series([10.0] * 30)
    
    with pytest.raises(ValueError):
        macd(close, fast=26, slow=12)
        
    with pytest.raises(ValueError):
        macd(close, fast=12, slow=12)

    with pytest.raises(ValueError):
        macd(close, fast=0, slow=26)

def test_macd_logic_validation():
    """MACD bilesenlerinin matematiksel iliskisi (macd - signal = hist) dogrulanmalidir."""
    # Rastgele bir veri seti
    close = pd.Series([10, 11, 13, 12, 14, 15, 17, 16, 18, 20])
    result = macd(close, fast=2, slow=5, signal=3)
    
    # hist = macd - signal kontrolu
    calculated_hist = result["macd"] - result["signal"]
    pd.testing.assert_series_equal(result["hist"], calculated_hist, check_names=False)


def test_macd_matches_ema_formula():
    """macd = ema(fast) - ema(slow), signal = ema(macd, signal), hist = macd - signal (G-002'deki ema ile)."""
    from stratlab.indicators.moving_averages import ema

    close = pd.Series([10.0, 11.0, 13.0, 12.0, 14.0, 15.0, 17.0, 16.0, 18.0, 20.0])
    result = macd(close, fast=2, slow=5, signal=3)

    expected_macd = ema(close, window=2) - ema(close, window=5)
    expected_signal = ema(expected_macd, window=3)
    pd.testing.assert_series_equal(result["macd"], expected_macd, check_names=False)
    pd.testing.assert_series_equal(result["signal"], expected_signal, check_names=False)
    pd.testing.assert_series_equal(result["hist"], expected_macd - expected_signal, check_names=False)
