"""Backtest sonuçlarının SQLite veritabanına kaydedilmesini ve yüklenmesini test eder (G-026)."""

import json
import sqlite3
import pandas as pd
import pytest
from datetime import datetime

# Not: Modül henüz yazılmadığı için bu importlar başlangıçta hata verecektir.
from stratlab.results.db import save_run, load_runs

def test_save_run_creates_database_and_table(tmp_path):
    """Veritabanı yoksa ilk kayıtla birlikte oluşmalı ve tablo şeması doğru olmalıdır."""
    db_path = str(tmp_path / "test.sqlite")
    run_data = {
        "ticker": "THYAO.IS",
        "grp": "bist",
        "strategy": "ma_crossover",
        "params": {"fast": 50, "slow": 200},
        "start": "2024-01-01",
        "end": "2024-12-31",
        "cost_bps": 10.0,
        "period": "gelistirme",
        "total_return": 0.25,
        "annual_return": 0.22,
        "annual_volatility": 0.15,
        "sharpe": 1.2,
        "max_drawdown": -0.10,
        "trades": 5,
        "hit_rate": 0.6,
        "bench_total_return": 0.15,
        "bench_sharpe": 0.8,
        "bench_max_drawdown": -0.12,
        "n_days": 252,
        "notes": "Test notu",
        "error": None
    }
    
    run_id = save_run(db_path, run_data)
    assert run_id == 1
    
    # SQLite şemasını doğrudan kontrol et
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='runs'")
    assert cursor.fetchone() is not None
    
    cursor.execute("PRAGMA table_info(runs)")
    columns = [row[1] for row in cursor.fetchall()]
    expected_cols = [
        "id", "created_at", "ticker", "grp", "strategy", "params", "start", "end", 
        "cost_bps", "period", "total_return", "annual_return", "annual_volatility", 
        "sharpe", "max_drawdown", "trades", "hit_rate", "bench_total_return", 
        "bench_sharpe", "bench_max_drawdown", "n_days", "notes", "error"
    ]
    for col in expected_cols:
        assert col in columns
    conn.close()

def test_load_runs_returns_all_data_correctly(tmp_path):
    """Kaydedilen veriler load_runs ile doğru tip ve değerlerle geri okunmalıdır."""
    db_path = str(tmp_path / "test.sqlite")
    
    run1 = {
        "ticker": "AAPL", "grp": "nasdaq", "strategy": "rsi_reversion",
        "params": {"window": 14, "low": 30}, "start": "2023-01-01", "end": "2023-06-01",
        "cost_bps": 5.0, "period": "gelistirme", "total_return": 0.1, "annual_return": 0.2,
        "annual_volatility": 0.1, "sharpe": 2.0, "max_drawdown": -0.05, "trades": 3,
        "hit_rate": 0.66, "bench_total_return": 0.05, "bench_sharpe": 1.0,
        "bench_max_drawdown": -0.08, "n_days": 120, "notes": "Not 1", "error": None
    }
    
    run2 = {
        "ticker": "BTC-USD", "grp": "kripto", "strategy": "momentum",
        "params": {"lookback": 10}, "start": "2023-06-01", "end": "2023-12-01",
        "cost_bps": 20.0, "period": "final", "total_return": 0.5, "annual_return": 1.2,
        "annual_volatility": 0.8, "sharpe": 1.5, "max_drawdown": -0.3, "trades": 10,
        "hit_rate": 0.5, "bench_total_return": 0.3, "bench_sharpe": 1.1,
        "bench_max_drawdown": -0.25, "n_days": 180, "notes": "Not 2", "error": None
    }
    
    id1 = save_run(db_path, run1)
    id2 = save_run(db_path, run2)
    
    assert id1 == 1
    assert id2 == 2
    
    df = load_runs(db_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    
    # Birinci kaydı kontrol et
    row1 = df[df["id"] == 1].iloc[0]
    assert row1["ticker"] == "AAPL"
    assert row1["period"] == "gelistirme"
    assert row1["sharpe"] == 2.0
    
    # JSON params kontrolü
    params_back = json.loads(row1["params"])
    assert params_back == {"window": 14, "low": 30}
    
    # created_at ISO formatında mı?
    try:
        datetime.fromisoformat(row1["created_at"])
    except (ValueError, TypeError):
        pytest.fail("created_at geçerli bir ISO formatında değil")

def test_save_and_load_run_with_error(tmp_path):
    """Hata durumunda metrikler boş (NaN/None) olsa bile kayıt başarılı olmalıdır."""
    db_path = str(tmp_path / "error.sqlite")
    error_run = {
        "ticker": "GARAN.IS",
        "grp": "bist",
        "strategy": "bollinger",
        "params": {"k": 2},
        "start": "2024-01-01",
        "end": "2024-01-05",
        "cost_bps": 10.0,
        "period": "gelistirme",
        "total_return": None, 
        "annual_return": float('nan'),
        "annual_volatility": None,
        "sharpe": None,
        "max_drawdown": None,
        "trades": None,
        "hit_rate": None,
        "bench_total_return": None,
        "bench_sharpe": None,
        "bench_max_drawdown": None,
        "n_days": 0,
        "notes": "",
        "error": "Veri yüklenemedi: 404"
    }
    
    save_run(db_path, error_run)
    df = load_runs(db_path)
    
    assert len(df) == 1
    assert df.iloc[0]["error"] == "Veri yüklenemedi: 404"
    assert pd.isna(df.iloc[0]["sharpe"])


def test_numpy_numbers_are_stored_as_numbers(tmp_path):
    """np.int64 / np.float64 değerleri bayt olarak değil sayı olarak saklanır (metrik fonksiyonları NumPy türü döndürebilir)."""
    import numpy as np

    db_path = str(tmp_path / "np.sqlite")
    save_run(db_path, {"ticker": "X", "trades": np.int64(7), "sharpe": np.float64(1.25), "n_days": np.int64(300)})
    row = load_runs(db_path).iloc[0]
    assert row["trades"] == 7
    assert row["n_days"] == 300
    assert row["sharpe"] == 1.25
    with sqlite3.connect(db_path) as conn:
        kind = conn.execute("SELECT typeof(trades) FROM runs").fetchone()[0]
    assert kind == "integer"


def test_save_run_creates_missing_folder(tmp_path):
    """Varsayılan yol gibi (results/sonuclar.sqlite) klasörü olmayan bir yola da kaydedilebilir."""
    db_path = tmp_path / "results" / "sonuclar.sqlite"
    assert save_run(str(db_path), {"ticker": "X"}) == 1
    assert db_path.exists()


def test_load_runs_missing_file_raises(tmp_path):
    """Olmayan veritabanı okunurken FileNotFoundError verilir ve boş dosya oluşturulmaz."""
    db_path = tmp_path / "yok.sqlite"
    with pytest.raises(FileNotFoundError):
        load_runs(str(db_path))
    assert not db_path.exists()
