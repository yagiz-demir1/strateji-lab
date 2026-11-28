# Görev listesi

Görevler yukarıdan aşağıya yapılır. Her görev `GOREV_SABLONU.md`'ye uyar. Yapılan görev `[x]` ile işaretlenir.

## Faz 1 – Çekirdek

## [x] G-001: Testler için örnek fiyat verisi

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

## [x] G-002: Basit ve üstel hareketli ortalama (SMA, EMA)

**Hedef:** Stratejilerin kullanacağı ilk iki gösterge.

**Bitme şartı (test):**
- `sma(series, window)` ve `ema(series, window)` fonksiyonları girdiyle aynı uzunlukta bir pandas Series döndürür.
- `sma`: `[1, 2, ..., 10]` serisi, `window=3` için son değer `9.0`; ilk 2 değer NaN.
- `ema`: `adjust=False` ve `alpha = 2 / (window + 1)` ile hesaplanır. `[1, 2, 3]` serisi, `window=2` için değerler yaklaşık `[1.0, 1.6667, 2.5556]` (4 basamak).
- `window < 1` için `ValueError`.

**Dokunulacak dosyalar:** `src/stratlab/indicators/__init__.py`, `src/stratlab/indicators/moving_averages.py`, `tests/test_moving_averages.py`

**Kapsam dışı:** Diğer göstergeler.

**Örnek girdi → çıktı:** `sma(pd.Series([1,2,3,4]), 2)` → `[NaN, 1.5, 2.5, 3.5]`

## [x] G-003: RSI göstergesi

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

## [x] G-004: Tek varlık backtest motoru (maliyetsiz)

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

## [x] G-005: İşlem maliyetleri

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

## [x] G-021: İşlem maliyeti düzeltmesi (öneri #6'dan kalan eksikler)

Önce G-005 bitmeli.

**Hedef:** G-005 birleştirildikten sonra incelemede bulunan iki eksiği gidermek: 0. gündeki alımın maliyeti düşülmüyor ve "pozisyon hiç değişmezse maliyet 0" şartının testi yok.

**Bitme şartı (test):**
- Başlangıçta nakitte olunduğu varsayılır: 0. gün pozisyon 1 ise bu bir değişikliktir ve 0. günün `equity` değeri `(1 - cost_bps / 10000)` ile çarpılır. Sabit fiyat, `positions = [1, 1, 1, 1]`, `cost_bps=10` → bütün `equity` değerleri `0.999`.
- `cost_bps=0` iken `equity` 1.0'dan başlar; G-004 testleri değişmeden geçer.
- Pozisyon hep 0 ise `cost_bps=10` ile de `equity` hep 1.0.
- Sabit fiyat, `positions = [0, 1, 1, 0]`, `cost_bps=10` → son `equity` ≈ `0.998001` (bugünkü davranış korunur).

**Not:** `tests/test_backtest.py`'deki 5 günlük örnek testine, öneri #6'da silinen elle hesap açıklamaları (her günün getirisi ve sermayesi) yorum olarak geri eklenir.

**Dokunulacak dosyalar:** `src/stratlab/engine/backtest.py`, `tests/test_backtest.py`

**Kapsam dışı:** Pozisyon büyüklüğüne göre maliyet, kayma (slippage) modeli.

**Örnek girdi → çıktı:** `run_backtest(pd.Series([100.0] * 4), pd.Series([1, 1, 1, 1]), cost_bps=10)["equity"]` → `[0.999, 0.999, 0.999, 0.999]`

## [x] G-006: Temel performans metrikleri

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

## [x] G-007: Hareketli ortalama kesişimi stratejisi

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

## [x] G-008: Al-tut karşılaştırmalı Markdown rapor

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

## [x] G-009: Çekirdek varlık evreni

**Hedef:** Faz 1'de test edilecek varlıkların tek bir yerde tanımlı olması.

