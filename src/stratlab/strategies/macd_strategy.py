"""MACD stratejisi (G-016).

MACD &#231;izgisinin sinyal &#231;izgisini yukarı kestiēi ve &#252;st&#252;nde kaldıēı
durumlarda alımda kalma (1) mantıēını uygular.
"""

import pandas as pd
from stratlab.indicators.macd import macd


def cross_positions(a: pd.Series, b: pd.Series) -> pd.Series:
    """İki seriyi karőılaőtırarak a > b olduēu durumlarda 1, aksi halde 0 d&#246;nd&#252;r&#252;r.

    Serilerden en az biri NaN ise sonu&#221; 0 olur.
    """
    # pandas karőılaőtırması NaN olan yerlerde False d&#246;nd&#252;r&#252;r.
    return (a > b).astype(int)


def macd_positions(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.Series:
    """MACD ve sinyal &#231;izgisi kesiőimine g&#246;re pozisyon serisi &#252;retir.

    MACD > Sinyal ise pozisyon 1, aksi halde 0'dır.
    """
    df = macd(close, fast=fast, slow=slow, signal=signal)
    return cross_positions(df["macd"], df["signal"])
