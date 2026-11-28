"""RSI ortalamaya dönüş stratejisi (G-013)."""

import pandas as pd
import numpy as np
from stratlab.indicators.rsi import rsi


def threshold_positions(signal: pd.Series, low: float, high: float) -> pd.Series:
    """Sinyal değerlerine göre durum koruyarak pozisyon (0 veya 1) üretir.

    Sinyal low altına inince 1, high üstüne çıkınca 0 olur. Arada önceki durum korunur.
    Başlangıç pozisyonu 0'dır. Sinyal NaN ise pozisyon 0 olur.
    """
    positions = np.zeros(len(signal), dtype=int)
    current_pos = 0

    for i in range(len(signal)):
        val = signal.iloc[i]

        if pd.isna(val):
            current_pos = 0
        elif val < low:
            current_pos = 1
        elif val > high:
            current_pos = 0
        # Değilse current_pos değişmez (aradaki bölge)

        positions[i] = current_pos

    return pd.Series(positions, index=signal.index)


def rsi_reversion_positions(
    close: pd.Series, window: int = 14, low: float = 30.0, high: float = 70.0
) -> pd.Series:
    """RSI göstergesine dayalı ortalamaya dönüş stratejisi pozisyonlarını üretir.

    RSI düşükken (aşırı satım) alım yapılır (1), yüksekken (aşırı alım) nakte geçilir (0).
    """
    if low >= high:
        raise ValueError("low değeri high değerinden kesinlikle küçük olmalıdır.")

    rsi_series = rsi(close, window=window)
    return threshold_positions(rsi_series, low, high)
