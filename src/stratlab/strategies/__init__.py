"""Stratejiler modülü."""

from stratlab.strategies.ma_crossover import ma_crossover_positions
from stratlab.strategies.rsi_reversion import (
    threshold_positions,
    rsi_reversion_positions,
)
from stratlab.strategies.momentum import momentum_positions
from stratlab.strategies.bollinger_breakout import bollinger_breakout_positions
from stratlab.strategies.macd_strategy import macd_positions

STRATEGY_PARAMS = {
    "ma_crossover": {"fast": 50, "slow": 200},
    "rsi_reversion": {"window": 14, "low": 30.0, "high": 70.0},
    "momentum_12_1": {"lookback": 252, "skip": 21},
    "bollinger_breakout": {"window": 20, "k": 2.0},
    "macd": {"fast": 12, "slow": 26, "signal": 9},
}


def _wrapped_ma_crossover(close):
    """ma_crossover_positions fonksiyonunu varsayılan parametrelerle sarmalar."""
    return ma_crossover_positions(close, **STRATEGY_PARAMS["ma_crossover"])


def _wrapped_rsi_reversion(close):
    """rsi_reversion_positions fonksiyonunu varsayılan parametrelerle sarmalar."""
    return rsi_reversion_positions(close, **STRATEGY_PARAMS["rsi_reversion"])


def _wrapped_momentum(close):
    """momentum_positions fonksiyonunu varsayılan parametrelerle sarmalar."""
    return momentum_positions(close, **STRATEGY_PARAMS["momentum_12_1"])


def _wrapped_bollinger(close):
    """bollinger_breakout_positions fonksiyonunu varsayılan parametrelerle sarmalar."""
    return bollinger_breakout_positions(close, **STRATEGY_PARAMS["bollinger_breakout"])


def _wrapped_macd(close):
    """macd_positions fonksiyonunu varsayılan parametrelerle sarmalar."""
    return macd_positions(close, **STRATEGY_PARAMS["macd"])


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
    "STRATEGY_PARAMS",
]
