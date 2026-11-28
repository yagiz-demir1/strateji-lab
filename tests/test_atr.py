"""ATR (Ortalama Gercek Aralik) gostergesi icin testler (G-011)."""
import numpy as np
import pandas as pd
import pytest
from stratlab.indicators.atr import atr

def test_atr_returns_series_with_correct_length():
    """atr fonksiyonu girdiyle ayni uzunlukta bir pandas Series dondurmelidir."""
    high = pd.Series([10.0] * 20)
    low = pd.Series([8.0] * 20)
    close = pd.Series([9.0] * 20)
    result = atr(high, low, close, window=14)
    
    assert isinstance(result, pd.Series)
    assert len(result) == 20

def test_atr_hand_calculated_example():
    """G-011 gorevindeki elle hesaplanmis ornek dogrulanmalidir."""
    # high = [10, 12, 11], low = [8, 9, 9], close = [9, 11, 10], window = 2
    # TR0: high-low = 2
    # TR1: max(12-9, |12-9|, |9-9|) = 3
    # TR2: max(11-9, |11-11|, |9-11|) = 2
    # ATR1 (ilk window ortalamasi) = (2+3)/2 = 2.5
    # ATR2 (Wilder) = (2.5 * 1 + 2) / 2 = 2.25
    high = pd.Series([10.0, 12.0, 11.0])
    low = pd.Series([8.0, 9.0, 9.0])
    close = pd.Series([9.0, 11.0, 10.0])
    
    result = atr(high, low, close, window=2)
    
    assert np.isnan(result.iloc[0])
    assert pytest.approx(result.iloc[1]) == 2.5
    assert pytest.approx(result.iloc[2]) == 2.25

def test_atr_zero_for_constant_prices():
    """Fiyatlarin hic degismedigi bir seride ATR 0 olmalidir."""
    high = pd.Series([100.0] * 20)
    low = pd.Series([100.0] * 20)
    close = pd.Series([100.0] * 20)
    
    result = atr(high, low, close, window=14)
    # Ilk window-1 degerden sonrakiler 0 olmalidir
    assert (result.iloc[13:] == 0.0).all()
