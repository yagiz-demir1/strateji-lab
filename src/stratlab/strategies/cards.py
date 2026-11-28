"""Strateji kartlari ve bilgi siniflari (G-029)."""

from dataclasses import dataclass


@dataclass
class StrategyCard:
    """Strateji tanim karti."""
    name: str
    title: str
    source: str
    hypothesis: str
    rules: list[str]
    params: dict
    added: str


CARDS = {
    "ma_crossover": StrategyCard(
        name="ma_crossover",
        title="Hareketli Ortalama Kesişimi",
        source="Brock, Lakonishok ve LeBaron (1992), 'Simple Technical Trading Rules and the Stochastic Properties of Stock Returns'",
        hypothesis="Kısa vadeli hareketli ortalama uzun vadiyi yukarı kestiğinde fiyat momentum kazanır ve yükseliş trendi başlar.",
        rules=[
            "Kısa SMA, uzun SMA'nın üstündeyse pozisyon 1 (alım).",
            "Kısa SMA, uzun SMA'nın altındaysa veya eşitse pozisyon 0 (nakit).",
        ],
        params={"fast": 50, "slow": 200},
        added="2026-11-28",
    ),
    "rsi_reversion": StrategyCard(
        name="rsi_reversion",
        title="RSI Ortalamaya Dönüş",
        source="J. Welles Wilder (1978), 'New Concepts in Technical Trading Systems'",
        hypothesis="Aşırı satım bölgesine inen fiyatlar ortalamaya döner; aşırı alım bölgesine çıkanlar düşer.",
        rules=[
            "RSI düşük eşiğin altına (30) inince alım yapılır (1).",
            "RSI yüksek eşiğin üstüne (70) çıkınca nakte geçilir (0).",
            "Arada önceki pozisyon korunur.",
        ],
        params={"window": 14, "low": 30.0, "high": 70.0},
        added="2026-11-28",
    ),
    "momentum_12_1": StrategyCard(
        name="momentum_12_1",
        title="12-1 Momentum",
        source="Moskowitz, Ooi ve Pedersen (2012), 'Time Series Momentum'",
        hypothesis="Geçmişte kazanan varlıklar yakın gelecekte de kazanmaya devam eder.",
        rules=[
            "Son bir yılın (252 gün, son 21 gün hariç) getirisi pozitifse alımda kalınır (1).",
            "Getiri negatifse nakte geçilir (0).",
        ],
        params={"lookback": 252, "skip": 21},
        added="2026-11-28",
    ),
    "bollinger_breakout": StrategyCard(
        name="bollinger_breakout",
        title="Bollinger Bant Kırılımı",
        source="John Bollinger (2001), 'Bollinger on Bollinger Bands'",
        hypothesis="Fiyat üst bandı aşarak volatilite kırılımı yaptığında yukarı yönlü hareket devam eder.",
        rules=[
            "Fiyat üst bandın üstüne çıkınca pozisyon 1 olur.",
            "Fiyat orta bandın altına inince pozisyon 0 olur.",
        ],
        params={"window": 20, "k": 2.0},
        added="2026-11-28",
    ),
    "macd": StrategyCard(
        name="macd",
        title="MACD Sinyal Kesişimi",
        source="Gerald Appel (1970'lerin sonu)",
        hypothesis="MACD çizgisinin sinyal çizgisini yukarı kesmesi trend dönüşünü ve alım fırsatını gösterir.",
        rules=[
            "MACD çizgisi sinyal çizgisinin üstündeyse pozisyon 1 (alım).",
            "MACD çizgisi sinyal çizgisinin altındaysa pozisyon 0 (nakit).",
        ],
        params={"fast": 12, "slow": 26, "signal": 9},
        added="2026-11-28",
    ),
}
