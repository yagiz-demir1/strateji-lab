import os
import pandas as pd
import pytest

from tests.helpers import load_fixture


def test_fixture_dosyalari_var_mi():
    assert os.path.exists("tests/fixtures/yukselen.csv")
    assert os.path.exists("tests/fixtures/dalgali.csv")


def test_yukselen_fixture_kurallari():
    df = load_fixture("yukselen")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 60
    expected_columns = ["open", "high", "low", "close", "volume"]
    for col in expected_columns:
        assert col in df.columns
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.is_monotonic_increasing
    assert df.isnull().sum().sum() == 0
    assert (df["low"] <= df["open"]).all()
    assert (df["low"] <= df["close"]).all()
    assert (df["open"] <= df["high"]).all()
    assert (df["close"] <= df["high"]).all()
    closes = df["close"].values
    for i in range(1, len(closes)):
        assert closes[i] > closes[i - 1]


def test_dalgali_fixture_kurallari():
    df = load_fixture("dalgali")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 60
    expected_columns = ["open", "high", "low", "close", "volume"]
    for col in expected_columns:
        assert col in df.columns
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.is_monotonic_increasing
    assert df.isnull().sum().sum() == 0
    assert (df["low"] <= df["open"]).all()
    assert (df["low"] <= df["close"]).all()
    assert (df["open"] <= df["high"]).all()
    assert (df["close"] <= df["high"]).all()
    closes = df["close"].values
    changes = 0
    direction = 0
    for i in range(1, len(closes)):
        if closes[i] > closes[i - 1]:
            new_dir = 1
        elif closes[i] < closes[i - 1]:
            new_dir = -1
        else:
            continue
        if direction != 0 and new_dir != direction:
            changes += 1
        direction = new_dir
    assert changes >= 5
