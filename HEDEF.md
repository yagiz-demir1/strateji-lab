# Hedef: Strateji Laboratuvarı

## Ne

Yeni ve bilinen yatırım stratejilerini toplayan, kaynağıyla kaydeden, geçmiş veride maliyetler dahil test eden, birbirleriyle ve al-tut ile karşılaştıran, arayüzü olan ve sürekli genişleyen bir araştırma sistemi.

Uzun vadede tutarlı çıkan stratejiler önce sanal portföyde, sonra küçük gerçek parayla çalıştırılır. Proje aylar ya da yıllar boyunca adım adım büyür; acele yoktur.

## Kim kullanacak

Sadece depo sahibi (tek kullanıcı). Kodu Python'u temel seviyede bilen biri inceleyecek:

- Kod basit ve açık olmalı; açıklayıcı isimler kullanılmalı.
- Her modülün başında ne yaptığını anlatan kısa bir açıklama olmalı.
- Kod içindeki isimler İngilizce; açıklamalar, raporlar ve arayüz metinleri Türkçe.

## İlkeler

1. Doğruluk hızdan önemlidir. Her hesap, sonucu önceden bilinen bir örnekle testten geçer.
2. Maliyetler (komisyon, spread) her testte dahildir.
3. Aşırı uyuma karşı korumalar çekirdeğin parçasıdır, sonradan eklenen bir süs değildir.
4. Her strateji kaynağıyla kaydedilir: fikir nereden geldi, hipotezi ne.
5. Her sonuç al-tut ile karşılaştırılır.
6. Gerçek parayla emir gönderen kod ajan tarafından yazılmaz (bkz. Faz 5).

## Piyasalar ve veri

- **Kapsam:** Borsa İstanbul, DAX, NASDAQ hisseleri ve endeksleri; altın ve petrol (Brent, WTI). Günlük veri.
- **Faz 1'deki çekirdek evren:** her piyasadan 5 büyük hisse, 3 endeks (XU100, DAX, NASDAQ-100) ve 3 emtia (altın, WTI, Brent). Tam endeks bileşenleri (BIST 30, DAX 40, NASDAQ-100) Faz 2'de eklenir.
- **Veri kaynağı:** araştırma için yfinance (kişisel kullanım). Veri erişimi tek bir modülde toplanır, böylece kaynak sonradan değiştirilebilir.
- **Önbellek:** indirilen veri yerelde saklanır; aynı veri tekrar indirilmez.
- **Testler internete çıkmaz;** `tests/fixtures/` altındaki örnek verilerle çalışır.
- **Bilinen sınırlar** (raporlar bunları not eder):
  - Bugünkü endeks bileşenlerini geçmişe uygulamak hayatta kalma yanlılığı yaratır; ileride tarihsel bileşen listesi eklenir.
  - Emtialar sürekli vadeli kontratlarla izlenir (ör. `GC=F`, `CL=F`, `BZ=F`); kontrat devirlerinde fiyatta yapay sıçramalar olabilir.
  - Varlıklar farklı para birimlerinde (TRY, EUR, USD). Faz 1'de her strateji kendi varlığının al-tut'uyla karşılaştırılır; piyasalar arası karşılaştırma için döviz çevirimi Faz 2'de eklenir.
  - Piyasaların işlem günleri farklı; çok varlıklı testlerde tarihler hizalanır.

## Fazlar

Fazlar sırayla yapılır. Bir fazın bitme şartı sağlanmadan sonrakine geçilmez.

### Faz 1 – Çekirdek (ilk sürüm)

- **Veri katmanı:** indirme, önbellek, temizlik (eksik günler, bölünme ve temettü düzeltmesi).
- **Gösterge kütüphanesi:** SMA, EMA, RSI, MACD, Bollinger bantları, ATR.
- **Backtest motoru:** günlük; sinyal → pozisyon → getiri; komisyon ve spread. Önce tek varlık, sonra çok varlık.
- **Metrikler:** toplam ve yıllık getiri, volatilite, Sharpe oranı, en büyük düşüş, işlem sayısı, isabet oranı, al-tut farkı.
- **Klasik stratejiler (5 adet):** hareketli ortalama kesişimi, RSI ortalamaya dönüş, 12-1 momentum, Bollinger kırılımı, MACD sinyali.
- **Rapor:** her test için Markdown rapor.
- **Arayüz:** Streamlit ile tek sayfa: strateji ve varlık seç, testi çalıştır, sonucu gör.

**Bitme şartı:** 5 strateji BIST ve DAX hisselerinde test edilebiliyor, sonuçlar raporlanıyor, arayüzden görülebiliyor ve bütün testler yeşil.

### Faz 2 – Kayıt ve karşılaştırma

- **Strateji kaydı:** her strateji için bir kart: ad, kaynak, hipotez, kurallar, parametreler, eklenme tarihi.
- **Sonuç veritabanı (SQLite):** her çalıştırma saklanır.
- **Karşılaştırma tablosu** ve arayüzde bir sayfası.
- **Aşırı uyum korumaları:**
  - Ayrılmış dönem: son 2 yıl sadece onaylanmış final testinde kullanılır.
  - Kayan pencere testi (walk-forward).
  - Çok sayıda deneme yapıldığında başarı eşiğini yükselten düzeltme (deflated Sharpe).
  - En az işlem sayısı şartı.
- **Parametre taraması.**

### Faz 3 – Fikir girişi

- Arayüzden elle strateji kartı girişi.
- **Kaynak tarama:** akademik çalışma özetleri (ör. arXiv q-fin) → model strateji kartı taslağı çıkarır → insan onaylar → görev olarak `BACKLOG.md`'ye eklenir.
- Planlayıcı (`PLANLAYICI.md`) sonuçlara bakarak yeni deneyler önerir.

### Faz 4 – İleriye dönük test (paper trading)

- Seçilen stratejiler her iş günü kapanıştan sonra sanal portföyde çalışır.
- Sonuçlar backtest ile karşılaştırılır. En az 3–6 ay sürer.

### Faz 5 – Gerçek para (ajanın kapsamı dışında)

- Ayrı bir modül; insan tarafından yazılır ve incelenir. Ajan bu faza ait kod yazmaz ve çalıştırmaz.
- **Ön koşullar:** Faz 4 sonuçları backtest ile tutarlı; aracı kurum şartları yazılı olarak alınmış; pozisyon üst sınırı, günlük zarar limiti ve acil durdurma hazır.

## Yapılmayacaklar (şimdilik)

- Gün içi veri ve yüksek frekanslı işlem.
- Gerçek emir gönderen kod (Faz 5 dışında hiçbir zaman, ajan tarafından hiçbir zaman).
- Başkasına sinyal yayınlama ya da satma.
- Çok kullanıcılı site, kullanıcı hesabı, ödeme sistemi.
- Ücretli veri ya da servis (karar `KARARLAR.md`'ye yazılmadan).

## Teknik tercihler

- Python 3.12, pandas, numpy, pytest. Arayüz için Streamlit (Faz 1'in son görevlerinde eklenir).
- Klasör yapısı:
  - `src/stratlab/data/` – veri katmanı
  - `src/stratlab/indicators/` – göstergeler
  - `src/stratlab/engine/` – backtest motoru
  - `src/stratlab/metrics/` – metrikler
  - `src/stratlab/strategies/` – stratejiler
  - `src/stratlab/reports/` – raporlar
  - `src/stratlab/ui/` – arayüz
  - `tests/` – testler, `tests/fixtures/` – örnek veri
- Kurulum: `bash setup.sh`. Testler: `python -m pytest`.
