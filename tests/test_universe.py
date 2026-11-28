"""Çekirdek varlık evreni (G-009) için testler."""
import pytest
from stratlab.data.universe import UNIVERSE, all_tickers, group_of

def test_universe_groups_and_sizes():
    """Varlık evrenindeki grupların varlığını ve boyutlarını kontrol eder."""
    assert "bist" in UNIVERSE
    assert len(UNIVERSE["bist"]) == 5
    assert "dax" in UNIVERSE
    assert len(UNIVERSE["dax"]) == 5
    assert "nasdaq" in UNIVERSE
    assert len(UNIVERSE["nasdaq"]) == 5
    assert "endeksler" in UNIVERSE
    assert len(UNIVERSE["endeksler"]) == 3
    assert "emtia" in UNIVERSE
    assert len(UNIVERSE["emtia"]) == 3

def test_bist_tickers_have_is_suffix():
    """BIST hisselerinin .IS uzantısı olmalıdır."""
    for ticker in UNIVERSE["bist"]:
        assert ticker.endswith(".IS")

def test_dax_tickers_have_de_suffix():
    """DAX hisselerinin .DE uzantısı olmalıdır."""
    for ticker in UNIVERSE["dax"]:
        assert ticker.endswith(".DE")

def test_all_tickers_is_unique_list():
    """all_tickers() tekrarsız ve tam listedir."""
    tickers = all_tickers()
    assert len(tickers) == 21
    assert len(set(tickers)) == 21

def test_group_of_returns_correct_name():
    """group_of fonksiyonu doğru grup adını döndürmelidir."""
    assert group_of("THYAO.IS") == "bist"
    assert group_of("SAP.DE") == "dax"
    assert group_of("AAPL") == "nasdaq"
    assert group_of("XU100.IS") == "endeksler"
    assert group_of("GC=F") == "emtia"

def test_group_of_raises_key_error_for_unknown_ticker():
    """Bilinmeyen bir ticker için group_of KeyError fırlatmalıdır."""
    with pytest.raises(KeyError):
        group_of("GEÇERSİZ")
