"""Bollinger Bantlari gostergesi icin testler (G-011)."""
import numpy as np
import pandas as pd
import pytest
from stratlab.indicators.bollinger import bollinger

def test_bollinger_returns_dataframe_with_correct_columns():
    """bollinger fonksiyonu mid, upper, lower sutunlari olan bir DataFrame dondurmelidir."""
    close = pd.Series([10.0] * 30)
    result = bollinger(close, window=20, k=2)
    
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["mid", "upper", "lower"]
    assert len(result) == len(close)

def test_bollinger_constant_series_bands_are_equal():
    """Sabit fiyatli bir seride upper == lower == mid olmalidir."""
    close = pd.Series([100.0] * 30)
    result = bollinger(close, window=20, k=2)
    
    # Ilk window-1 gun NaN olabilir, ondan sonrasini kontrol et
    valid_range = result.iloc[19:]
    assert (valid_range["upper"] == valid_range["mid"]).all()
    assert (valid_range["lower"] == valid_range["mid"]).all()

def test_bollinger_mid_is_sma():
    """mid sutunu basit hareketli ortalamaya (SMA) esit olmalidir."""
    close = pd.Series([10.0, 12.0, 14.0, 16.0, 18.0])
    result = bollinger(close, window=2, k=2)
    # SMA window=2: [NaN, 11, 13, 15, 17]
    expected_mid = [np.nan, 11.0, 13.0, 15.0, 17.0]
    pd.testing.assert_series_equal(result["mid"], pd.Series(expected_mid, name="mid"))

def test_bollinger_calculation_with_k():
    """Bant genisligi k * standart sapma (ddof=0) olarak hesaplanmalidir."""
    # Veri: [10, 20], window=2, k=2
    # SMA = 15
    # Std (ddof=0) = sqrt(((10-15)^2 + (20-15)^2) / 2) = 5.0
    # Upper = 15 + 2*5 = 25
    # Lower = 15 - 2*5 = 5
    close = pd.Series([10.0, 20.0])
    result = bollinger(close, window=2, k=2)
    assert pytest.approx(result["upper"].iloc[1]) == 25.0
    assert pytest.approx(result["lower"].iloc[1]) == 5.0
