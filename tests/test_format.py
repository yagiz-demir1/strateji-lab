"""Sayı ve yüzde formatlama fonksiyonları için testler (G-024)."""

import numpy as np
import pytest
from stratlab.reports.format import fmt_pct, fmt_num

def test_fmt_pct_basic():
    """Pozitif yüzdeyi Türkçe formatta yazmalıdır."""
    assert fmt_pct(0.2112) == "%21,12"

def test_fmt_pct_negative():
    """Negatif yüzdeyi Türkçe formatta (işaret başta) yazmalıdır."""
    assert fmt_pct(-0.25) == "-%25,00"

def test_fmt_pct_negative_zero_suppression():
    """Eksi sıfır durumunda eksi işareti gösterilmemelidir."""
    # -0.00001 * 100 = -0.001 -> yuvarlanınca 0.00
    assert fmt_pct(-0.00001) == "%0,00"

def test_fmt_pct_thousands_separator():
    """Yüzde değerinde binlik ayırıcı (nokta) kullanılmalıdır."""
    # 12.345 * 100 = 1234.5 -> %1.234,50
    assert fmt_pct(12.345) == "%1.234,50"

def test_fmt_pct_nan():
    """NaN değeri için tire (–) döndürmelidir."""
    assert fmt_pct(np.nan) == "–"

def test_fmt_num_basic():
    """Sayıları Türkçe formatta (ondalık virgül) yazmalıdır."""
    assert fmt_num(1.234) == "1,23"

def test_fmt_num_negative_zero():
    """Sayısal değerlerde eksi sıfır gösterilmemelidir."""
    assert fmt_num(-0.004) == "0,00"

def test_fmt_num_nan():
    """NaN sayısal değeri için tire (–) döndürmelidir."""
    assert fmt_num(np.nan) == "–"

def test_fmt_pct_isabet_orani_check():
    """İsabet oranı gibi değerler için %50,00 gibi format üretmelidir."""
    assert fmt_pct(0.5) == "%50,00"
