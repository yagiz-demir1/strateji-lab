"""Bollinger Bantları göstergesi (G-011)."""

import pandas as pd
from stratlab.indicators.moving_averages import sma

def bollinger(close: pd.Series, window: int = 20, k: float = 2.0) -> pd.DataFrame:
    """Bollinger Bantlarını hesaplar.
    
    mid = SMA
    upper/lower = mid +/- k * standart sapma (popülasyon, ddof=0)
    """
    if window < 1:
        raise ValueError("window değeri 1'den küçük olamaz.")
        
    mid = sma(close, window=window)
    std = close.rolling(window=window).std(ddof=0)
    
    upper = mid + k * std
    lower = mid - k * std
    
    return pd.DataFrame({
        "mid": mid,
        "upper": upper,
        "lower": lower
    }, index=close.index)
