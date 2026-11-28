'''Streamlit çok sayfalı karşılaştırma sayfası (G-028).'''

import pandas as pd
import streamlit as st

from stratlab.results.db import load_runs
from stratlab.ui.compare import comparison_frame, beat_count, sharpe_diff_pivot
from stratlab.reports.format import fmt_pct, fmt_num
from stratlab.strategies import STRATEGIES
from stratlab.data.universe import UNIVERSE

st.set_page_config(page_title="Strateji Karşılaştırması", layout="wide")

st.title("Strateji Karşılaştırma Sayfası")
st.write("Toplu backtest sonuçlarını inceleyin ve al-tut ile karşılaştırın.")

st.sidebar.header("Filtreler")

db_path = st.sidebar.text_input("Veritabanı Yolu", value="results/sonuclar.sqlite", key="db_path_input")

try:
    runs_df = load_runs(db_path)
except FileNotFoundError:
    runs_df = pd.DataFrame()
except Exception as err:  # bozuk dosya gibi beklenmeyen hatalar gizlenmez
    st.error(f"Veritabanı okunamadı: {err}")
    st.stop()

if runs_df.empty:
    st.warning(
        f"Önce toplu çalıştırma yapın: python -m stratlab.batch --db {db_path} ..."
    )
else:
    # Grup and Strateji çoklu seçim filtreleri
    available_groups = sorted(runs_df["grp"].dropna().unique().tolist())
    selected_groups = st.sidebar.multiselect("Gruplar", available_groups, default=available_groups, key="groups_ms")

    available_strategies = sorted(runs_df["strategy"].dropna().unique().tolist())
    selected_strategies = st.sidebar.multiselect("Stratejiler", available_strategies, default=available_strategies, key="strats_ms")

    frame = comparison_frame(runs_df, groups=selected_groups, strategies=selected_strategies)

    if frame.empty:
        st.info(
            "Seçilen filtrelerde gösterilecek sonuç bulunamadı. Lütfen filtreleri kontrol edin veya yeni bir toplu çalıştırma yapın."
        )
    else:
        # Özet satırı
        beaten, total = beat_count(frame)
        st.subheader(f"Al-tut'u Sharpe'ta geçen: {beaten} / {total}")

        # Karşılaştırma Tablosu Gösterimi
        st.subheader("Detaylı Karşılaştırma Tablosu")
        
        display_df = frame.copy()
        display_df["Strateji getirisi"] = display_df["Strateji getirisi"].apply(fmt_pct)
        display_df["Al-tut getirisi"] = display_df["Al-tut getirisi"].apply(fmt_pct)
        display_df["Getiri farkı"] = display_df["Getiri farkı"].apply(fmt_pct)
        display_df["Sharpe"] = display_df["Sharpe"].apply(fmt_num)
        display_df["Al-tut Sharpe"] = display_df["Al-tut Sharpe"].apply(fmt_num)
        display_df["Sharpe farkı"]  = display_df["Sharpe farkı"].apply(fmt_num)
        display_df["En büyük düşüş"] = display_df["En büyük düşüş"].apply(fmt_pct)

        st.dataframe(display_df, use_container_width=True)

        # Sharpe farkı pivot tablosu
        st.subheader("Sharpe Farkı Matrisi (Varlık × Strateji)")
        pivot = sharpe_diff_pivot(frame)
        if not pivot.empty:
            formatted_pivot = pivot.map(fmt_num)
            st.dataframe(formatted_pivot, use_container_width=True)