**Bitme şartı (test):**
- `src/stratlab/data/universe.py` içinde `UNIVERSE` sözlüğü; gruplar ve içerik tam olarak:
  - `bist`: `THYAO.IS`, `ASELS.IS`, `KCHOL.IS`, `GARAN.IS`, `BIMAS.IS`
  - `dax`: `SAP.DE`, `SIE.DE`, `ALV.DE`, `DTE.DE`, `MBG.DE`
  - `nasdaq`: `AAPL`, `MSFT`, `NVDA`, `AMZN`, `GOOGL`
  - `endeksler`: `XU100.IS`, `^GDAXI`, `^NDX`
  - `emtia`: `GC=F` (altın), `CL=F` (WTI petrol), `BZ=F` (Brent petrol)
- `all_tickers()` tekrarsız düz liste döndürür; `group_of(ticker)` grubun adını döndürür; bilinmeyen ticker için `KeyError`.
- Testler: grup boyutları 5, 5, 5, 3, 3; `bist` hisseleri `.IS`, `dax` hisseleri `.DE` ile bitiyor; tekrar yok.

**Dokunulacak dosyalar:** `src/stratlab/data/__init__.py`, `src/stratlab/data/universe.py`, `tests/test_universe.py`

**Kapsam dışı:** Veri indirme; tam endeks bileşen listeleri (Faz 2).

**Örnek girdi → çıktı:** `group_of("GC=F")` → `"emtia"`

## [x] G-010: Veri indirme ve yerel önbellek

Önce G-001 ve G-009 bitmeli.

**Hedef:** Günlük fiyat verisini indirip yerelde saklayan, kaynağı değiştirilebilir bir katman.

**Bitme şartı (test):**
- `load_prices(ticker, start, end, source=None, cache_dir=".cache/prices")` sütunları `open, high, low, close, volume` olan, tarih indeksli bir DataFrame döndürür.
- `source` verilmezse yfinance kullanılır (bölünme ve temettü düzeltilmiş fiyatlar). Testlerde `source` olarak sahte bir fonksiyon verilir; testler internete çıkmaz.
- İlk çağrıda veri önbelleğe CSV olarak yazılır. Aynı parametrelerle ikinci çağrıda kaynak fonksiyonu hiç çağrılmaz (test: çağrı sayacı 1).
- Kaynak boş veri döndürürse `ValueError`.
- `requirements.txt`'ye `yfinance` eklenir.

**Dokunulacak dosyalar:** `src/stratlab/data/loader.py`, `src/stratlab/data/__init__.py`, `requirements.txt`, `tests/test_loader.py`

**Kapsam dışı:** Önbelleği güncelleme ya da uzatma mantığı, döviz çevirimi.

**Örnek girdi → çıktı:** `load_prices("THYAO.IS", "2020-01-01", "2020-03-31", source=sahte)` → sahte kaynağın verisi, aynı biçimde.

## [x] G-011: Bollinger bantları ve ATR

Önce G-002 bitmeli.

**Hedef:** İki gösterge daha.

**Bitme şartı (test):**
- `bollinger(close, window=20, k=2)` sütunları `mid, upper, lower` olan bir DataFrame döndürür. `mid` = SMA; bant genişliği = `k` × standart sapma (popülasyon, `ddof=0`). Sabit bir seride `upper == lower == mid`.
- `atr(high, low, close, window=14)` Wilder yöntemiyle hesaplanır. Gerçek aralık (true range) = `max(high - low, |high - önceki close|, |low - önceki close|)`; ilk ATR ilk `window` gerçek aralığın ortalaması.
- Elle örnek: `high = [10, 12, 11]`, `low = [8, 9, 9]`, `close = [9, 11, 10]`, `window = 2` → `[NaN, 2.5, 2.25]`.
- Sabit fiyatlı bir seride ATR 0.

**Dokunulacak dosyalar:** `src/stratlab/indicators/bollinger.py`, `src/stratlab/indicators/atr.py`, `src/stratlab/indicators/__init__.py`, `tests/test_bollinger.py`, `tests/test_atr.py`

**Kapsam dışı:** Stratejiler.

