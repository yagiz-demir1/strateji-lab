# Görev şablonu

`BACKLOG.md`'deki her görev bu biçimde yazılır.

```markdown
## [ ] G-000: Görevin kısa adı

**Hedef:** Tek cümle: bu görev bitince ne mümkün olacak.

**Bitme şartı (test):**
- Otomatik testle kontrol edilecek, ölçülebilir koşul 1
- Koşul 2

**Dokunulacak dosyalar:** `src/...`, `tests/...`

**Kapsam dışı:** Bu görevde yapılmayacak olanlar.

**Örnek girdi → çıktı:** `fonksiyon(girdi)` → `beklenen sonuç`
```

## Kurallar

- Görev tek bir öneride bitebilecek büyüklükte olmalı (kabaca 200 satırdan az değişiklik).
- Bitme şartı ölçülebilir olmalı. "İyileştir", "güzelleştir", "hızlandır" gibi ölçüsüz kelimeler kullanılmaz; kullanılacaksa bir sayıya bağlanır.
- Görev başka bir göreve bağlıysa adını yaz: "Önce G-003 bitmeli."
- Görev numaraları artarak gider ve tekrar kullanılmaz.
