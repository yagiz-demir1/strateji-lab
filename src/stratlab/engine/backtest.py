"""Tek varlık backtest motoru hesaplama fonksiyonları."""

import pandas as pd


def run_backtest(close: pd.Series, positions: pd.Series, cost_bps: float = 0.0) -> pd.DataFrame:
    """Tek varlık için komisyon ve spread maliyetli günlük backtest hesaplar.

    Bugünkü pozisyon bir gün kaydırılarak yarının getirisine uygulanır (gecikme / look-ahead bias koruması).
    Pozisyon değişimlerinde cost_bps baz puan üzerinden maliyet düşülür.
    Sermaye eğrisi 1.0'dan başlar.
    """
    if cost_bps < 0:
        raise ValueError("cost_bps değeri 0'dan küçük olamaz.")
        
    if len(close) != len(positions):
        raise ValueError("close ve positions serilerinin uzunlukları aynı olmalıdır.")
    
    # Getirileri hesapla: (P_t / P_{t-1}) - 1
    price_returns = close.pct_change().fillna(0.0)
    
    # Pozisyonu 1 gün kaydır (bugünkü pozisyon yarının getirisine etki eder)
    shifted_positions = positions.shift(1).fillna(0.0)
    
    # Strateji getirileri (fiyat değişimi kaynaklı)
    strategy_returns = price_returns * shifted_positions
    
    # Maliyet hesaplaması: Pozisyonun değiştiği günlerde maliyet yansıtılır.
    # İlk gün (t=0) pozisyon açılışı/değişimi için pozisyonun ilk değerine bakılır.
    position_changes = positions.diff().abs()
    position_changes.iloc[0] = abs(positions.iloc[0])
    
    cost_multiplier = 1.0 - (cost_bps / 10000.0)
    
    # Sermaye eğrisi (Equity curve): 1.0'dan başlar, bileşik olarak büyür ve maliyetler düşülür
    equity_values = [1.0]
    current_equity = 1.0
    
    for i in range(1, len(close)):
        # Önceki günden bugüne fiyat getirisi ve shift edilmiş pozisyon uygulanır
        ret = strategy_returns.iloc[i]
        current_equity *= (1.0 + ret)
        
        # Eğer bugünkü pozisyonda değişim varsa maliyeti uygula
        if position_changes.iloc[i] > 0:
            current_equity *= cost_multiplier
            
        equity_values.append(current_equity)
        
    equity = pd.Series(equity_values, index=close.index)
    
    result = pd.DataFrame({
        "returns": strategy_returns,
        "equity": equity
    }, index=close.index)
    
    return result
