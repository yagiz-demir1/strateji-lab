"""Tek varlık backtest motoru hesaplama fonksiyonları."""

import pandas as pd


def run_backtest(close: pd.Series, positions: pd.Series) -> pd.DataFrame:
    """Tek varlık için maliyetsiz günlük backtest hesaplar.

    Bugünkü pozisyon bir gün kaydırılarak yarının getirisine uygulanır (gecikme / look-ahead bias koruması).
    Sermaye eğrisi 1.0'dan başlar.
    """
    if len(close) != len(positions):
        raise ValueError("close ve positions serilerinin uzunlukları aynı olmalıdır.")
    
    # Getirileri hesapla: (P_t / P_{t-1}) - 1
    price_returns = close.pct_change().fillna(0.0)
    
    # Pozisyonu 1 gün kaydır (bugünkü pozisyon yarının getirisine etki eder)
    shifted_positions = positions.shift(1).fillna(0.0)
    
    # Strateji getirileri
    strategy_returns = price_returns * shifted_positions
    
    # Sermaye eğrisi (Equity curve): 1.0'dan başlar ve bileşik olarak büyür
    equity = (1.0 + strategy_returns).cumprod()
    
    # İlk gün equity 1.0 olmalı
    if not equity.empty:
        equity.iloc[0] = 1.0
        
    result = pd.DataFrame({
        "returns": strategy_returns,
        "equity": equity
    }, index=close.index)
    
    return result
