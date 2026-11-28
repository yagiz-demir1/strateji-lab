"""Toplu çalıştırma (G-027) için testler: varlık × strateji kombinasyonları veritabanına yazılır."""

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


def _wave_source(ticker, start, end):
    """Ağa çıkmayan sahte kaynak: 300 iş günlük dalgalı fiyat; BAD.IS için hata verir."""
    import numpy as np

    if ticker == "BAD.IS":
        raise ValueError("Veri alınamadı")
    dates = pd.bdate_range(start, periods=300)
    close = 100 + 10 * np.sin(np.arange(300) / 8.0) + np.arange(300) * 0.05
    return pd.DataFrame(
        {"open": close, "high": close, "low": close, "close": close, "volume": 1000}, index=dates
    )


def test_run_batch_writes_rows_to_database(tmp_path):
    """2 × 2 çalıştırma veritabanında 4 satır; hatalı üçüncü varlıkla toplam 6 satır, 2'sinde error dolu."""
    from stratlab.results.db import load_runs

    db_path = str(tmp_path / "results" / "sonuclar.sqlite")
    common = dict(strategies=["ma_crossover", "macd"], start="2023-01-01", end="2024-03-01",
                  cost_bps=10.0, db_path=db_path, source=_wave_source, cache_dir=str(tmp_path / "cache"))
    run_batch(tickers=["THYAO.IS", "AAPL"], **common)
    assert len(load_runs(db_path)) == 4

    run_batch(tickers=["BAD.IS"], **common)
    rows = load_runs(db_path)
    assert len(rows) == 6
    assert rows["error"].notna().sum() == 2
    assert set(rows.loc[rows["error"].notna(), "ticker"]) == {"BAD.IS"}


def test_run_batch_benchmark_metrics_come_from_benchmark_equity(tmp_path):
    """Al-tut Sharpe ve en büyük düşüşü stratejinin değil, al-tut eğrisinin değerleridir."""
    from stratlab.metrics import max_drawdown, sharpe, total_return
    from stratlab.ui.logic import run_selected

    rows = run_batch(tickers=["AAPL"], strategies=["macd"], start="2023-01-01", end="2024-03-01",
                     cost_bps=10.0, db_path=str(tmp_path / "r.sqlite"), source=_wave_source,
                     cache_dir=str(tmp_path / "cache"))
    row = rows.iloc[0]
    res = run_selected("AAPL", "macd", "2023-01-01", "2024-03-01", 10.0,
                       source=_wave_source, cache_dir=str(tmp_path / "cache"))
    assert row["bench_total_return"] == pytest.approx(total_return(res["bench_equity"]))
    assert row["bench_sharpe"] == pytest.approx(sharpe(res["bench_equity"]))
    assert row["bench_max_drawdown"] == pytest.approx(max_drawdown(res["bench_equity"]))
    assert row["bench_sharpe"] != pytest.approx(row["sharpe"])
    assert row["grp"] == "nasdaq"
    assert row["n_days"] == len(res["strat_equity"])


def test_batch_cli_with_all_strategies(tmp_path):
    """Komut satırı 'all' stratejileriyle çalışır, 0 döndürür ve her strateji için bir satır yazar."""
    from stratlab.batch import main
    from stratlab.results.db import load_runs

    db_path = str(tmp_path / "results" / "sonuclar.sqlite")
    code = main(["--tickers", "AAPL", "--strategies", "all", "--start", "2023-01-01", "--end", "2024-03-01",
                 "--db", db_path, "--cache-dir", str(tmp_path / "cache")], source=_wave_source)
    assert code == 0
    rows = load_runs(db_path)
    assert sorted(rows["strategy"]) == sorted(STRATEGIES)
    assert rows["error"].isna().all()
