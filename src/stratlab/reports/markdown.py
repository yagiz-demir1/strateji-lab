"""Markdown raporu üretim fonksiyonları (G-008, G-024, G-025)."""

import pandas as pd
from stratlab.reports.comparison import comparison_table
from stratlab.reports.format import fmt_pct, fmt_num


def make_report(name: str, strategy_equity: pd.Series, benchmark_equity: pd.Series) -> str:
    """Strateji ve al-tut performansını karşılaştıran Markdown raporu oluşturur.

    Metrikler comparison_table fonksiyonu kullanılarak hesaplanır.
    Sayılar G-024 formatlama kurallarına göre Türkçe biçimdedir.
    """
    comp_df = comparison_table(strategy_equity, benchmark_equity)

    lines = [f"# {name}", ""]
    lines.append("| Metrik | Strateji | Al-tut | Fark |")
    lines.append("| :--- | :---: | :---: | :---: |")

    for label, row in comp_df.iterrows():
        s_val = row["Strateji"]
        b_val = row["Al-tut"]
        diff = row["Fark"]

        # Sharpe Oranı için fmt_num, diğerleri için fmt_pct kullanılır
        formatter = fmt_num if label == "Sharpe Oranı" else fmt_pct

        lines.append(
            f"| {label} | {formatter(s_val)} | {formatter(b_val)} | {formatter(diff)} |"
        )

    return "\n".join(lines)
