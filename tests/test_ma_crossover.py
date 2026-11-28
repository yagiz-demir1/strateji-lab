"""Hareketli ortalama kesişimi stratejisi (G-007) testleri.

Kısa hareketli ortalamanın uzun hareketli ortalamanın üstünde olduğu durumlarda
alımda kalma (1) pozisyonunu ve kural sınırlarını test eder.
"""

import numpy as np
import pandas as pd
import pytest

from stratlab.strategies.ma_crossover import ma_crossover_positions
from tests.helpers import load_fixture


def test_ma_crossover_returns_series_with_zero_or_one():
    """ma_crossover_positions fonksiyonu sadece 0 veya 1 değerlerini içeren bir Series döndürmelidir."""
    close = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0])
    positions = ma_crossover_positions(close, fast=2, slow=4)
    
    assert isinstance(positions, pd.Series)
    assert len(positions) == len(close)
    assert set(positions.unique()).issubset({0, 1})


def test_ma_crossover_fast_greater_or_equal_slow_raises_value_error():
    """fast >= slow durumlarında ValueError fırlatılmalıdır."""
    close = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    
    with pytest.raises(ValueError):
        ma_crossover_positions(close, fast=5, slow=5)
        
    with pytest.raises(ValueError):
        ma_crossover_positions(close, fast=6, slow=5)


def test_ma_crossover_initial_days_are_zero():
    """Ortalamaların henüz hesaplanamadığı ilk günler pozisyon 0 olmalıdır."""
    close = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    # slow=4 için ilk 3 günde (0, 1, 2. indisler) slow SMA hesaplanamaz (NaN)
    positions = ma_crossover_positions(close, fast=2, slow=4)
    assert (positions.iloc[:3] == 0).all()


def test_ma_crossover_logic_above_and_below():
    """Kısa ortalama uzun ortalamanın üstündeyken 1, altındayken veya eşitken 0 olmalıdır."""
    # İlk 3 gün yükselip sonra hızla düşen bir seri kuralım
    # t=0..2: yükseliş, t=3..5: sert düşüş
    close = pd.Series([10.0, 20.0, 30.0, 10.0, 5.0, 2.0])
    positions = ma_crossover_positions(close, fast=2, slow=3)
    
    # slow=3 için ilk 2 gün (0, 1) 0 olmalı
    assert positions.iloc[0] == 0
    assert positions.iloc[1] == 0
    # t=2: fast(2)=(20+30)/2=25, slow(3)=(10+20+30)/3=20 -> fast > slow -> 1
    assert positions.iloc[2] == 1
    # t=3: close=[10, 20, 30, 10] -> fast=(30+10)/2=20, slow=(20+30+10)/3=20 -> fast not > slow -> 0
    assert positions.iloc[3] == 0
    # t=4: close=5 -> fast=(10+5)/2=7.5, slow=(30+10+5)/3=15 -> fast < slow -> 0
    assert positions.iloc[4] == 0


def test_ma_crossover_with_yukselen_fixture():
    """load_fixture('yukselen') ile fast=5, slow=20 için 20. günden (indis 19) sonra bütün pozisyonlar 1 olmalıdır."""
    df = load_fixture("yukselen")
    positions = ma_crossover_positions(df["close"], fast=5, slow=20)
    
    # İlk slow-1 (19 gün) pozisyon 0 olmalı
    assert (positions.iloc[:19] == 0).all()
    # 20. günden itibaren (indis >= 19) sürekli yükselen seride fast > slow olacağından hepsi 1 olmalı
    assert (positions.iloc[19:] == 1).all()


def test_ma_crossover_example_case():
    """Örnek girdi kontrolü: sürekli yükselen seri, fast=2, slow=4 -> 4. günden (indis 3) itibaren 1."""
    close = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0])
    positions = ma_crossover_positions(close, fast=2, slow=4)
    
    # İlk 3 gün (indis 0, 1, 2) 0
    assert (positions.iloc[:3] == 0).all()
    # 4. günden itibaren (indis 3, 4, 5) 1
    assert (positions.iloc[3:] == 1).all()
