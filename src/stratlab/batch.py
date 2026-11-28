"""Toplu backtest çalıştırma ve sonuçları veritabanına kaydetme modülü (G-027)."""

import argparse
import sys
from datetime import date
import pandas as pd

from stratlab.data.universe import all_tickers, group_of
from stratlab.metrics import max_drawdown, sharpe, total_return
from stratlab.strategies import STRATEGIES, STRATEGY_PARAMS
from stratlab.ui.logic import run_selected
from stratlab.results.db import save_run


def run_batch(
    tickers: list[str] | str,
    strategies: list[str] | str,
    start: str,
    end: str,
    cost_bps: float,
    db_path: str,
    source=None,
    cache_dir: str = ".cache/prices",
) -> pd.DataFrame:
    """Seçilen varlık ve stratejilerin tüm kombinasyonları için backtest çalıştırır ve sonuçları SQLite'a kaydeder.

    Hata durumunda çalışma durmaz, error alanına hata mesajı yazılır.
    """
    if tickers == "all":
        t_list = all_tickers()
    elif isinstance(tickers, str):
        t_list = [t.strip() for t in tickers.split(",")]
    else:
        t_list = list(tickers)

    if strategies == "all":
        s_list = list(STRATEGIES.keys())
    elif isinstance(strategies, str):
        s_list = [s.strip() for s in strategies.split(",")]
    else:
        s_list = list(strategies)

    run_records = []

    for ticker in t_list:
        try:
            grp = group_of(ticker)
        except KeyError:
            grp = "unknown"

        for strategy in s_list:
            params = STRATEGY_PARAMS.get(strategy, {})
            run_dict = {
                "ticker": ticker,
                "grp": grp,
                "strategy": strategy,
                "params": params,
                "start": start,
                "end": end,
                "cost_bps": cost_bps,
                "period": "gelistirme",
                "error": None,
            }

            try:
                res = run_selected(
                    ticker=ticker,
                    strategy=strategy,
                    start=start,
                    end=end,
                    cost_bps=cost_bps,
                    source=source,
                    cache_dir=cache_dir,
                )
                metrics = res["metrics"]
                notes_list = res.get("notes", [])
                notes_str = "; ".join(notes_list) if notes_list else None

                # Al-tut metrikleri her zaman al-tut sermaye eğrisinden hesaplanır.
                bench_eq = res["bench_equity"]
                bench_total = total_return(bench_eq)
                bench_sharpe = sharpe(bench_eq)
                bench_mdd = max_drawdown(bench_eq)

                strat_eq = res["strat_equity"]

                run_dict.update({
                    "total_return": metrics.get("Toplam Getiri"),
                    "annual_return": metrics.get("Yıllık Getiri"),
                    "annual_volatility": metrics.get("Yıllık Volatilite"),
                    "sharpe": metrics.get("Sharpe Oranı"),
                    "max_drawdown": metrics.get("En Büyük Düşüş"),
                    "trades": int(metrics.get("İşlem Sayısı", 0)),
                    "hit_rate": metrics.get("İsabet Oranı"),
                    "bench_total_return": bench_total,
                    "bench_sharpe": bench_sharpe,
                    "bench_max_drawdown": bench_mdd,
                    "n_days": len(strat_eq),
                    "notes": notes_str,
                })
            except Exception as e:
                run_dict.update({
                    "total_return": None,
                    "annual_return": None,
                    "annual_volatility": None,
                    "sharpe": None,
                    "max_drawdown": None,
                    "trades": None,
                    "hit_rate": None,
                    "bench_total_return": None,
                    "bench_sharpe": None,
                    "bench_max_drawdown": None,
                    "n_days": None,
                    "notes": None,
                    "error": str(e),
                })

            save_run(db_path, run_dict)
            run_records.append(run_dict)

    return pd.DataFrame(run_records)


def main(argv: list[str] | None = None, source=None) -> int:
    """Komut satırından toplu backtest çalıştırır (source testlerde sahte veri kaynağı için)."""
    parser = argparse.ArgumentParser(description="Strateji Laboratuvarı Toplu Backtest CLI")
    parser.add_argument("--tickers", default="all", help="Varlıklar (all veya virgülle ayrılmış)")
    parser.add_argument("--strategies", default="all", help="Stratejiler (all veya virgülle ayrılmış)")
    parser.add_argument("--start", required=True, help="Başlangıç tarihi (YYYY-AA-GG)")
    parser.add_argument("--end", default=date.today().strftime("%Y-%m-%d"), help="Bitiş tarihi")
    parser.add_argument("--cost-bps", type=float, default=10.0, help="İşlem maliyeti (baz puan)")
    parser.add_argument("--db", default="results/sonuclar.sqlite", help="SQLite veritabanı yolu")
    parser.add_argument("--cache-dir", default=".cache/prices", help="İndirilen fiyatların saklandığı klasör")

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2

    try:
        run_batch(
            tickers=args.tickers,
            strategies=args.strategies,
            start=args.start,
            end=args.end,
            cost_bps=args.cost_bps,
            db_path=args.db,
            source=source,
            cache_dir=args.cache_dir,
        )
        print(f"Toplu çalıştırma tamamlandı. Sonuçlar: {args.db}")
        return 0
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
