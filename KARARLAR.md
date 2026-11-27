# Kararlar

Her karar için: tarih, karar, neden, değerlendirilen alternatifler.

## 2026-10-30 · Kodlama ajanı: Google Jules, ücretsiz katman

- **Neden:** ek maliyet yok, GitHub ile doğrudan çalışıyor.
- **Alternatifler:** Claude zamanlanmış görev, ayrı Claude Pro hesabı, GitHub Actions + API.
- **Tekrar bakılacak:** 2. hafta; aynı tür görevler Claude ile denenip `OLCUM.md`'deki sayılarla karşılaştırılacak.

## 2026-10-30 · Görev listesi: depoda `BACKLOG.md`

- **Neden:** iki ajan da dosyayı okuyabiliyor; ajan değiştirmek kolay.
- **Alternatif:** GitHub Issues.

## 2026-10-30 · Çalışma sıklığı: günde 1, ilk haftadan sonra 2

- **Neden:** darboğaz ajanın kotası değil, insanın inceleme süresi.
- **Kural:** açık öneri 3 veya fazlaysa ajan yeni görev almaz.

## 2026-11-27 · İlk proje: Strateji Laboratuvarı

- **Neden:** sonuçlar sayı olduğu için testle doğrulanabilir; kariyer hedefiyle (yatırım alanı) örtüşür; izin ya da talep doğrulaması beklemeden başlanabilir.
- **Alternatifler:** işletme izleme altyapısı (talep henüz doğrulanmadı), gayrimenkul veri takibi, alarm botu.

## 2026-11-27 · Dil Python, arayüz Streamlit

- **Neden:** proje sahibi Python'u temel seviyede biliyor; Streamlit arayüzü de Python ile yazılır, ayrıca JavaScript gerekmez.
- **Alternatif:** TypeScript ile web arayüzü (okuması ve test etmesi daha zor).

## 2026-11-27 · Araştırma verisi: yfinance, günlük

- **Neden:** ücretsiz; BIST (`.IS` uzantısı) ve Xetra hisselerini kapsıyor.
- **Sınır:** resmi bir API değil, kişisel kullanım içindir ve bozulabilir. Bu yüzden veri erişimi tek bir modülde toplanır. Sonuçlar dışarıya fiyat verisi olarak yayınlanmaz.

## 2026-11-27 · Kurulum komutu: `bash setup.sh`

- **Neden:** GitHub'ın web arayüzünden yüklenen dosyalar çalıştırma iznini taşımıyor; `./setup.sh` bu yüzden hata verir.

## 2026-11-27 · Kodlama ajanı değişti: Gemini CLI + GitHub Actions (Jules yerine)

- **Neden:** Jules 11 Kasım 2026'dan beri sadece görüntüleme modunda, 31 Aralık 2026'da kapanıyor. Ajan, proje sahibinin Claude kotasından ayrı bir kotayla çalışmalı.
- **Nasıl:** `.github/workflows/ajan.yml` her gün bir kez çalışır. Model ayrı bir Google AI Studio projesinin ücretsiz API anahtarıyla (`GEMINI_API_KEY`) çağrılır. Model adı `GEMINI_MODEL` depo değişkeniyle değiştirilebilir.
- **Güvenlik:** öneriyi ajan değil iş akışının son adımı açar; ana dala yazılmaz. Testler iş akışında tekrar çalışır; `HEDEF.md`, `AGENTS.md`, `DERSLER.md` ve `.github/` değişirse öneri açılmaz.
- **Sınırlar:** ücretsiz katmanda sadece Flash modelleri; gönderilen içerik Google'ın ürün geliştirmesinde kullanılabilir.
- **Alternatifler:** Antigravity + Google AI Plus (muhtemelen bilgisayarın açık olmasını gerektirir), Claude zamanlanmış görevi (proje sahibinin Claude kotasını kullanır), aynı kurulumun ücretli API ile çalışması.
- **Tekrar bakılacak:** 2. hafta karar kapısında `OLCUM.md`'deki sayılarla.

## 2026-11-27 · Piyasalar: BIST, DAX, NASDAQ, altın ve petrol

- **Karar:** proje sahibinin seçimi. Faz 1'de her piyasadan 5 büyük hisse, 3 endeks ve 3 emtia (altın, WTI, Brent); tam endeks bileşenleri Faz 2'de.
- **Neden çekirdek evrenle başlanıyor:** bileşen listelerini doğru tutmak ayrı bir iş; Faz 1'in amacı motoru doğrulamak.
- **Bilinen sınırlar:** vadeli kontrat devirleri, farklı para birimleri ve işlem takvimleri (`HEDEF.md`).

## 2026-11-27 · Varsayımlar: Streamlit arayüzü ve 5 klasik strateji

- **Durum:** proje sahibi bu iki soruyu cevaplamadı; öneriler varsayıldı ve değiştirilebilir.
- **Arayüz:** Streamlit, önce yerel bilgisayarda.
- **Stratejiler:** hareketli ortalama kesişimi, RSI ortalamaya dönüş, 12-1 momentum, Bollinger kırılımı, MACD.

## 2026-11-27 · Mimari yön: ajan araştırır, test edilmiş motor karar verir

- **Karar:** dil modeli tabanlı ajan araştırma, hipotez üretme ve raporlamada; alım-satım kararı sabit kodlu, test edilmiş karar motorunda.
- **Neden:** dil modelinin kararları geçmiş veride güvenilir test edilemez (gelecek sızıntısı); aynı girdiye farklı cevap verebilir; ikna edici ama yanlış gerekçe üretebilir; her karar için çağırmak pahalı ve yavaş.
- **İstisna:** ajanın ürettiği skorlar sinyal olarak karar motoruna girebilir; ağırlıkları ileriye dönük testle belirlenir.
- **Alternatif:** kararı doğrudan ajanın vermesi (test edilemez, denetlenemez).

## 2026-11-27 · Yedek: ayrı bir gizli GitHub deposu

- **Karar:** ana daldaki proje her birleştirmede ve haftada bir `strateji-lab-yedek` adlı gizli depoya kopyalanır (`.github/workflows/yedek.yml`). Proje sahibinin tercihi.
- **Neden:** git geçmişi ajan hatalarına karşı zaten koruyor; yedek, ana deponun silinmesi ya da bozulması gibi durumlara karşı.
- **Güvenlik:** zorla yazma yok; geçmiş beklenmedik şekilde değişirse kopyalama durur ve yedek ezilmez. Erişim anahtarı sadece yedek deposuna yazabilir.
- **Sınır:** iki depo aynı GitHub hesabında; hesaba bir şey olursa ikisi birden etkilenir. Bu risk için ileride farklı bir sağlayıcı (ör. GitLab) eklenebilir.
