"""İşlem sayısı ve isabet oranı metrikleri (G-017)."""

import numpy as np
import pandas as pd


def trade_count(positions: pd.Series) -> int:
    """Stratejinin yaptığı toplam işlem sayısını (0'dan 1'e geçişleri) hesaplar.

    Başlangıçta pozisyon 1 ise bu da bir işlem olarak sayılır.
    """
    if positions.empty:
        return 0

    changes = positions.diff().fillna(0)
    # 0'dan 1'e geçişler
    counts = int((changes == 1).sum())

    # İlk gün pozisyon 1 ise bu da bir giriştir
    if positions.iloc[0] == 1:
        counts += 1

    return counts


def hit_rate(close: pd.Series, positions: pd.Series) -> float:
    """Kârlı işlemlerin toplam işlem sayısına oranını hesaplar.

    Her işlem için giriş fiyatı (pozisyonun 1 olduğu ilk gün) ve
    çıkış fiyatı (pozisyonun 0'a düştüğü gün veya veri sonu) kullanılarak
    getiri hesaplanır. Getirisi 0'dan büyük olanlar kârlı sayılır.
    """
    if len(close) != len(positions):
        raise ValueError("close ve positions uzunlukları aynı olmalıdır.")

    trades_returns = []
    in_trade = False
    entry_price = 0.0

    for i in range(len(positions)):
        pos = positions.iloc[i]

        if not in_trade and pos == 1:
            # İşleme giriş
            in_trade = True
            entry_price = close.iloc[i]
        elif in_trade and pos == 0:
            # İşlemden çıkış
            in_trade = False
            exit_price = close.iloc[i]
            trades_returns.append(exit_price / entry_price - 1.0)

    # Seri bittiğinde hala işlemdeyse son fiyatla kapat
    if in_trade:
        exit_price = close.iloc[-1]
        trades_returns.append(exit_price / entry_price - 1.0)

    if not trades_returns:
        return np.nan

    profitable_trades = sum(1 for ret in trades_returns if ret > 0)
    return float(profitable_trades / len(trades_returns))
