"""Sayı ve yüzde değerlerini Türkçe biçimde formatlar (G-024)."""

import pandas as pd


def _base_format(val: float) -> str:
    """Binlik ayırıcı olarak nokta, ondalık ayırıcı olarak virgül kullanır."""
    # 1234.56 -> "1,234.56"
    formatted = "{:.2f}".format(val)
    # Ondalık noktayı virgüle çevir
    if "." in formatted:
        parts = formatted.split(".")
        # Binlik ayırıcıları ekle
        integer_part = "{:,}".format(int(parts[0])).replace(",", ".")
        return f"{integer_part},{parts[1]}"
    return "{:,}".format(int(formatted)).replace(",", ".")


def fmt_pct(val: float) -> str:
    """Yüzde değerini Türkçe formatta (örn. %21,12 veya -%25,00) döndürür."""
    if pd.isna(val):
        return "–"
    
    val_pct = round(val * 100, 2)
    # Eksi sıfır kontrolü (-0.00 -> 0.00)
    if abs(val_pct) < 0.005:
        val_pct = 0.0
        
    sign = "-" if val_pct < 0 else ""
    return f"{sign}%{_base_format(abs(val_pct))}"


def fmt_num(val: float) -> str:
    """Sayısal değeri Türkçe formatta (örn. 1,23) döndürür."""
    if pd.isna(val):
        return "–"
    
    val_round = round(val, 2)
    if abs(val_round) < 0.005:
        val_round = 0.0
        
    sign = "-" if val_round < 0 else ""
    formatted = _base_format(abs(val_round))
    return f"{sign}{formatted}" if sign else formatted
