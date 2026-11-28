"""ATR (Ortalama Gerçek Aralık) göstergesi (G-011)."""

import pandas as pd

def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Wilder yöntemiyle Ortalama Gerçek Aralığı (ATR) hesaplar.
    
    Gerçek Aralık (TR) = max(high - low, |high - prev_close|, |low - prev_close|)
    İlk ATR, ilk 'window' TR değerinin ortalamasıdır.
    Sonraki ATR = (önceki_atr * (window - 1) + mevcut_tr) / window
    """
    if window < 1:
        raise ValueError("window değeri 1'den küçük olamaz.")
        
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR serisini başlat
    atr_values = [float('nan')] * len(tr)
    
    if len(tr) < window:
        return pd.Series(atr_values, index=tr.index)
    
    # İlk ATR: ilk window TR'nin ortalaması
    current_atr = tr.iloc[:window].mean()
    atr_values[window-1] = current_atr
    
    # Wilder düzeltmesi
    for i in range(window, len(tr)):
        current_atr = (current_atr * (window - 1) + tr.iloc[i]) / window
        atr_values[i] = current_atr
        
    return pd.Series(atr_values, index=tr.index)
