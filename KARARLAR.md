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
