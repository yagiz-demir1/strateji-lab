"""Fiyat verisi indirme ve yerel önbellek katmanı (G-010)."""

from collections.abc import Callable
from pathlib import Path
import pandas as pd


def _fetch_yfinance(ticker: str, start: str, end: str) -> pd.DataFrame:
    """yfinance üzerinden bölünme ve temettü düzeltilmiş günlük fiyat verisini çeker."""
    import yfinance as yf

    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(col).lower() for col in df.columns]
    return df


def load_prices(
    ticker: str,
    start: str,
    end: str,
    source: Callable[..., pd.DataFrame] | None = None,
    cache_dir: str = ".cache/prices",
) -> pd.DataFrame:
    """Tarih indeksli ve OHLCV sütunlarına sahip fiyat verisini yerel önbellekle birlikte yükler.

    Önbellekte veri varsa doğrudan okunur. Yoksa kaynak fonksiyonundan (varsayılan: yfinance)
    alınarak önbelleğe CSV olarak yazılır.
    """
    cache_path = Path(cache_dir) / f"{ticker}_{start}_{end}.csv"

    if cache_path.exists():
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        inferred = pd.infer_freq(df.index)
        if inferred is not None:
            df.index.freq = inferred
        return df

    if source is not None:
        raw_data = source(ticker, start, end)
    else:
        raw_data = _fetch_yfinance(ticker, start, end)

    if raw_data is None or raw_data.empty:
        raise ValueError(f"{ticker} için veri boş döndü veya bulunamadı.")

    df = raw_data.copy()
    df.columns = [str(col).lower() for col in df.columns]

    required_columns = ["open", "high", "low", "close", "volume"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Veride gerekli sütunlar eksik: {missing}")

    df = df[required_columns]
    df.index = pd.to_datetime(df.index)

    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    df.to_csv(cache_path)

    return df
