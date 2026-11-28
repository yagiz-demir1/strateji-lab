"""Strateji kartlari (G-029) icin testler."""

import datetime
import pytest
from stratlab.strategies import STRATEGIES, STRATEGY_PARAMS
try:
    from stratlab.strategies.cards import StrategyCard, CARDS
except ImportError:
    StrategyCard = None
    CARDS = {}


def test_strategy_cards_exist_for_all_strategies():
    """STRATEGIES icindeki her strateji icin bir StrategyCard tanimli olmalidir."""
    assert StrategyCard is not None, "StrategyCard sinifi tanimlanmamis"
    for strat_name in STRATEGIES.keys():
        assert strat_name in CARDS, f"{strat_name} icin strateji karti eksik"
        card = CARDS[strat_name]
        assert isinstance(card, StrategyCard)
        assert card.name == strat_name
        assert bool(card.title)
        assert bool(card.source)
        assert bool(card.hypothesis)
        assert isinstance(card.rules, list) and len(card.rules) > 0
        assert isinstance(card.params, dict)
        # Parametreler STRATEGY_PARAMS ile eslesmeli
        assert card.params == STRATEGY_PARAMS.get(strat_name, {})
        # Eklenme tarihi YYYY-MM-DD formatinda olmali
        try:
            datetime.date.fromisoformat(card.added)
        except ValueError:
        	pytest.fail(f"{strat_name} eklenme tarihi YYYY-MM-DD formatinda degil: {card.added}")


def test_specific_sources():
    """Belirtilen akademik ve klasik kaynaklar kartlarda dogru yer almali."""
    assert "Brock" in CARDS["ma_crossover"].source
    assert "Wilder" in CARDS["rsi_reversion"].source
    assert "Moskowitz" in CARDS["momentum_12_1"].source
    assert "Bollinger" in CARDS["bollinger_breakout"].source
    assert "Appel" in CARDS["macd"].source
