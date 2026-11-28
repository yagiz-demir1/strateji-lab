"""Strateji Laboratuvarı Streamlit web arayüzü (G-019)."""

import datetime
import pandas as pd
import streamlit as st

from stratlab.data.universe import all_tickers
from stratlab.strategies import STRATEGIES
from stratlab.ui.logic import run_selected

st.set_page_config(page_title="Strateji Laboratuvarı", layout="wide")

st.title("Strateji Laboratuvarı")
st.write("Yatırım stratejilerini test edin ve al-tut ile karşılaştırın.")

st.sidebar.header("Ayarlar")

# Varlık seçimi
all_t = all_tickers()
selected_ticker = st.sidebar.selectbox("Varlık (Ticker)", all_t, key="ticker_select")

# Strateji seçimi
selected_strategy = st.sidebar.selectbox("Strateji", list(STRATEGIES.keys()), key="strategy_select")

# Tarih aralığı
def_start = datetime.date(2023, 1, 1)
def_end = datetime.date.today()

start_date = st.sidebar.date_input("Başlangıç Tarihi", def_start, key="start_date")
end_date = st.sidebar.date_input("Bitiş Tarihi", def_end, key="end_date")

cost_bps = st.sidebar.number_input(
    "İşlem Maliyeti (baz puan)", min_value=0.0, value=10.0, step=1.0, key="cost_bps"
)

run_clicked = st.sidebar.button("Çalıştır", key="run_button")

if run_clicked:
    try:
        with st.spinner("Backtest çalıştırılıyor..."):
            result = run_selected(
                ticker=selected_ticker,
                strategy=selected_strategy,
                start=str(start_date),
                end=str(end_date),
                cost_bps=float(cost_bps),
            )

        st.subheader(f"Sonuçlar: {selected_ticker} – {selected_strategy}")

        # Sermaye Eğrisi Grafiği
        chart_df = pd.DataFrame(
            {
                "Strateji": result["strat_equity"],
                "Al-tut": result["bench_equity"],
            }
        )
        st.line_chart(chart_df)

        # Metrik Tablosu
        st.subheader("Performans Metrikleri")
        metrics_dict = result["metrics"]
        
        rows = []
        for k, v in metrics_dict.items():
            if pd.isna(v):
                val_str = "N/A"
            elif isinstance(v, float) and ("Getiri" in k or "Düşüş" in k):
                sign = "-" if v < 0 else ""
                val_str = f"{sign}%{abs(v * 100):.2f}"
            elif isinstance(v, float) and "İsabet" in k:
                val_str = f"%{v * 100:.2f}"
            elif isinstance(v, float):
                val_str = f"{v:.2f}"
            else:
                val_str = str(v)
            rows.append({"Metrik": k, "Değer": val_str})

        st.table(pd.DataFrame(rows))

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
else:
    st.info("Kenar çubuğundan ayarları seçip 'Çalıştır' butonuna basın.")
