"""SQLite veritabanı üzerinde backtest sonuçlarını saklama ve okuma işlemleri (G-026)."""

from datetime import datetime, timezone
import json
import sqlite3
import pandas as pd


def _get_connection(db_path: str) -> sqlite3.Connection:
    """SQLite bağlantısı açar ve gerekirse runs tablosunu oluşturur."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            ticker TEXT,
            grp TEXT,
            strategy TEXT,
            params TEXT,
            start TEXT,
            end TEXT,
            cost_bps REAL,
            period TEXT,
            total_return REAL,
            annual_return REAL,
            annual_volatility REAL,
            sharpe REAL,
            max_drawdown REAL,
            trades INTEGER,
            hit_rate REAL,
            bench_total_return REAL,
            bench_sharpe REAL,
            bench_max_drawdown REAL,
            n_days INTEGER,
            notes TEXT,
            error TEXT
        )
        """
    )
    conn.commit()
    return conn


def save_run(db_path: str, run: dict) -> int:
    """Backtest sonuç sözlüğünü SQLite veritabanına kaydeder ve yeni kaydın id'sini döndürür."""
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    created_at = run.get("created_at")
    if not created_at:
        created_at = datetime.now(timezone.utc).isoformat()

    params = run.get("params", {})
    if isinstance(params, dict):
        params_str = json.dumps(params, ensure_ascii=False)
    else:
        params_str = str(params)

    columns = [
        "created_at",
        "ticker",
        "grp",
        "strategy",
        "params",
        "start",
        "end",
        "cost_bps",
        "period",
        "total_return",
        "annual_return",
        "annual_volatility",
        "sharpe",
        "max_drawdown",
        "trades",
        "hit_rate",
        "bench_total_return",
        "bench_sharpe",
        "bench_max_drawdown",
        "n_days",
        "notes",
        "error",
    ]

    values = [
        created_at,
        run.get("ticker"),
        run.get(
            "grp"
        ),  # G-026 gereği 'grp' alanı sözlükte olmasa bile None olarak kaydedilir
        run.get("strategy"),
        params_str,
        run.get("start"),
        run.get("end"),
        run.get("cost_bps"),
        run.get("period"),
        run.get("total_return"),
        run.get("annual_return"),
        run.get("annual_volatility"),
        run.get("sharpe"),
        run.get("max_drawdown"),
        run.get("trades"),
        run.get("hit_rate"),
        run.get("bench_total_return"),
        run.get("bench_sharpe"),
        run.get("bench_max_drawdown"),
        run.get("n_days"),
        run.get("notes"),
        run.get("error"),
    ]

    placeholders = ", ".join(["?"] * len(columns))
    cols_str = ", ".join(columns)

    cursor.execute(
        f"INSERT INTO runs ({cols_str}) VALUES ({placeholders})",
        values,
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def load_runs(db_path: str) -> pd.DataFrame:
    """Veritabanındaki bütün runs kayıtlarını pandas DataFrame olarak döndürür."""
    conn = _get_connection(db_path)
    df = pd.read_sql_query("SELECT * FROM runs", conn)
    conn.close()
    return df
