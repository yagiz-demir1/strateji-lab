# Görev listesi

Görevler yukarıdan aşağıya yapılır. Her görev `GOREV_SABLONU.md`'ye uyar. Yapılan görev `[x]` ile işaretlenir.

## Faz 1 – Çekirdek

## [ ] G-001: Testler için örnek fiyat verisi

**Hedef:** Testlerin internete çıkmadan kullanacağı küçük, sabit fiyat verisi ve onu okuyan yardımcı fonksiyon.

**Bitme şartı (test):**
- `tests/fixtures/` altında iki CSV dosyası var: `yukselen.csv` ve `dalgali.csv`. Her biri 60 iş günü, sütunlar `date, open, high, low, close, volume`.
- Veriler el ile ya da sabit tohumlu (seed) bir betikle üretilmiş sentetik veridir; gerçek piyasa verisi değildir.
- `yukselen.csv`'de kapanış fiyatı her gün bir öncekinden yüksek; `dalgali.csv`'de en az 5 kez yön değiştiriyor.
- `tests/helpers.py` içindeki `load_fixture(name)` fonksiyonu tarihi indeks olan bir pandas DataFrame döndürür.
- Testler: satır sayısı 60; sütun adları doğru; tarihler artan sırada; eksik değer yok; her satırda `low <= open, close <= high`.

**Dokunulacak dosyalar:** `tests/fixtures/yukselen.csv`, `tests/fixtures/dalgali.csv`, `tests/helpers.py`, `tests/test_fixtures.py`

**Kapsam dışı:** İnternetten veri indirme, `src/` altındaki kod.

**Örnek girdi → çıktı:** `load_fixture("yukselen")` → 60 satırlık DataFrame, indeks `date`.

## [ ] G-002: Basit ve üstel hareketli ortalama (SMA, EMA)

**Hedef:** Stratejilerin kullanacağı ilk iki gösterge.

**Bitme şartı (test):**
- `sma(series, window)` ve `ema(series, window)` fonksiyonları girdiyle aynı uzunlukta bir pandas Series döndürür.
- `sma`: `[1, 2, ..., 10]` serisi, `window=3` için son değer `9.0`; ilk 2 değer NaN.
- `ema`: `adjust=False` ve `alpha = 2 / (window + 1)` ile hesaplanır. `[1, 2, 3]` serisi, `window=2` için değerler yaklaşık `[1.0, 1.6667, 2.5556]` (4 basamak).
- `window < 1` için `ValueError`.

**Dokunulacak dosyalar:** `src/stratlab/indicators/__init__.py`, `src/stratlab/indicators/moving_averages.py`, `tests/test_moving_averages.py`

**Kapsam dışı:** Diğer göstergeler.

**Örnek girdi → çıktı:** `sma(pd.Series([1,2,3,4]), 2)` → `[NaN, 1.5, 2.5, 3.5]`

## [ ] G-003: RSI göstergesi

**Hedef:** Wilder yöntemiyle RSI.

**Bitme şartı (test):**
- `rsi(close, window=14)` girdiyle aynı uzunlukta Series döndürür; ilk `window` değer NaN.
- Tanımlı bütün değerler 0 ile 100 arasında.
- Her gün yükselen bir seride son değer 100; her gün düşen bir seride 0.
- Hiç değişmeyen bir seride değerler NaN.
- `window < 2` için `ValueError`.

**Dokunulacak dosyalar:** `src/stratlab/indicators/rsi.py`, `src/stratlab/indicators/__init__.py`, `tests/test_rsi.py`

**Kapsam dışı:** Diğer göstergeler, stratejiler.

**Örnek girdi → çıktı:** `rsi(pd.Series(range(1, 31)), 14).iloc[-1]` → `100.0`

## [ ] G-004: Tek varlık backtest motoru (maliyetsiz)

**Hedef:** Pozisyon serisinden (0 = nakit, 1 = alımda) günlük strateji getirisi ve sermaye eğrisi.

**Bitme şartı (test):**
- `run_backtest(close, positions)` sütunları `returns` ve `equity` olan bir DataFrame döndürür; `equity` 1.0'dan başlar.
- Bugünkü pozisyon yarının getirisine uygulanır (geleceği görme hatası yok): pozisyon bir gün kaydırılır.
- Pozisyon hep 1 ise son `equity`, `close` son değerinin ilk değerine oranına eşit (al-tut).
- Pozisyon hep 0 ise bütün getiriler 0, `equity` hep 1.0.
- 5 günlük elle hesaplanmış bir örnek: `close = [100, 110, 99, 99, 108.9]`, `positions = [1, 1, 0, 1, 1]` → son `equity` = `1.1 × 0.9 × 1.0 × 1.1` = `1.089`.
- `close` ve `positions` uzunlukları farklıysa `ValueError`.

