"""RSI (Göreceli Güç Endeksi) gösterge hesaplama fonksiyonu."""

import numpy as np
import pandas as pd


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Wilder yöntemiyle Göreceli Güç Endeksi (RSI) hesaplar."""
    if window < 2:
        raise ValueError("window değeri 2'den küçük olamaz.")
    
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    
    # Wilder düzeltmesi (EWM alpha = 1 / window, adjust=False)
    avg_gain = gain.ewm(alpha=1.0 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / window, min_periods=window, adjust=False).mean()
    
    # İlk window dönemi için değerleri NaN yap
    # ewm min_periods=window zaten NaN bırakır ancak ilk indexleri temizleyelim
    rs = avg_gain / avg_loss
    result = 100.0 - (100.0 / (1.0 + rs))
    
    # Kayıpların 0 olduğu durumlar (sürekli yükseliş)
    result[avg_loss == 0] = 100.0
    # Kazançların 0 olduğu durumlar (sürekli düşüş)
    result[avg_gain == 0] = 0.0
    # Her ikisi de 0 olan veya değişmeyen durumlar / ilk window
    # ewm sonuçlarında ilk geçerli değer index window-1 civarındadır
    result.iloc[:window] = np.nan
    
    # Eğer tüm seride hiç değişim yoksa (std == 0) veya avg_gain ve avg_loss toplamı 0 ise NaN
    no_change = (avg_gain == 0) & (avg_loss == 0)
    result[no_change] = np.nan
    
    return result
