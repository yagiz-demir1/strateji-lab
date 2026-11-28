"""Faz 1 bitme şartının gerçek veriyle kontrolü.

Çekirdek evrendeki her varlıkta beş stratejiyi gerçek (yfinance) fiyatlarla çalıştırır ve
sonuçları tek bir Markdown tablosuna yazar. Testlerin parçası değildir (internete çıkar);
GitHub Actions'ta elle çalıştırılır: .github/workflows/gercek-veri.yml
"""

import sys
from datetime import date

from stratlab.data.universe import UNIVERSE
from stratlab.strategies import STRATEGIES
from stratlab.ui.logic import run_selected


def pct(value: float) -> str:
    return "–" if value != value else f"{value * 100:.1f}"


def main(start: str = "2015-01-01") -> int:
    end = date.today().isoformat()
    lines = [
        f"## Gerçek veri kontrolü ({start} – {end}, maliyet 10 bps)",
        "",
        "| Grup | Varlık | Strateji | Strateji getirisi (%) | Al-tut getirisi (%) | Sharpe | İşlem |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    errors = 0
    for group, tickers in UNIVERSE.items():
        for ticker in tickers:
            for name in STRATEGIES:
                try:
                    result = run_selected(ticker, name, start, end, 10.0, cache_dir=".cache/prices")
                    m = result["metrics"]
                    sharpe = m["Sharpe Oranı"]
                    lines.append(
                        f"| {group} | {ticker} | {name} | {pct(m['Toplam Getiri'])} | "
                        f"{pct(m['Al-tut Toplam Getiri'])} | {'–' if sharpe != sharpe else f'{sharpe:.2f}'} | "
                        f"{m['İşlem Sayısı']} |"
                    )
                except Exception as err:  # bir varlıktaki hata diğerlerini durdurmasın
                    errors += 1
                    lines.append(f"| {group} | {ticker} | {name} | HATA: {str(err)[:80]} | | | |")
    lines += ["", f"Hatalı satır: {errors} / {sum(len(t) for t in UNIVERSE.values()) * len(STRATEGIES)}"]
    print("\n".join(lines))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
