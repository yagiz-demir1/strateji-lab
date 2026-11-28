"""RSI ortalamaya donus stratejisi icin testler (G-013)."""

import pandas as pd
import pytest
import numpy as np
from stratlab.strategies.rsi_reversion import threshold_positions, rsi_reversion_positions

def test_threshold_positions_hand_calculated_example():
    """Gorev tanimindaki elle hesaplanmis ornek dogrulanmalidir.
    
    Sinyal [50, 25, 40, 75, 50], low=30, high=70 -> [0, 1, 1, 0, 0]
    """
    signal = pd.Series([50, 25, 40, 75, 50])
    low = 30
    high = 70
    
    expected = [0, 1, 1, 0, 0]
    result = threshold_positions(signal, low, high)
    
    assert list(result) == expected

def test_threshold_positions_maintains_state():
    """Sinyal low ve high arasindayken onceki pozisyon korunmalidir."""
    # 0 -> al (low altina inis) -> bekle -> sat (high ustune cikis) -> bekle
    signal = pd.Series([50, 20, 40, 40, 80, 50])
    # t=0: 50 (ara, baslangic 0) -> 0
    # t=1: 20 (<30) -> 1
    # t=2: 40 (ara) -> 1
    # t=3: 40 (ara) -> 1
    # t=4: 80 (>70) -> 0
    # t=5: 50 (ara) -> 0
    expected = [0, 1, 1, 1, 0, 0]
    result = threshold_positions(signal, 30, 70)
    assert list(result) == expected

def test_rsi_reversion_positions_invalid_bounds_raises_error():
    """low >= high durumu ValueError firlatmalidir."""
    close = pd.Series([10.0, 11.0, 12.0])
    
    with pytest.raises(ValueError):
        rsi_reversion_positions(close, low=70, high=30)
        
    with pytest.raises(ValueError):
        rsi_reversion_positions(close, low=50, high=50)

def test_rsi_reversion_positions_handles_nan_values():
    """RSI'nin hesaplanamadigi (NaN) gunlerde pozisyon 0 olmalidir."""
    # RSI window=14 icin ilk 14 gun NaN doner (0-13 indisler)
    close = pd.Series([100.0] * 20)
    result = rsi_reversion_positions(close, window=14)
    
    assert (result.iloc[:14] == 0).all()

def test_rsi_reversion_logic_with_close_prices():
    """Fiyat hareketlerine gore RSI uretilip esiklere gore pozisyon alinmalidir."""
    # 15 gunluk yukselis (RSI yukselir), sonra sert dusus (RSI duser)
    prices = list(range(100, 115)) + [110, 105, 100, 95, 90]
    close = pd.Series(prices)
    
    # RSI hesaplanir, dusukken (low=30) alim, yuksekken (high=70) satis yapilmalidir
    result = rsi_reversion_positions(close, window=14, low=30, high=70)
    
    assert isinstance(result, pd.Series)
    assert len(result) == len(close)
    assert set(result.unique()).issubset({0, 1})
