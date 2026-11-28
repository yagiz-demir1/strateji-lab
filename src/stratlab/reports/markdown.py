"""Markdown raporu üretim fonksiyonları (G-008, G-024)."""

import pandas as pd
from stratlab.metrics import (
    total_return,
    annual_return,
    annual_volatility,
    sharpe,
    max_drawdown,
)
from stratlab.reports.format import fmt_pct, fmt_num


def make_report(name: str, strategy_equity: pd.Series, benchmark_equity: pd.Series) -> str:
    """Strateji ve al-tut performansını karşılaştıran Markdown raporu oluşturur.

    Metrikler G-006 modülündeki fonksiyonlar kullanılarak hesaplanır.
    Sayılar G-024 formatlama kurallarına göre Türkçe biçimdedir.
    """

    # Metrik tanımları: (Etiket, Fonksiyon, Formatlayıcı)
    metrics_def = [
        ("Toplam Getiri", total_return, fmt_pct),
        ("Yıllık Getiri", annual_return, fmt_pct),
        ("Yıllık Volatilite", annual_volatility, fmt_pct),
        ("Sharpe Oranı", sharpe, fmt_num),
        ("En Büyük Düşüş", max_drawdown, fmt_pct),
    ]

    lines = [f"# {name}", ""]
    lines.append("| Metrik | Strateji | Al-tut | Fark |")
    lines.append("| :--- | :---: | :---: | :---: |")

    for label, func, formatter in metrics_def:
        s_val = func(strategy_equity)
        b_val = func(benchmark_equity)

        # Fark hesapla (strateji - al-tut)
        if pd.notna(s_val) and pd.notna(b_val):
            diff = s_val - b_val
        else:
            diff = float("nan")

        lines.append(f"| {label} | {formatter(s_val)} | {formatter(b_val)} | {formatter(diff)} |")

    return "\n".join(lines)
