"""Testler için yardımcı fonksiyonlar."""

from pathlib import Path
import pandas as pd


def load_fixture(name: str) -> pd.DataFrame:
    """Verilen ada sahip CSV fikstürünü okur ve tarih indeksli DataFrame döndürür."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    file_path = fixtures_dir / f"{name}.csv"
    df = pd.read_csv(file_path, parse_dates=["date"], index_col="date")
    return df
