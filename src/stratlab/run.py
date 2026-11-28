"""Komut satırından backtest çalıştırma ve raporlama modülü (G-018)."""

import argparse
import sys
from datetime import date
from pathlib import Path
import pandas as pd

from stratlab.data.loader import load_prices
from stratlab.data.cleaning import clean_prices
from stratlab.strategies import STRATEGIES
from stratlab.engine.backtest import run_backtest
from stratlab.reports.markdown import make_report
from stratlab.metrics.trades import trade_count, hit_rate


def main(argv: list[str] | None = None, source=None) -> int:
    """Komut satırı argümanlarını ayrıştırır, veriyi yükler, temizler, backtest çalıştırır ve rapor üretir.

    Başarılı olursa 0, hata durumunda uygun çıkış kodu (bilinmeyen strateji için 2) döndürür.
    """
    parser = argparse.ArgumentParser(description="Strateji Laboratuvarı Backtest CLI")
    parser.add_argument("--ticker", required=True, help="Varlık sembolü (örn. THYAO.IS)")
    parser.add_argument("--strategy", required=True, help="Strateji adı")
    parser.add_argument("--start", required=True, help="Başlangıç tarihi (YYYY-AA-GG)")
    parser.add_argument("--end", default=date.today().strftime("%Y-%m-%d"), help="Bitiş tarihi")
    parser.add_argument("--cost-bps", type=float, default=10.0, help="İşlem maliyeti (baz puan)")
    parser.add_argument("--reports-dir", default="reports", help="Raporların kaydedileceği klasör")
    parser.add_argument("--cache-dir", default=".cache/prices", help="İndirilen fiyatların saklandığı klasör")

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2

    if args.strategy not in STRATEGIES:
        print(f"Hata: Bilinmeyen strateji '{args.strategy}'. Mevcutlar: {list(STRATEGIES.keys())}")
        return 2

    try:
        # Veriyi yükle
        df = load_prices(args.ticker, args.start, args.end, source=source, cache_dir=args.cache_dir)
    except Exception as e:
        print(f"Veri yükleme hatası: {e}")
        return 1

    # G-023: Veri temizliği
    df, data_notes = clean_prices(df)
    
    if df.empty:
        print("Hata: Temizlik sonrası veri boş kaldı.")
        return 1

    close = df["close"]
    
    # Strateji pozisyonlarını üret
    strat_func = STRATEGIES[args.strategy]
    try:
        positions = strat_func(close)
    except Exception as e:
        print(f"Strateji çalıştırma hatası: {e}")
        return 1

    # Backtest çalıştır (strateji)
    strat_bt = run_backtest(close, positions, cost_bps=args.cost_bps)
    
    # Al-tut backtest (hep 1 pozisyon)
    benchmark_positions = pd.Series(1, index=close.index)
    bench_bt = run_backtest(close, benchmark_positions, cost_bps=args.cost_bps)

    # Rapor üret
    strategy_display_name = f"{args.ticker} – {args.strategy}"
    report_md = make_report(strategy_display_name, strat_bt["equity"], bench_bt["equity"])

    # İşlem sayısı ve isabet oranı satırlarını rapora ekle
    t_count = trade_count(positions)
    h_rate = hit_rate(close, positions)
    h_rate_str = "N/A" if pd.isna(h_rate) else f"%{h_rate * 100:.2f}"

    report_md += f"\n\n## İşlem İstatistikleri\n"
    report_md += f"- **İşlem Sayısı:** {t_count}\n"
    report_md += f"- **İsabet Oranı:** {h_rate_str}\n"

    # G-023: Veri notlarını rapora ekle
    if data_notes:
        report_md += f"\n## Veri notları\n"
        for note in data_notes:
            report_md += f"- {note}\n"

    # Raporu dosyaya yaz
    reports_path = Path(args.reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)
    
    report_file = reports_path / f"{args.ticker}_{args.strategy}.md"
    report_file.write_text(report_md, encoding="utf-8")

    print(f"Rapor başarıyla oluşturuldu: {report_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
