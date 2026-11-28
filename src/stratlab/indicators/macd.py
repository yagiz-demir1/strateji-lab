"""MACD (Moving Average Convergence Divergence) göstergesi (G-012)."""

import pandas as pd
from stratlab.indicators.moving_averages import ema


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """MACD, sinyal çizgisi ve histogram hesaplar.

    macd = EMA(close, fast) - EMA(close, slow)
    signal = EMA(macd, signal)
    hist = macd - signal
    """
    if fast < 1 or slow < 1 or signal < 1:
        raise ValueError("Periyotlar 1'den küçük olamaz.")
    if fast >= slow:
        raise ValueError("fast periyodu slow periyodundan küçük olmalıdır.")

    macd_line = ema(close, window=fast) - ema(close, window=slow)
    signal_line = ema(macd_line, window=signal)
    histogram = macd_line - signal_line

    return pd.DataFrame({
        "macd": macd_line,
        "signal": signal_line,
        "hist": histogram
    }, index=close.index)
