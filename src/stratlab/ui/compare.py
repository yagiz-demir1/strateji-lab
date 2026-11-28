'''Karşılaştırma sayfası için arka plan veri işleme ve özet fonksiyonları (G-028).'''

import pandas as pd

MIN_TRADES = 30


def comparison_frame(
    runs: pd.DataFrame,
    groups: list[str] | None = None,
    strategies: list[str] | None = None,
) -> pd.DataFrame:
    """Veritabanından gelen runs DataFrame'ini filtreler ve karşılaştırma tablosuna dönüştürür."""
    if runs.empty:
        return pd.DataFrame(
            columns=[
                "Grup",
                "Varlık",
                "Strateji",
                "Strateji getirisi",
                "Al-tut getirisi",
                "Getiri farkı",
                "Sharpe",
                "Al-tut Sharpe",
                "Sharpe farkı",
                "En büyük düşüş",
                "İşlem",
                "Yeterli işlem",
            ]
        )

    # Hatalı satırları ele
    df = runs[runs["error"].isna() | (runs["error"] == "")].copy()

    # Toplu çalıştırma aynı veritabanına tekrar yapılırsa aynı kombinasyon birden çok kez bulunur;
    # her (varlık, strateji, dönem) için en son kayıt (en büyük id) kullanılır.
    if "id" in df.columns:
        df = df.sort_values("id")
    key = [col for col in ("ticker", "strategy", "period") if col in df.columns]
    df = df.drop_duplicates(subset=key, keep="last")
    if df.empty:
        return pd.DataFrame()

    if groups:
        df = df[df["grp"].isin(groups)]
    if strategies:
        df = df[df["strategy"].isin(strategies)]

    if df.empty:
        return pd.DataFrame()

    records = []
    for _, row in df.iterrows():
        t_ret = row.get("total_return", 0.0)
        b_ret = row.get("bench_total_return", 0.0)
        ret_diff = (t_ret - b_ret) if (pd.notna(t_ret) and pd.notna(b_ret)) else float("nan")

        sh = row.get("sharpe", 0.0)
        b_sh = row.get("bench_sharpe", 0.0)
        sh_diff = (sh - b_sh) if (pd.notna(sh) and pd.notna(b_sh)) else float("nan")

        trades = row.get("trades", 0)
        if pd.isna(trades):
            trades = 0
        trades = int(trades)

        sufficient = bool(trades >= MIN_TRADES)

        records.append({
            "Grup": row.get("grp"),
            "Varlık": row.get("ticker"),
            "Strateji": row.get("strategy"),
            "Strateji getirisi": t_ret,
            "Al-tut getirisi": b_ret,
            "Getiri farkı": ret_diff,
            "Sharpe": sh,
            "Al-tut Sharpe": b_sh,
            "Sharpe farkı": sh_diff,
            "En büyük düşüş": row.get("max_drawdown", 0.0),
            "İşlem": trades,
            "Yeterli işlem": sufficient,
        })

    res_df = pd.DataFrame(records)

    # Sharpe farkına göre büyükten küçüğe sırala
    if "Sharpe farkı" in res_df.columns:
        res_df = res_df.sort_values(by="Sharpe farkı", ascending=False).reset_index(drop=True)

    return res_df


def beat_count(frame: pd.DataFrame) -> tuple[int, int]:
    """Sharpe'ı al-tut'tan büyük olan satır sayısını ve toplam hatasız satır sayısını döndürür."""
    if frame.empty:
        return (0, 0)
    beaten = int((frame["Sharpe"] > frame["Al-tut Sharpe"]).sum())
    return (beaten, len(frame))


def sharpe_diff_pivot(frame: pd.DataFrame) -> pd.DataFrame:
    """Varlık x Strateji Sharpe farkı pivot tablosunu döndürür."""
    if frame.empty:
        return pd.DataFrame()
    pivot = frame.pivot(index="Varlık", columns="Strateji", values="Sharpe farkı")
    return pivot
