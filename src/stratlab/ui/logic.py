"""Streamlit arayüzü için arka plan hesaplama mantığı (G-019, G-025)."""

import pandas as pd
from stratlab.data.loader import load_prices
from stratlab.data.cleaning import clean_prices
from stratlab.strategies import STRATEGIES
from stratlab.engine.backtest import run_backtest
from stratlab.metrics import (
    total_return,
    annual_return,
    annual_volatility,
    sharpe,
    max_drawdown,
)
from stratlab.metrics.trades import trade_count, hit_rate
from stratlab.reports.comparison import comparison_table


def run_selected(
    ticker: str,
    strategy: str,
    start: str,
    end: str,
    cost_bps: float,
    source=None,
    cache_dir: str = ".cache/prices",
) -> dict:
    """Seçilen varlık ve strateji için backtest çalıştırır, sermaye eğrilerini, metrikleri ve karşılaştırma tablosunu döndürür."""
    df = load_prices(ticker, start, end, source=source, cache_dir=cache_dir)
    
    # G-023: Veri temizliği
    df, notes = clean_prices(df)
    
    if df.empty:
        raise ValueError("Temizlik sonrası veri boş kaldı.")

    close = df["close"]
    strat_func = STRATEGIES[strategy]
    positions = strat_func(close)

    strat_bt = run_backtest(close, positions, cost_bps=cost_bps)
    benchmark_positions = pd.Series(1, index=close.index)
    bench_bt = run_backtest(close, benchmark_positions, cost_bps=cost_bps)

    t_count = trade_count(positions)
    h_rate = hit_rate(close, positions)

    metrics = {
        "Toplam Getiri": total_return(strat_bt["equity"]),
        "Al-tut Toplam Getiri": total_return(bench_bt["equity"]),
        "Yıllık Getiri": annual_return(strat_bt["equity"]),
        "Yıllık Volatilite": annual_volatility(strat_bt["equity"]),
        "Sharpe Oranı": sharpe(strat_bt["equity"]),
        "En Büyük Düşüş": max_drawdown(strat_bt["equity"]),
        "İşlem Sayısı": t_count,
        "İsabet Oranı": h_rate,
    }

    comp_df = comparison_table(strat_bt["equity"], bench_bt["equity"])

    return {
        "strat_equity": strat_bt["equity"],
        "bench_equity": bench_bt["equity"],
        "metrics": metrics,
        "comparison": comp_df,
        "notes": notes,
    }
