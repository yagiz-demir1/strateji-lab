"""Veri temizliği ve hatalı veri ayıklama işlemleri (G-023)."""

import pandas as pd


def clean_prices(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Kapanış fiyatı NaN veya pozitif olmayan (sıfır/negatif) satırları temizler.

    Atılan satırların nedenlerini içeren Türkçe bir not listesi döndürür.
    """
    if df.empty:
        return df, []

    notes = []
    
    # 1. Kapanış fiyatı boş olanlar
    nan_mask = df["close"].isna()
    nan_count = int(nan_mask.sum())
    if nan_count > 0:
        notes.append(f"{nan_count} gün atıldı: kapanış boş")

    # 2. Kapanış fiyatı sıfır veya negatif olanlar (NaN olmayanlar arasından)
    invalid_val_mask = (df["close"] <= 0) & (~nan_mask)
    invalid_count = int(invalid_val_mask.sum())
    if invalid_count > 0:
        if invalid_count == 1:
            # Tek gün varsa tarih belirtilir (örnek: "1 gün atıldı: kapanış ≤ 0 (2020-04-20)")
            bad_date = df.index[invalid_val_mask][0].strftime("%Y-%m-%d")
            notes.append(f"1 gün atıldı: kapanış ≤ 0 ({bad_date})")
        else:
            notes.append(f"{invalid_count} gün atıldı: kapanış ≤ 0")

    cleaned_df = df[~(nan_mask | invalid_val_mask)].copy()
    
    return cleaned_df, notes
