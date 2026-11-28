"""Islem sayisi ve isabet orani metrikleri icin testler (G-017)."""

import numpy as np
import pandas as pd
import pytest
from stratlab.metrics.trades import trade_count, hit_rate


def test_trade_count_hand_calculated():
    """Gorev tanimindaki trade_count ornegi dogrulanmalidir."""
    # [0, 1, 1, 0, 1, 0] -> 2 islem (0'dan 1'e gecisler)
    positions = pd.Series([0, 1, 1, 0, 1, 0])
    assert trade_count(positions) == 2


def test_trade_count_starts_with_one():
    """Seri 1 ile basliyorsa bu da bir islem olarak sayilmalidir (nakitten gecis)."""
    # [1, 1, 0, 1, 0] -> 2 islem
    positions = pd.Series([1, 1, 0, 1, 0])
    assert trade_count(positions) == 2


def test_trade_count_no_trades():
    """Hic islem olmayan durumlar dogru hesaplanmalidir."""
    assert trade_count(pd.Series([0, 0, 0])) == 0
    assert trade_count(pd.Series([1, 1, 1])) == 1


def test_hit_rate_hand_calculated():
    """Gorev tanimindaki elle hesaplanmis hit_rate ornegi dogrulanmalidir."""
    # close = [100, 110, 110, 90, 100, 105]
    # positions = [0, 1, 1, 0, 1, 0]
    # 1. Islem: Giris t=1 (110), Cikis t=3 (90) -> Getiri: -18.18% (Zarar)
    # 2. Islem: Giris t=4 (100), Cikis t=5 (105) -> Getiri: +5% (Kar)
    # Toplam 2 islem, 1 kar -> Hit Rate = 0.5
    close = pd.Series([100, 110, 110, 90, 100, 105])
    positions = pd.Series([0, 1, 1, 0, 1, 0])
    assert pytest.approx(hit_rate(close, positions)) == 0.5


def test_hit_rate_no_trades_returns_nan():
    """Hic islem yapilmayan serilerde hit_rate NaN dondurmelidir."""
    close = pd.Series([100, 110, 120])
    positions = pd.Series([0, 0, 0])
    assert np.isnan(hit_rate(close, positions))


def test_hit_rate_open_trade_at_end():
    """Seri sonunda acik kalan islem de son fiyatla degerlendirilip hesaba katilmalidir."""
    # Giris t=1 (100), Seri sonu t=2 (110) -> Kar
    close = pd.Series([90, 100, 110])
    positions = pd.Series([0, 1, 1])
    assert hit_rate(close, positions) == 1.0


def test_hit_rate_all_loss():
    """Butun islemler zararliysa (getiri <= 0) hit_rate 0.0 olmalidir."""
    close = pd.Series([100, 90, 100, 80])
    positions = pd.Series([1, 0, 1, 0])
    # 1. Giris 100, Cikis 90 (Zarar)
    # 2. Giris 100, Cikis 80 (Zarar)
    assert hit_rate(close, positions) == 0.0


def test_hit_rate_all_profit():
    """Butun islemler karliysa hit_rate 1.0 olmalidir."""
    close = pd.Series([100, 110, 100, 110])
    positions = pd.Series([1, 0, 1, 0])
    # 1. Giris 100, Cikis 110 (Kar)
    # 2. Giris 100, Cikis 110 (Kar)
    assert hit_rate(close, positions) == 1.0
