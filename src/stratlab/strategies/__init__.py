"""Stratejiler modülü."""

from stratlab.strategies.ma_crossover import ma_crossover_positions
from stratlab.strategies.rsi_reversion import (
    threshold_positions,
    rsi_reversion_positions,
)
from stratlab.strategies.momentum import momentum_positions
from stratlab.strategies.bollinger_breakout import bollinger_breakout_positions
from stratlab.strategies.macd_strategy import macd_positions


def _wrapped_ma_crossover(close):
    """ma_crossover_positions fonksiyonunu varsayılan parametrelerle (fast=50, slow=200) sarmalar."""
    return ma_crossover_positions(close, fast=50, slow=200)


def _wrapped_rsi_reversion(close):
    """rsi_reversion_positions fonksiyonunu varsayılan parametrelerle sarmalar."""
    return rsi_reversion_positions(close, window=14, low=30.0, high=70.0)


def _wrapped_momentum(close):
    """momentum_positions fonksiyonunu varsayılan parametrelerle sarmalar."""
    return momentum_positions(close, lookback=252, skip=21)


def _wrapped_bollinger(close):
    """bollinger_breakout_positions fonksiyonunu varsayılan parametrelerle sarmalar."""
    return bollinger_breakout_positions(close, window=20, k=2.0)


def _wrapped_macd(close):
    """macd_positions fonksiyonunu varsayılan parametrelerle sarmalar."""
    return macd_positions(close, fast=12, slow=26, signal=9)


STRATEGIES = {
    "ma_crossover": _wrapped_ma_crossover,
    "rsi_reversion": _wrapped_rsi_reversion,
    "momentum_12_1": _wrapped_momentum,
    "bollinger_breakout": _wrapped_bollinger,
    "macd": _wrapped_macd,
}

__all__ = [
    "ma_crossover_positions",
    "threshold_positions",
    "rsi_reversion_positions",
    "momentum_positions",
    "bollinger_breakout_positions",
    "macd_positions",
    "STRATEGIES",
]
