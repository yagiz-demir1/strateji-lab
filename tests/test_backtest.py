"""Tek varlık backtest motoru için testler."""

import numpy as np
import pandas as pd
import pytest

from stratlab.engine.backtest import run_backtest


def test_run_backtest_returns_dataframe_with_expected_columns_and_starts_at_one():
    """run_backtest fonksiyonu returns ve equity sütunları olan bir DataFrame döndürmeli ve equity 1.0'dan başlamalıdır."""
    close = pd.Series([100.0, 105.0, 102.0], index=pd.date_range("2025-01-01", periods=3))
    positions = pd.Series([1, 1, 0], index=close.index)
    
    result = run_backtest(close, positions)
    
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["returns", "equity"]
    assert len(result) == len(close)
    assert pytest.approx(result["equity"].iloc[0]) == 1.0
    assert pytest.approx(result["returns"].iloc[0]) == 0.0


def test_lookahead_bias_prevention_position_is_shifted_by_one_day():
    """Bugünkü pozisyon yarının getirisine uygulanmalı, bugünün getirisine etki etmemelidir (gecikme/shift testi)."""
    close = pd.Series([100.0, 110.0, 120.0])
    # İlk gün (t=0) pozisyon 0, ikinci gün (t=1) pozisyon 1
    # t=1'deki fiyat hareketi (100->110) t=0 pozisyonuna (0) tabi olmalı, dolayısıyla getiri 0
    # t=2'deki fiyat hareketi (110->120) t=1 pozisyonuna (1) tabi olmalı, dolayısıyla getiri 120/110 - 1
    positions = pd.Series([0, 1, 0])
    
    result = run_backtest(close, positions)
    
    assert pytest.approx(result["returns"].iloc[1]) == 0.0
    assert pytest.approx(result["returns"].iloc[2]) == (120.0 / 110.0) - 1.0
    assert pytest.approx(result["equity"].iloc[1]) == 1.0
    assert pytest.approx(result["equity"].iloc[2]) == 120.0 / 110.0


def test_all_ones_position_equals_buy_and_hold():
    """Pozisyon serisi hep 1 ise son equity değeri al-tut getirisine (close[-1] / close[0]) eşit olmalıdır."""
    close = pd.Series([100.0, 105.0, 95.0, 110.0, 125.0])
    positions = pd.Series([1, 1, 1, 1, 1])
    
    result = run_backtest(close, positions)
    
    expected_final_equity = close.iloc[-1] / close.iloc[0]
    assert pytest.approx(result["equity"].iloc[-1]) == expected_final_equity


def test_all_zeros_position_returns_zero_and_equity_one():
    """Pozisyon serisi hep 0 ise bütün getiriler 0.0 ve equity sürekli 1.0 olmalıdır."""
    close = pd.Series([100.0, 110.0, 90.0, 120.0])
    positions = pd.Series([0, 0, 0, 0])
    
    result = run_backtest(close, positions)
    
    assert (result["returns"] == 0.0).all()
    assert (result["equity"] == 1.0).all()


def test_five_day_hand_calculated_example():
    """5 günlük elle hesaplanmış senaryoda sermaye eğrisi ve getiriler doğrulanmalıdır."""
    close = pd.Series([100.0, 110.0, 99.0, 99.0, 108.9])
    positions = pd.Series([1, 1, 0, 1, 1])
    
    result = run_backtest(close, positions)
    
    # t0: close 100, pos 1 -> returns 0.0, equity 1.0
    # t1: close 110 (+10%), pos 1 -> t0 pos 1 olduğu için getiri +0.10, equity 1.1
    # t2: close 99 (-10%), pos 0 -> t1 pos 1 olduğu için getiri -0.10, equity 0.99
    # t3: close 99 (0%), pos 1 -> t2 pos 0 olduğu için getiri 0.0, equity 0.99
    # t4: close 108.9 (+10%), pos 1 -> t3 pos 1 olduğu için getiri +0.10, equity 1.089
    expected_returns = [0.0, 0.10, -0.10, 0.0, 0.10]
    expected_equity = [1.0, 1.10, 0.99, 0.99, 1.089]
    
    for actual, expected in zip(result["returns"], expected_returns):
        assert pytest.approx(actual, abs=1e-5) == expected
        
    for actual, expected in zip(result["equity"], expected_equity):
        assert pytest.approx(actual, abs=1e-5) == expected


def test_mismatched_lengths_raise_value_error():
    """close ve positions serilerinin uzunlukları farklı olduğunda ValueError fırlatılmalıdır."""
    close = pd.Series([100.0, 105.0, 110.0])
    positions = pd.Series([1, 1])
    
    with pytest.raises(ValueError):
        run_backtest(close, positions)
