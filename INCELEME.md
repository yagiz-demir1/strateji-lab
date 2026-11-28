# İnceleme kontrol listesi

Her öneri bu listeyle incelenir. Önce sen kullanırsın; 3.–4. haftada ikinci bir model de her öneriyi bu listeye göre otomatik inceler.

1. **Otomatik test:** öneri sayfasında "Ajan: testler" yeşil mi? (Ajanın açtığı önerilerde "Testler" iş akışı ayrıca onay bekler; istersen "Approve and run" ile çalıştırabilirsin.)
2. **Testin değeri:** yeni test görevin bitme şartını gerçekten ölçüyor mu, yoksa her durumda geçen boş bir test mi?
3. **Test zayıflatma:** mevcut bir test silinmiş, atlanmış ya da gevşetilmiş mi?
4. **Kapsam:** sadece görevin "Dokunulacak dosyalar" bölümündeki dosyalar mı değişmiş?
5. **Gizli bilgi:** koda ya da dosyalara anahtar, şifre veya token girmiş mi?
6. **Yeni kütüphane:** eklendiyse nedeni açıklamada yazıyor mu?
7. **Kayıt:** `ILERLEME.md`'ye satır eklenmiş ve `BACKLOG.md`'de görev işaretlenmiş mi?
8. **Anlaşılırlık:** anlamadığın bir yer varsa açıklama iste.

## Karar

- **Birleştir:** hepsi geçtiyse.
- **Küçük düzeltme:** 5 dakikadan kısa sürüyorsa kendin yap (öneri sayfasında "Files changed" → dosyadaki üç nokta → "Edit file"), sonra birleştir. Ajan şimdilik öneri yorumlarını okumuyor.
- **Reddet:** öneriyi kapat ve `DERSLER.md`'ye bir kural yaz.

## İkinci model için çıktı biçimi

Her madde için tek satır: `N. Geçti` ya da `N. Sorun: <bir cümle>`. Sonunda öneri: Birleştir / Düzeltme iste / Reddet.
