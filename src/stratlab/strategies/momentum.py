"""12-1 momentum stratejisi (G-014)."""

import pandas as pd


def momentum_positions(close: pd.Series, lookback: int = 252, skip: int = 21) -> pd.Series:
    """12-1 momentum stratejisine göre pozisyon serisi (0 veya 1) üretir.

    Son bir yılın getirisi (son skip gün hariç) pozitifse alımda kal (1), değilse nakitte ol (0).
    Formül: close[t - skip] / close[t - lookback] - 1
    İlk lookback gün boyunca pozisyon 0 olur.
    """
    if lookback < 1 or skip < 1:
        raise ValueError("lookback ve skip 1'den küçük olamaz.")
    if skip >= lookback:
        raise ValueError("skip değeri lookback değerinden küçük olmalıdır.")

    positions = pd.Series(0, index=close.index, dtype=int)

    if len(close) <= lookback:
        return positions

    shifted_end = close.shift(skip)
    shifted_start = close.shift(lookback)
    returns = (shifted_end / shifted_start) - 1.0

    valid_mask = returns > 0.0
    positions.loc[valid_mask] = 1
    positions.iloc[:lookback] = 0

    return positions
