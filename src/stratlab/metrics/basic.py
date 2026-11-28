"""Temel performans metrikleri (G-006)."""

import numpy as np
import pandas as pd


def total_return(equity: pd.Series) -> float:
    """Toplam getiriyi hesaplar."""
    if len(equity) < 2:
        return 0.0
    return float((equity.iloc[-1] / equity.iloc[0]) - 1.0)


def annual_return(equity: pd.Series) -> float:
    """Yıllıklandırılmış getiriyi (CAGR) 252 iş günü üzerinden hesaplar."""
    if len(equity) < 2:
        return 0.0
    total_days = len(equity) - 1
    if total_days == 0:
        return 0.0
    return float((equity.iloc[-1] / equity.iloc[0]) ** (252 / total_days) - 1.0)


def annual_volatility(equity: pd.Series) -> float:
    """Yıllıklandırılmış volatiliteyi (standart sapma) hesaplar."""
    if len(equity) < 2:
        return 0.0
    returns = equity.pct_change().dropna()
    if returns.empty:
        return 0.0
    return float(returns.std() * np.sqrt(252))


def sharpe(equity: pd.Series, risk_free: float = 0.0) -> float:
    """Sharpe oranını hesaplar (risksiz faiz varsayılan 0)."""
    vol = annual_volatility(equity)
    if vol == 0 or np.isnan(vol):
        return np.nan
    ann_ret = annual_return(equity)
    return float((ann_ret - risk_free) / vol)


def max_drawdown(equity: pd.Series) -> float:
    """Sermaye eğrisi üzerindeki en büyük düşüşü (Maximum Drawdown) hesaplar."""
    if len(equity) < 1:
        return 0.0
    rolling_max = equity.cummax()
    drawdown = (equity / rolling_max) - 1.0
    return float(drawdown.min())
