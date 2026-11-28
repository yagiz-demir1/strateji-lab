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
    positions = pd.Series([0, 1, 0])
    
    result = run_backtest(close, positions)
    
    assert pytest.approx(result["returns"].iloc[1]) == 0.0
    assert pytest.approx(result["returns"].iloc[2]) == (120.0 / 110.0) - 1.0
    assert pytest.approx(result["equity"].iloc[1]) == 1.0
    assert pytest.approx(result["equity"].iloc[2]) == 120.0 / 110.0


def test_all_ones_position_equals_buy_and_hold():
    """Pozisyon serisi hep 1 ise son equity değeri al-tut getirisine eşit olmalıdır."""
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


def test_backtest_cost_bps_default_and_behavior():
    """cost_bps parametresi eklendiğinde varsayılanı 0 kalmalı ve maliyet pozisyon değişimlerinde yansıtılmalıdır."""
    close = pd.Series([100.0, 100.0, 100.0, 100.0])
    # t=0: pos 0, t=1: pos 1 (değişim var, maliyet uygulanır), t=2: pos 1 (değişim yok), t=3: pos 0 (değişim var, maliyet uygulanır)
    positions = pd.Series([0, 1, 1, 0])
    
    # cost_bps = 0 iken equity değişmemeli
    res_0 = run_backtest(close, positions, cost_bps=0)
    assert pytest.approx(res_0["equity"].iloc[-1]) == 1.0

    # cost_bps = 10 iken (0.1% komisyon/spread)
    # t=1'de pozisyon 0 -> 1 (maliyet: * 0.999)
    # t=3'te pozisyon 1 -> 0 (maliyet: * 0.999)
    res_cost = run_backtest(close, positions, cost_bps=10)
    expected_final = 1.0 * (1.0 - 10 / 10000.0) * (1.0 - 10 / 10000.0)
    assert pytest.approx(res_cost["equity"].iloc[-1]) == expected_final


def test_backtest_negative_cost_bps_raises_value_error():
    """Negatif cost_bps değeri ValueError fırlatmalıdır."""
    close = pd.Series([100.0, 105.0, 110.0])
    positions = pd.Series([0, 1, 1])
    with pytest.raises(ValueError):
        run_backtest(close, positions, cost_bps=-1.0)
