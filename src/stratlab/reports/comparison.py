"""Strateji ve al-tut performans metriklerini yan yana karşılaştıran tablo modülü (G-025)."""

import pandas as pd
from stratlab.metrics import (
    total_return,
    annual_return,
    annual_volatility,
    sharpe,
    max_drawdown,
)


def comparison_table(strategy_equity: pd.Series, benchmark_equity: pd.Series) -> pd.DataFrame:
    """Strateji ve al-tut sermaye eğrilerini temel metrikler üzerinden karşılaştıran DataFrame üretir.

    Sütunlar: Strateji, Al-tut, Fark (Strateji - Al-tut).
    İndeksler: Toplam Getiri, Yıllık Getiri, Yıllık Volatilite, Sharpe Oranı, En Büyük Düşüş.
    """
    metrics_def = [
        ("Toplam Getiri", total_return),
        ("Yıllık Getiri", annual_return),
        ("Yıllık Volatilite", annual_volatility),
        ("Sharpe Oranı", sharpe),
        ("En Büyük Düşüş", max_drawdown),
    ]

    rows = []
    index_labels = []

    for label, func in metrics_def:
        s_val = func(strategy_equity)
        b_val = func(benchmark_equity)
        
        if pd.notna(s_val) and pd.notna(b_val):
            diff = s_val - b_val
        else:
            diff = float("nan")
            
        rows.append({
            "Strateji": s_val,
            "Al-tut": b_val,
            "Fark": diff
        })
        index_labels.append(label)

    return pd.DataFrame(rows, index=index_labels)
