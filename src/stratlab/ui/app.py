"""Strateji Laboratuvarı Streamlit web arayüzü (G-019, G-025, G-029)."""

import datetime
import pandas as pd
import streamlit as st

from stratlab.data.universe import all_tickers
from stratlab.strategies import STRATEGIES
from stratlab.strategies.cards import CARDS
from stratlab.ui.logic import run_selected
from stratlab.reports.format import fmt_pct, fmt_num

st.set_page_config(page_title="Strateji Laboratuvarı", layout="wide")

st.title("Strateji Laboratuvarı")
st.write("Yatırım stratejilerini test edin ve al-tut ile karşılaştırın.")

st.sidebar.header("Ayarlar")

# Varlık seçimi
all_t = all_tickers()
selected_ticker = st.sidebar.selectbox("Varlık (Ticker)", all_t, key="ticker_select")

# Strateji seçimi
selected_strategy = st.sidebar.selectbox("Strateji", list(STRATEGIES.keys()), key="strategy_select")

# Strateji Kartı Bilgileri (G-029)
card = CARDS.get(selected_strategy)
if card:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Strateji Kartı")
    st.sidebar.markdown(f"**Başlık:** {card.title}")
    st.sidebar.markdown(f"**Kaynak:** {card.source}")
    st.sidebar.markdown(f"**Hipotez:** {card.hypothesis}")
    rules_md = "\n".join([f"- {r}" for r in card.rules])
    st.sidebar.markdown(f"**Kurallar:**\n{rules_md}")
    st.sidebar.markdown(f"**Parametreler:** `{card.params}`")

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

        # Karşılaştırma Tablosu (G-025)
        st.subheader("Performans Karşılaştırması")
        comp_df = result["comparison"]

        # Tabloyu Türkçe formatta göster
        formatted_rows = []
        for idx, row in comp_df.iterrows():
            formatter = fmt_num if idx == "Sharpe Oranı" else fmt_pct
            formatted_rows.append(
                {
                    "Metrik": idx,
                    "Strateji": formatter(row["Strateji"]),
                    "Al-tut": formatter(row["Al-tut"]),
                    "Fark": formatter(row["Fark"]),
                }
            )

        st.table(pd.DataFrame(formatted_rows))

        # İşlem İstatistikleri (Tablonun altında)
        st.subheader("İşlem İstatistikleri")
        metrics_dict = result["metrics"]
        t_count = metrics_dict.get("İşlem Sayısı", 0)
        h_rate = metrics_dict.get("İsabet Oranı", float("nan"))
        h_rate_str = fmt_pct(h_rate)

        st.write(f"- **İşlem Sayısı:** {t_count}")
        st.write(f"- **İsabet Oranı:** {h_rate_str}")

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
else:
    st.info("Kenar çubuğundan ayarları seçip 'Çalıştır' butonuna basın.")
