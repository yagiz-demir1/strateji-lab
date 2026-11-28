"""Hareketli ortalama kesişimi stratejisi hesaplama fonksiyonları."""

import pandas as pd
from stratlab.indicators.moving_averages import sma


def ma_crossover_positions(close: pd.Series, fast: int, slow: int) -> pd.Series:
    """Kısa ve uzun vadeli basit hareketli ortalama kesişimine göre pozisyon serisi (0 veya 1) üretir.

    Kısa ortalama (fast) uzun ortalamanın (slow) kesinlikle üstündeyse pozisyon 1, aksi hâllerde
    (altında, eşit veya ortalamaların henüz hesaplanamadığı ilk günlerde) 0 olur.
    """
    if fast >= slow:
        raise ValueError("fast periyodu slow periyodundan küçük olmalıdır.")
    if fast < 1 or slow < 1:
        raise ValueError("Periyotlar en az 1 olmalıdır.")

    fast_ma = sma(close, window=fast)
    slow_ma = sma(close, window=slow)

    positions = (fast_ma > slow_ma).astype(int)
    return positions
