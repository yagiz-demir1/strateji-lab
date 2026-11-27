"""Testler için yardımcı fonksiyonlar ve veri okuyucular."""

import os
import pandas as pd


def load_fixture(name: str) -> pd.DataFrame:
    """Belirtilen örnek fiyat verisini (fixture) okur ve DataFrame döndürür."""
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "fixtures", f"{name}.csv")
    df = pd.read_csv(file_path, parse_dates=["date"], index_col="date")
    return df
