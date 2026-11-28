"""RSI (Göreceli Güç Endeksi) gösterge hesaplama fonksiyonu (G-022)."""

import numpy as np
import pandas as pd


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Wilder yöntemiyle Göreceli Güç Endeksi (RSI) hesaplar.

    İlk ortalama kazanç ve kayıp, ilk 'window' değişimin basit ortalamasıdır.
    Sonraki değerler: (önceki * (window - 1) + mevcut) / window
    """
    if window < 2:
        raise ValueError("window değeri 2'den küçük olamaz.")

    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)

    # Wilder hesaplaması için dizileri hazırla
    avg_gain = np.full(len(series), np.nan)
    avg_loss = np.full(len(series), np.nan)

    if len(series) <= window:
        return pd.Series(avg_gain, index=series.index)

    # İlk window değişimin ortalaması (indeks 1'den window'a kadar olan window adet değişim)
    # prices[0]...prices[window] arasındaki değişimler window adettir.
    # Bu değişimlerin ortalaması Wilder'ın ilk RSI değerinin temelidir.
    curr_avg_gain = gain.iloc[1 : window + 1].mean()
    curr_avg_loss = loss.iloc[1 : window + 1].mean()

    # İlk ortalama değerleri window. indekse (fiyat serisindeki window+1. fiyatın olduğu satır) yazılır
    avg_gain[window] = curr_avg_gain
    avg_loss[window] = curr_avg_loss

    # Wilder düzeltmesi (smoothing)
    for i in range(window + 1, len(series)):
        curr_avg_gain = (curr_avg_gain * (window - 1) + gain.iloc[i]) / window
        curr_avg_loss = (curr_avg_loss * (window - 1) + loss.iloc[i]) / window
        avg_gain[i] = curr_avg_gain
        avg_loss[i] = curr_avg_loss

    # RSI değerlerini hesapla
    rsi_values = np.full(len(series), np.nan)
    for i in range(window, len(series)):
        ag = avg_gain[i]
        al = avg_loss[i]

        if al == 0:
            # Eğer kayıp yoksa ve kazanç varsa RSI 100'dür.
            # Eğer hiç hareket yoksa (ikisi de 0) sonuç NaN kalır.
            rsi_values[i] = 100.0 if ag > 0 else np.nan
        else:
            rs = ag / al
            rsi_values[i] = 100.0 - (100.0 / (1.0 + rs))

    return pd.Series(rsi_values, index=series.index)
