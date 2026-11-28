"""Örnek fiyat verisi fikstürlerinin doğruluğunu kontrol eden testler."""

import pytest
import pandas as pd
from tests.helpers import load_fixture


@pytest.mark.parametrize("fixture_name", ["yukselen", "dalgali"])
def test_fixture_loads_and_row_count(fixture_name):
    """Fikstür başarıyla yüklenmeli ve 60 satır içermeli."""
    df = load_fixture(fixture_name)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 60


@pytest.mark.parametrize("fixture_name", ["yukselen", "dalgali"])
def test_fixture_columns_and_no_missing_values(fixture_name):
    """Sütun adları doğru olmalı ve eksik veri bulunmamalı."""
    df = load_fixture(fixture_name)
    expected_columns = ["open", "high", "low", "close", "volume"]
    assert list(df.columns) == expected_columns
    assert df.index.name == "date"
    assert df.isna().sum().sum() == 0


@pytest.mark.parametrize("fixture_name", ["yukselen", "dalgali"])
def test_fixture_dates_increasing(fixture_name):
    """Tarih indeksi kesinlikle artan sırada olmalı."""
    df = load_fixture(fixture_name)
    assert df.index.is_monotonic_increasing


@pytest.mark.parametrize("fixture_name", ["yukselen", "dalgali"])
def test_fixture_price_bounds(fixture_name):
    """Her satırda en düşük <= açılış, kapanış <= en yüksek koşulu sağlanmalı."""
    df = load_fixture(fixture_name)
    assert (df["low"] <= df["open"]).all()
    assert (df["low"] <= df["close"]).all()
    assert (df["open"] <= df["high"]).all()
    assert (df["close"] <= df["high"]).all()


def test_yukselen_is_strictly_increasing():
    """Yükselen veri setinde kapanış fiyatı her gün bir öncekinden yüksek olmalı."""
    df = load_fixture("yukselen")
    diffs = df["close"].diff().dropna()
    assert (diffs > 0).all()


def test_dalgali_has_minimum_direction_changes():
    """Dalgalı veri setinde kapanış fiyatı en az 5 kez yön değiştirmeli."""
    df = load_fixture("dalgali")
    diffs = df["close"].diff().dropna()
    # İşaret değişimlerini say: diff pozitiften negatife veya negatiften pozitife geçişler
    signs = diffs.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    direction_changes = (signs != signs.shift(1)).iloc[1:].sum()
    assert direction_changes >= 5
