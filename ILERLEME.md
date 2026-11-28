# İlerleme günlüğü

Her çalışmadan sonra bir satır eklenir; en yeni kayıt en altta.

Biçim: `- YYYY-AA-GG · Görev adı · Sonuç`

Sonuç örnekleri: "Öneri açıldı (#3)", "Testler geçmedi: veri dosyası bulunamadı", "Açık öneri 3, yeni görev alınmadı".

- 2026-11-27 · Kurulum (insan + Claude, ajan çalışması değil) · `HEDEF.md`, iskelet, otomatik test ve ilk 8 görev eklendi
- 2026-11-27 · Ajan motoru değişti (insan + Claude, ajan çalışması değil) · Gemini CLI yerine `.github/ajan/ajan.py`; yedek iş akışı düzeltildi ve ilk yedek alındı
- 2026-11-28 · G-001: Testler için örnek fiyat verisi · Öneri açıldı (ajan: gemini-flash-latest, 4 istek). G-001 tamamlandı: Örnek fiyat verisi fikstürleri ve yardımcı fonksiyon eklendi.
- 2026-11-28 · G-002: Basit ve üstel hareketli ortalama (SMA, EMA) · Öneri açıldı (ajan: gemini-flash-latest, gemini-flash-lite-latest, 4 istek). G-002: Basit ve üstel hareketli ortalama (SMA, EMA) · Öneri açıldı
- 2026-11-28 · G-003: RSI göstergesi · Öneri açıldı (ajan: gemini-flash-lite-latest, 4 istek)
- 2026-11-28 · G-004: Tek varlık backtest motoru (maliyetsiz) · Öneri açıldı (ajan: gemini-flash-latest, gemini-flash-lite-latest, 4 istek)
- 2026-11-28 · G-005: İşlem maliyetleri · Öneri açıldı (ajan: gemini-flash-lite-latest, 4 istek)
- 2026-11-28 · G-021: İşlem maliyeti düzeltmesi (öneri #6'dan kalan eksikler) · Öneri açıldı (ajan: gemini-3-flash-preview, 4 istek). G-021: Başlangıç pozisyonu için işlem maliyeti eklendi ve pozisyon değişimi testleri tamamlandı.
- 2026-11-28 · G-006: Temel performans metrikleri · Öneri açıldı (ajan: gemini-3-flash-preview, 4 istek)
- 2026-11-28 · G-007: Hareketli ortalama kesişimi stratejisi · Öneri açıldı (ajan: gemini-flash-latest, 3 istek). G-007 tamamlandı: Hareketli ortalama kesişimi (ma_crossover_positions) stratejisi uygulandı.
- 2026-11-28 · G-008: Al-tut karşılaştırmalı Markdown rapor · Öneri açıldı (ajan: gemini-3-flash-preview, 6 istek)
- 2026-11-28 · G-009: Çekirdek varlık evreni · Öneri açıldı (ajan: gemini-3-flash-preview, 3 istek)
- 2026-11-28 · G-010: Veri indirme ve yerel önbellek · Öneri açıldı (ajan: gemini-flash-latest, 2 istek)
- 2026-11-28 · G-011: Bollinger bantları ve ATR · Öneri açıldı (ajan: gemini-3-flash-preview, 4 istek). G-011 tamamlandı: Bollinger Bantları ve ATR göstergeleri Wilder yöntemine uygun şekilde eklendi.
- 2026-11-28 · G-012: MACD göstergesi · Öneri açıldı (ajan: gemini-3-flash-preview, 3 istek)
- 2026-11-28 · G-022: RSI'da Wilder başlatması ve bilinen örnek testi · Öneri açıldı (ajan: gemini-3-flash-preview, 4 istek). G-022 tamamlandı: RSI göstergesi Wilder yöntemiyle (SMA başlatmalı) hesaplanacak şekilde güncellendi ve klasik örnekle doğrulandı.
- 2026-11-28 · G-013: RSI ortalamaya dönüş stratejisi · Öneri açıldı (ajan: gemini-3-flash-preview, 3 istek)
- 2026-11-28 · G-014: 12-1 momentum stratejisi · Öneri açıldı (ajan: gemini-flash-latest, 0 istek)
- 2026-11-28 · G-015: Bollinger kırılım stratejisi · Öneri açıldı (ajan: gemini-flash-latest, 0 istek)
- 2026-11-28 · G-016: MACD stratejisi · Öneri açıldı (ajan: gemini-flash-latest, gemini-3-flash-preview, 4 istek). G-016 tamamlandı: MACD sinyal kesiőimine dayalı strateji (macd_positions) eklendi.
- 2026-11-28 · G-017: İşlem sayısı ve isabet oranı · Öneri açıldı (ajan: gemini-3-flash-preview, 4 istek)
