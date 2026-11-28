"""Bollinger kırılım stratejisi (G-015).

Fiyat üst bandı aşınca alım (1), orta bandın altına inince satış (0) mantığını uygular.
"""

import pandas as pd
from stratlab.indicators.bollinger import bollinger


def bollinger_breakout_positions(close: pd.Series, window: int = 20, k: float = 2.0) -> pd.Series:
    """Bollinger bant kırılımı stratejisine göre pozisyon serisi (0 veya 1) üretir.

    Fiyat üst bandın üstüne çıktığında (close > upper) pozisyon 1 olur.
    Fiyat orta bandın altına indiğinde (close < mid) pozisyon 0 olur.
    Arada önceki pozisyon korunur. Bantların hesaplanamadığı ilk günlerde pozisyon 0'dır.
    """
    bands = bollinger(close, window=window, k=k)
    upper = bands["upper"]
    mid = bands["mid"]

    positions = pd.Series(0, index=close.index, dtype=int)
    current_pos = 0

    for i in range(len(close)):
        c_val = close.iloc[i]
        u_val = upper.iloc[i]
        m_val = mid.iloc[i]

        if pd.isna(u_val) or pd.isna(m_val):
            current_pos = 0
        elif c_val > u_val:
            current_pos = 1
        elif c_val < m_val:
            current_pos = 0

        positions.iloc[i] = current_pos

    return positions
