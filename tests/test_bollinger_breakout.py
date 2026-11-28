"""Bollinger kırılım stratejisi (G-015) için testler.

Fiyat üst bandı aşınca alım (1), orta bandın altına inince satış (0) mantığını kontrol eder.
"""

import pandas as pd
import pytest
import numpy as np
from stratlab.strategies.bollinger_breakout import bollinger_breakout_positions


def test_bollinger_breakout_returns_series_with_zero_or_one():
    """bollinger_breakout_positions sadece 0 veya 1 içeren bir Series döndürmelidir."""
    close = pd.Series([100.0] * 30)
    positions = bollinger_breakout_positions(close, window=20, k=2)
    
    assert isinstance(positions, pd.Series)
    assert len(positions) == len(close)
    assert set(positions.unique()).issubset({0, 1})


def test_bollinger_breakout_initial_days_are_zero():
    """Bantların hesaplanamadığı ilk günler (window-1) pozisyon 0 olmalıdır."""
    close = pd.Series([100.0] * 30)
    positions = bollinger_breakout_positions(close, window=20, k=2)
    assert (positions.iloc[:19] == 0).all()


def test_bollinger_breakout_logic_manual_series():
    """Elle kurulmuş seri ile strateji mantığı doğrulanmalıdır.

    Senaryo:
    - 20 gün 100.0 (Bantlar hesaplanır: mid=100, upper=100)
    - 21. gün 110.0 (Sert yükseliş -> upper band aşılır -> pozisyon 1)
    - 22. gün 105.0 (Düşüş ama hala orta bandın üzerinde -> pozisyon 1 korunur)
    - 23. gün 95.0 (Sert düşüş -> orta bandın altına inilir -> pozisyon 0)
    """
    prices = [100.0] * 20
    prices.append(110.0)
    prices.append(105.0)
    prices.append(95.0)
    
    close = pd.Series(prices)
    positions = bollinger_breakout_positions(close, window=20, k=2)
    
    assert positions.iloc[19] == 0
    assert positions.iloc[20] == 1
    assert positions.iloc[21] == 1
    assert positions.iloc[22] == 0


def test_bollinger_breakout_example_from_task():
    """Görevdeki örnek girdi doğrulanmalıdır: 25 gün 100, sonra 110 -> 1."""
    prices = [100.0] * 25 + [110.0]
    close = pd.Series(prices)
    positions = bollinger_breakout_positions(close, window=20, k=2)
    assert positions.iloc[-1] == 1
