"""Veri katmanı modülü.

Varlık evreni ve veri indirme/önbellek işlemlerini içerir.
"""

from stratlab.data.loader import load_prices
from stratlab.data.universe import UNIVERSE, all_tickers, group_of

__all__ = ["UNIVERSE", "all_tickers", "group_of", "load_prices"]
