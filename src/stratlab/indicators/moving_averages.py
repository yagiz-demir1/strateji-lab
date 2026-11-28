"""Basit ve üstel hareketli ortalama (SMA, EMA) hesaplama fonksiyonları."""

import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    """Basit hareketli ortalama (Simple Moving Average) hesaplar."""
    if window < 1:
        raise ValueError("window değeri 1'den küçük olamaz.")
    return series.rolling(window=window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    """Üstel hareketli ortalama (Exponential Moving Average) hesaplar."""
    if window < 1:
        raise ValueError("window değeri 1'den küçük olamaz.")
    return series.ewm(span=window, adjust=False).mean()
