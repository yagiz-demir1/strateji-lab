import pandas as pd
import pytest
from stratlab.batch import run_batch
from stratlab.strategies import STRATEGY_PARAMS, STRATEGIES
from stratlab.strategies.ma_crossover import ma_crossover_positions


def test_strategy_params_match_wrapped():
    """Her strateji için STRATEGY_PARAMS ile sarmalayıcı çağrısı aynı sonucu vermelidir."""
    close = pd.Series([100.0 + i for i in range(300)])
    
    for name, wrapper in STRATEGIES.items():
        params = STRATEGY_PARAMS[name]
        # Doğrudan fonksiyon ve sarmalayıcı çağrısı karşılaştırılır
        if name == "ma_crossover":
            expected = ma_crossover_positions(close, **params)
        elif name == "rsi_reversion":
            from stratlab.strategies.rsi_reversion import rsi_reversion_positions
            expected = rsi_reversion_positions(close, **params)
        elif name == "momentum_12_1":
            from stratlab.strategies.momentum import momentum_positions
            expected = momentum_positions(close, **params)
        elif name == "bollinger_breakout":
            from stratlab.strategies.bollinger_breakout import bollinger_breakout_positions
            expected = bollinger_breakout_positions(close, **params)
        elif name == "macd":
            from stratlab.strategies.macd_strategy import macd_positions
            expected = macd_positions(close, **params)
        else:
            pytest.fail(f"Bilinmeyen strateji: {name}")
            
        result = wrapper(close)
        pd.testing.assert_series_equal(result, expected)


def test_run_batch_saves_results_and_handles_errors(tmp_path):
    """2 varlık x 2 strateji ile 4 satır, hata veren 3. varlık ile 6 satır kaydedilmelidir."""
    db_path = str(tmp_path / "results.sqlite")
    tickers = ["THYAO.IS", "AAPL", "BAD.IS"]
    strategies = ["ma_crossover", "rsi_reversion"]
    
    def mock_source(ticker, start, end):
        if ticker == "BAD.IS":
            raise ValueError("Veri alınamadı")
        dates = pd.date_range(start, periods=60)
        close = pd.Series([100.0 + i for i in range(60)], index=dates)
        return pd.DataFrame({
            "open": close,
            "high": close,
            "low": close,
            "close": close,
            "volume": [1000] * 60
        }, index=dates)

    df_runs = run_batch(
        tickers=tickers,
        strategies=strategies,
        start="2024-01-01",
        end="2024-03-01",
        cost_bps=10.0,
        db_path=db_path,
        source=mock_source,
        cache_dir=str(tmp_path / "cache")
    )

    assert isinstance(df_runs, pd.DataFrame)
    # 2 geçerli varlık * 2 strateji = 4 başarılı, 1 hatalı varlık * 2 strateji = 2 hatalı -> toplam 6 satır
    assert len(df_runs) == 6
    
    error_rows = df_runs[df_runs["error"].notna() & (df_runs["error"] != "")]
    assert len(error_rows) == 2
