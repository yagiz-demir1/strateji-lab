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
    """Yıllıklandırılmış Sharpe oranını hesaplar (standart tanım).

    Sharpe = (günlük getirilerin ortalaması - günlük risksiz faiz) / günlük getirilerin
    standart sapması × √252. `risk_free` yıllık orandır (varsayılan 0).
    Getiriler hiç değişmiyorsa (standart sapma 0) sonuç NaN'dir.
    """
    returns = equity.pct_change().dropna()
    if len(returns) < 2:
        return np.nan
    std = returns.std()
    if std == 0 or np.isnan(std):
        return np.nan
    excess_mean = returns.mean() - risk_free / 252
    return float(excess_mean / std * np.sqrt(252))


def max_drawdown(equity: pd.Series) -> float:
    """Sermaye eğrisi üzerindeki en büyük düşüşü (Maximum Drawdown) hesaplar."""
    if len(equity) < 1:
        return 0.0
    rolling_max = equity.cummax()
    drawdown = (equity / rolling_max) - 1.0
    return float(drawdown.min())
