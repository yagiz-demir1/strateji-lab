"""MACD stratejisi (G-016).

MACD çizgisi sinyal çizgisinin üstündeyken alımda kalma (1), altındayken nakitte kalma (0)
mantığını uygular.
"""

import pandas as pd
from stratlab.indicators.macd import macd


def cross_positions(a: pd.Series, b: pd.Series) -> pd.Series:
    """İki seriyi karşılaştırır: a > b olan günler 1, diğerleri 0.

    Serilerden en az biri NaN ise sonuç 0 olur.
    """
    # pandas karşılaştırması NaN olan yerlerde False döndürür.
    return (a > b).astype(int)


def macd_positions(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.Series:
    """MACD ve sinyal çizgisi kesişimine göre pozisyon serisi üretir.

    MACD > Sinyal ise pozisyon 1, aksi halde 0'dır.
    """
    df = macd(close, fast=fast, slow=slow, signal=signal)
    return cross_positions(df["macd"], df["signal"])