**Örnek girdi → çıktı:** yukarıdaki ATR örneği.

## [x] G-012: MACD göstergesi

Önce G-002 bitmeli.

**Hedef:** MACD, sinyal çizgisi ve histogram.

**Bitme şartı (test):**
- `macd(close, fast=12, slow=26, signal=9)` sütunları `macd, signal, hist` olan bir DataFrame döndürür.
- `macd` = `ema(close, fast) - ema(close, slow)` (G-002'deki `ema`); `signal` = `ema(macd, signal)`; `hist` = `macd - signal`.
- Sabit bir seride üç sütun da 0.
- `fast >= slow` için `ValueError`.

**Dokunulacak dosyalar:** `src/stratlab/indicators/macd.py`, `src/stratlab/indicators/__init__.py`, `tests/test_macd.py`

**Kapsam dışı:** Stratejiler.

**Örnek girdi → çıktı:** sabit seri → `macd`, `signal`, `hist` hep 0.

## [x] G-022: RSI'da Wilder başlatması ve bilinen örnek testi

Önce G-003 bitmeli.

**Hedef:** RSI'ı ATR (G-011) ile aynı Wilder yöntemiyle hesaplamak. İlk ortalama kazanç ve kayıp, ilk `window` değişimin basit ortalamasıdır; sonrakiler `(önceki × (window − 1) + bugünkü) / window`. Bugünkü üstel ortalama başlatması ilk 50–100 günde çok farklı değer veriyor (aşağıdaki örnekte ilk RSI 70.46 yerine 50.66).

**Bitme şartı (test):**
- Klasik örnek, `window=14`, 33 kapanış: `[44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64, 46.21, 46.25, 45.71, 46.45, 45.78, 45.35, 44.03, 44.18, 44.22, 44.57, 43.42, 42.66, 43.13]`.
- İlk 14 değer (indeks 0–13) NaN; indeks 14'ten itibaren RSI (±0.01): `[70.46, 66.25, 66.48, 69.35, 66.29, 57.92, 62.88, 63.21, 56.01, 62.34, 54.67, 50.39, 40.02, 41.49, 41.90, 45.50, 37.32, 33.09, 37.79]`.
- İlk değerin elle hesabı test içinde yorum olarak yazılır: ilk 14 değişimin ortalama kazancı 0.238571, ortalama kaybı 0.100000 → RS = 2.38571 → RSI = 100 − 100 / (1 + 2.38571) = 70.46.
- G-003'ün mevcut testleri değiştirilmeden geçer (sürekli yükselen seride 100, sürekli düşen seride 0, sabit seride NaN, ilk 14 değer NaN, pencere < 2 ise hata).

**Dokunulacak dosyalar:** `src/stratlab/indicators/rsi.py`, `tests/test_rsi.py`

**Kapsam dışı:** Diğer göstergeler ve stratejiler.

**Örnek girdi → çıktı:** yukarıdaki 33 kapanış → indeks 14'te RSI 70.46, son değer 37.79.

## [x] G-013: RSI ortalamaya dönüş stratejisi

Önce G-003 bitmeli.

**Hedef:** RSI düşükken al, yüksekken sat.

**Bitme şartı (test):**
- Yardımcı fonksiyon `threshold_positions(signal, low, high)`: sinyal `low`'un altına inince 1'e geçer, `high`'ın üstüne çıkınca 0'a döner, arada önceki pozisyonu korur; başlangıç 0.
- Elle örnek: sinyal `[50, 25, 40, 75, 50]`, `low = 30`, `high = 70` → `[0, 1, 1, 0, 0]`.
- `rsi_reversion_positions(close, window=14, low=30, high=70)` bu yardımcıyı RSI ile kullanır; RSI'nın hesaplanamadığı günler 0.
- `low >= high` için `ValueError`.

**Dokunulacak dosyalar:** `src/stratlab/strategies/rsi_reversion.py`, `src/stratlab/strategies/__init__.py`, `tests/test_rsi_reversion.py`

**Kapsam dışı:** Backtest motorunu çalıştırmak.

**Örnek girdi → çıktı:** yukarıdaki elle örnek.

## [x] G-014: 12-1 momentum stratejisi

**Hedef:** Son bir yılın getirisi (son ay hariç) pozitifse alımda kal.

**Bitme şartı (test):**
- `momentum_positions(close, lookback=252, skip=21)`: `t` gününde getiri = `close[t - skip] / close[t - lookback] - 1`; getiri > 0 ise 1, değilse 0. İlk `lookback` gün 0.
- Her gün yükselen bir seride ilk `lookback` günden sonra bütün pozisyonlar 1; her gün düşen bir seride hepsi 0.
- `skip >= lookback` için `ValueError`.

**Dokunulacak dosyalar:** `src/stratlab/strategies/momentum.py`, `src/stratlab/strategies/__init__.py`, `tests/test_momentum.py`

**Kapsam dışı:** Birden çok varlık arasında sıralama (kesitsel momentum).

**Örnek girdi → çıktı:** `momentum_positions(pd.Series(range(1, 301)), 252, 21)` → ilk 252 değer 0, sonrası 1.

## [x] G-015: Bollinger kırılım stratejisi

Önce G-011 bitmeli.

**Hedef:** Fiyat üst bandı aşınca al, orta bandın altına inince sat.

**Bitme şartı (test):**
- `bollinger_breakout_positions(close, window=20, k=2)`: kapanış üst bandın üstüne çıkınca 1'e geçer, orta bandın altına inince 0'a döner, arada önceki pozisyonu korur; bantların hesaplanamadığı günler 0.
- Elle kurulmuş bir seriyle test: uzun süre sabit fiyattan sonra ani bir yükseliş 1'e geçirir; ardından orta bandın altına düşüş 0'a döndürür.

**Dokunulacak dosyalar:** `src/stratlab/strategies/bollinger_breakout.py`, `src/stratlab/strategies/__init__.py`, `tests/test_bollinger_breakout.py`

**Kapsam dışı:** Açığa satış.

**Örnek girdi → çıktı:** 25 gün 100, sonra 110 → o gün pozisyon 1.

## [x] G-016: MACD stratejisi

Önce G-012 bitmeli.

**Hedef:** MACD sinyal çizgisinin üstündeyken alımda kal.

**Bitme şartı (test):**
- Yardımcı fonksiyon `cross_positions(a, b)`: `a > b` olan günler 1, diğerleri 0; iki seriden biri NaN ise 0.
- Elle örnek: `a = [1, 2, 3, 2]`, `b = [2, 2, 1, 3]` → `[0, 0, 1, 0]`.
- `macd_positions(close, fast=12, slow=26, signal=9)` = `cross_positions(macd, signal)`.

**Dokunulacak dosyalar:** `src/stratlab/strategies/macd_strategy.py`, `src/stratlab/strategies/__init__.py`, `tests/test_macd_strategy.py`

**Kapsam dışı:** Histogram tabanlı varyantlar.

**Örnek girdi → çıktı:** yukarıdaki elle örnek.

## [ ] G-017: İşlem sayısı ve isabet oranı

Önce G-004 bitmeli.

**Hedef:** Bir stratejinin kaç işlem yaptığını ve işlemlerin ne kadarının kârlı olduğunu ölçmek.

**Bitme şartı (test):**
- `trade_count(positions)`: 0'dan 1'e geçişlerin sayısı. `[0, 1, 1, 0, 1, 0]` → 2.
- `hit_rate(close, positions)`: G-004'teki backtest kuralıyla (pozisyon bir gün kaydırılır) her işlemin toplam getirisi hesaplanır; kârlı işlemlerin oranı döner.
- Elle örnek: `close = [100, 110, 110, 90, 100, 105]`, `positions = [0, 1, 1, 0, 1, 0]` → ilk işlem zararda (-%18,18), ikinci kârda (+%5) → `0.5`.
- Hiç işlem yoksa `hit_rate` NaN.

**Dokunulacak dosyalar:** `src/stratlab/metrics/trades.py`, `src/stratlab/metrics/__init__.py`, `tests/test_trades.py`

**Kapsam dışı:** Ortalama işlem süresi, işlem listesi raporu.

**Örnek girdi → çıktı:** yukarıdaki elle örnek → `0.5`.

## [ ] G-018: Komut satırından backtest

Önce G-007, G-008, G-010 ve G-013 – G-016 bitmeli.

**Hedef:** Tek komutla bir varlıkta bir stratejiyi test edip rapor üretmek.

**Bitme şartı (test):**
- `python -m stratlab.run --ticker THYAO.IS --strategy ma_crossover --start 2015-01-01` komutu `reports/THYAO.IS_ma_crossover.md` dosyasını yazar.
- Strateji adları `STRATEGIES` sözlüğünden gelir: `ma_crossover`, `rsi_reversion`, `momentum_12_1`, `bollinger_breakout`, `macd`.
- `--cost-bps` seçeneği vardır; varsayılan 10.
- Test: G-010'daki `source` parametresiyle sahte veri verilerek çalıştırılır; rapor dosyası oluşur ve başlığı doğru; bilinmeyen strateji adı çıkış kodu 2 ile biter.
- `reports/` klasörü `.gitignore`'a eklenir.

**Dokunulacak dosyalar:** `src/stratlab/run.py`, `src/stratlab/strategies/__init__.py`, `.gitignore`, `tests/test_run.py`

**Kapsam dışı:** Birden çok varlığı aynı anda test etmek, arayüz.

**Örnek girdi → çıktı:** yukarıdaki komut → `reports/THYAO.IS_ma_crossover.md`.

## [ ] G-019: Streamlit arayüzü (tek sayfa)

Önce G-017 ve G-018 bitmeli.

**Hedef:** Varlık ve strateji seçip sonucu grafikle görmek.

**Bitme şartı (test):**
- Hesaplama arayüzden ayrı bir fonksiyonda: `run_selected(ticker, strategy, start, end, cost_bps, source=None)` → sermaye eğrisi (strateji ve al-tut) ve metrik tablosu. Bu fonksiyon sahte veri kaynağıyla test edilir.
- `src/stratlab/ui/app.py`: kenar çubuğunda varlık (G-009 evreni), strateji, tarih aralığı ve maliyet seçimi; "Çalıştır" ile sermaye eğrisi grafiği ve metrik tablosu (işlem sayısı ve isabet oranı dahil). Metinler Türkçe.
- Arayüz testi: `streamlit.testing.v1.AppTest` ile uygulama hatasız açılıyor.
- `requirements.txt`'ye `streamlit` eklenir.

**Dokunulacak dosyalar:** `src/stratlab/ui/__init__.py`, `src/stratlab/ui/app.py`, `src/stratlab/ui/logic.py`, `requirements.txt`, `tests/test_ui.py`

**Kapsam dışı:** Birden çok sayfa, kullanıcı hesabı, sunucuya yükleme.

**Örnek girdi → çıktı:** `streamlit run src/stratlab/ui/app.py` → tarayıcıda tek sayfalık arayüz.

## [ ] G-020: Faz 1 kapanışı: uçtan uca test ve kullanım kılavuzu

Önce G-019 bitmeli.

**Hedef:** Faz 1'in bitme şartının otomatik olarak kontrol edilmesi ve kullanım talimatının yazılması.

**Bitme şartı (test):**
- `tests/test_faz1.py`: 5 stratejinin hepsi iki örnek veri dosyasıyla hatasız çalışıyor ve her biri için rapor üretiliyor.
- `README.md` (Türkçe): projenin ne olduğu, kurulum, testler, komut satırı ve arayüzün nasıl çalıştırılacağı.

**Dokunulacak dosyalar:** `tests/test_faz1.py`, `README.md`

**Kapsam dışı:** Faz 2 işleri.

**Örnek girdi → çıktı:** `python -m pytest tests/test_faz1.py` → geçiyor.
