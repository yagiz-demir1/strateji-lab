"""Çekirdek varlık evreni tanımları ve yardımcı fonksiyonlar."""

UNIVERSE = {
    "bist": ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "GARAN.IS", "BIMAS.IS"],
    "dax": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "MBG.DE"],
    "nasdaq": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"],
    "endeksler": ["XU100.IS", "^GDAXI", "^NDX"],
    "emtia": ["GC=F", "CL=F", "BZ=F"],
}


def all_tickers() -> list[str]:
    """Evrendeki bütün ticker'ların tekrarsız listesini döndürür."""
    tickers = []
    for group_tickers in UNIVERSE.values():
        for ticker in group_tickers:
            if ticker not in tickers:
                tickers.append(ticker)
    return tickers


def group_of(ticker: str) -> str:
    """Verilen ticker'ın hangi gruba ait olduğunu döndürür.

    Bilinmeyen ticker için KeyError fırlatır.
    """
    for group, tickers in UNIVERSE.items():
        if ticker in tickers:
            return group
    raise KeyError(f"Ticker '{ticker}' evrende bulunamadı.")