**Dokunulacak dosyalar:** `src/stratlab/engine/__init__.py`, `src/stratlab/engine/backtest.py`, `tests/test_backtest.py`

**Kapsam dışı:** İşlem maliyetleri, çok varlık, açığa satış.

**Örnek girdi → çıktı:** yukarıdaki 5 günlük örnek.

## [ ] G-005: İşlem maliyetleri

Önce G-004 bitmeli.

**Hedef:** Backtest'e komisyon ve spread'i temsil eden maliyet eklemek.

**Bitme şartı (test):**
- `run_backtest(close, positions, cost_bps=0)` parametresi eklenir; varsayılan 0 ve G-004 testleri değişmeden geçer.
- Pozisyonun her değiştiği gün `equity`, `(1 - cost_bps / 10000)` ile çarpılır.
- Hiç pozisyon değişikliği yoksa maliyetin etkisi 0.
- Fiyatı sabit bir seride bir alım ve bir satım, `cost_bps=10` ile son `equity` = `0.999 × 0.999`.
- Negatif `cost_bps` için `ValueError`.

**Dokunulacak dosyalar:** `src/stratlab/engine/backtest.py`, `tests/test_backtest.py`

**Kapsam dışı:** Kayma (slippage) modeli, vergi.

**Örnek girdi → çıktı:** sabit fiyat, `positions = [0, 1, 1, 0]`, `cost_bps=10` → son `equity` ≈ `0.998001`.

## [ ] G-006: Temel performans metrikleri

Önce G-004 bitmeli.

**Hedef:** Bir sermaye eğrisini özetleyen sayılar.

**Bitme şartı (test):**
- `src/stratlab/metrics/basic.py` içinde: `total_return`, `annual_return` (252 iş günü), `annual_volatility`, `sharpe` (risksiz faiz 0), `max_drawdown`.
- `max_drawdown([1.0, 1.2, 0.9, 1.1])` = `-0.25`.
- `total_return([1.0, 1.1, 1.21])` = `0.21` (4 basamak).
- Getirileri hep 0 olan bir seride volatilite 0 ve Sharpe NaN.
- Hepsi elle hesaplanmış örneklerle test edilir.

**Dokunulacak dosyalar:** `src/stratlab/metrics/__init__.py`, `src/stratlab/metrics/basic.py`, `tests/test_metrics.py`

**Kapsam dışı:** İsabet oranı, işlem sayısı, al-tut karşılaştırması.

**Örnek girdi → çıktı:** `max_drawdown(pd.Series([1.0, 1.2, 0.9, 1.1]))` → `-0.25`

## [ ] G-007: Hareketli ortalama kesişimi stratejisi

Önce G-002 bitmeli.

**Hedef:** İlk strateji: kısa ortalama uzun ortalamanın üstündeyken alımda kal.

**Bitme şartı (test):**
- `ma_crossover_positions(close, fast, slow)` 0/1 değerli bir Series döndürür.
- Kısa ortalama uzun ortalamanın üstündeyse 1, değilse 0; ortalamaların henüz hesaplanamadığı ilk günler 0.
- `fast >= slow` için `ValueError`.
- `load_fixture("yukselen")` ile `fast=5, slow=20` için 20. günden sonra bütün pozisyonlar 1.

**Dokunulacak dosyalar:** `src/stratlab/strategies/__init__.py`, `src/stratlab/strategies/ma_crossover.py`, `tests/test_ma_crossover.py`

**Kapsam dışı:** Backtest motorunu çalıştırmak, parametre taraması.

**Örnek girdi → çıktı:** sürekli yükselen seri, `fast=2, slow=4` → 4. günden itibaren 1.

## [ ] G-008: Al-tut karşılaştırmalı Markdown rapor

Önce G-004 ve G-006 bitmeli.

**Hedef:** Bir backtest sonucunu al-tut ile yan yana gösteren rapor.

**Bitme şartı (test):**
- `make_report(name, strategy_equity, benchmark_equity)` Markdown metni döndürür.
- Rapor bir başlık, iki sütunlu (Strateji, Al-tut) metrik tablosu ve "Fark" satırı içerir.
- Metrikler G-006 fonksiyonlarıyla hesaplanır; yüzdeler 2 basamaklı.
- Test: bilinen iki sermaye eğrisiyle üretilen raporda beklenen başlık ve sayılar geçiyor.

**Dokunulacak dosyalar:** `src/stratlab/reports/__init__.py`, `src/stratlab/reports/markdown.py`, `tests/test_report.py`

**Kapsam dışı:** Grafik, HTML, dosyaya yazma, arayüz.

**Örnek girdi → çıktı:** `make_report("MA 5/20", eq_strateji, eq_altut)` → `# MA 5/20` başlıklı, tablolu metin.
