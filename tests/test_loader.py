"""Fiyat verisi indirme ve yerel önbellekleme (G-010) testleri."""

from unittest.mock import MagicMock
import pandas as pd
import pytest

from stratlab.data.loader import load_prices


def _create_dummy_df() -> pd.DataFrame:
    """Testler için örnek OHLCV DataFrame üretir."""
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    return pd.DataFrame(
        {
            "open": [10.0, 11.0, 12.0, 13.0, 14.0],
            "high": [10.5, 11.5, 12.5, 13.5, 14.5],
            "low": [9.5, 10.5, 11.5, 12.5, 13.5],
            "close": [10.2, 11.2, 12.2, 13.2, 14.2],
            "volume": [1000, 1100, 1200, 1300, 1400],
        },
        index=dates,
    )


def test_load_prices_returns_dataframe_with_expected_columns_and_date_index(tmp_path):
    """load_prices sütunları open, high, low, close, volume olan tarih indeksli bir DataFrame döndürmelidir."""
    fake_data = _create_dummy_df()
    fake_source = MagicMock(return_value=fake_data)

    df = load_prices(
        ticker="TEST",
        start="2024-01-01",
        end="2024-01-05",
        source=fake_source,
        cache_dir=str(tmp_path),
    )

    assert isinstance(df, pd.DataFrame)
    expected_columns = ["open", "high", "low", "close", "volume"]
    assert list(df.columns) == expected_columns
    assert isinstance(df.index, pd.DatetimeIndex)
    assert len(df) == 5


def test_load_prices_caching_avoids_second_source_call(tmp_path):
    """İlk çağrıda veri önbelleğe yazılmalı, aynı parametrelerle ikinci çağrıda kaynak fonksiyon tekrar çağrılmamalıdır."""
    fake_data = _create_dummy_df()
    fake_source = MagicMock(return_value=fake_data)

    # İlk çağrı: kaynak çağrılmalı ve dosya önbelleğe yazılmalı
    df1 = load_prices(
        ticker="THYAO.IS",
        start="2024-01-01",
        end="2024-01-05",
        source=fake_source,
        cache_dir=str(tmp_path),
    )
    assert fake_source.call_count == 1
    pd.testing.assert_frame_equal(df1, fake_data)

    # İkinci çağrı: aynı parametrelerle çağrıldığında kaynak tekrar çağrılmamalı (sayaç 1 kalmalı)
    df2 = load_prices(
        ticker="THYAO.IS",
        start="2024-01-01",
        end="2024-01-05",
        source=fake_source,
        cache_dir=str(tmp_path),
    )
    assert fake_source.call_count == 1
    pd.testing.assert_frame_equal(df1, df2)


def test_load_prices_raises_value_error_on_empty_data(tmp_path):
    """Kaynak boş veri döndürürse ValueError fırlatılmalıdır."""
    empty_df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    fake_source = MagicMock(return_value=empty_df)

    with pytest.raises(ValueError):
        load_prices(
            ticker="EMPTY.IS",
            start="2024-01-01",
            end="2024-01-05",
            source=fake_source,
            cache_dir=str(tmp_path),
        )


def test_load_prices_uses_yfinance_when_source_is_none(monkeypatch, tmp_path):
    """source verilmediğinde yfinance indirme fonksiyonu kullanılmalıdır."""
    mock_yf_download = MagicMock(return_value=_create_dummy_df())
    monkeypatch.setattr("stratlab.data.loader._fetch_yfinance", mock_yf_download)

    df = load_prices(
        ticker="MSFT",
        start="2024-01-01",
        end="2024-01-05",
        source=None,
        cache_dir=str(tmp_path),
    )

    assert mock_yf_download.call_count == 1
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
