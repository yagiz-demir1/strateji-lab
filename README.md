# Strateji Laboratuvarı

Yatırım stratejilerini toplayan, kaydeden ve geçmiş veride test eden bir araştırma sistemi.

## Özellikler (Faz 1)

- **Veri Katmanı:** yfinance entegrasyonu ve yerel CSV önbelleği.
- **Göstergeler:** SMA, EMA, RSI (Wilder), Bollinger Bantları, ATR, MACD.
- **Stratejiler:**
  - Hareketli Ortalama Kesişimi
  - RSI Ortalamaya Dönüş
  - 12-1 Momentum
  - Bollinger Bant Kırılımı
  - MACD Sinyal Kesişimi
- **Backtest Motoru:** İşlem maliyetleri (komisyon/spread) dahil, tek varlık simülasyonu.
- **Raporlama:** Al-tut (Buy & Hold) karşılaştırmalı Markdown raporu ve performans metrikleri (Sharpe, MDD vb.).
- **Arayüz:** Streamlit tabanlı kullanıcı arayüzü ve komut satırı desteği.

## Kurulum

Sistemi kurmak için:

```bash
bash setup.sh
```

## Testler

Bütün testleri çalıştırmak için:

```bash
python -m pytest
```

## Kullanım

### Komut Satırı (CLI)

Bir stratejiyi belirli bir varlık için test etmek:

```bash
python -m stratlab.run --ticker THYAO.IS --strategy ma_crossover --start 2024-01-01
```

### Arayüz (UI)

Web arayüzünü başlatmak için:

```bash
streamlit run src/stratlab/ui/app.py
```

---

Daha fazla bilgi için `HEDEF.md` dosyasını inceleyebilirsiniz.
