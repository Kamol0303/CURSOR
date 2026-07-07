# TMB Validatsiya Auditi — Hisobot

Auditi sanasi: 2026-06-20  
Qamrov: frontend, backend API, RBAC, fayl yuklash, o'qituvchi portali

## Xulosa

Asosiy foydalanuvchi xatolari (PDF/Excel yuklab olish, o'qituvchi dars boshlash) **kritik validatsiya/ruxsat bo'shliqlari** bilan bog'liq edi. Ushbu PR kritik va o'rta darajadagi muammolarni bartaraf etadi.

---

## Topilgan muammolar va tuzatishlar

| # | Fayl/Endpoint | Muammo | Xavf | Tavsiya / Holat |
|---|---------------|--------|------|-----------------|
| 1 | `certificates/page.tsx` → `GET /reports/ratings` | `res.ok` tekshirilmagan; 403 JSON xato `.pdf` sifatida saqlanadi | **Kritik** | ✅ `downloadRatingsReport` + xato UI |
| 2 | `permissions.py` — `center_admin` | `reports.generate` yo'q, lekin UI tugmalari ko'rinadi | **Kritik** | ✅ Ruxsat qo'shildi |
| 3 | `lesson_generation_service.py` — `list_teacher_subjects` | Faqat guruh fanlari; `teacher_subjects` e'tiborsiz | **Kritik** | ✅ Union qilindi |
| 4 | `lesson_generation_service.py` — `generate` | Har qanday `subject_id` qabul qilinadi | **Kritik** | ✅ `SUBJECT_NOT_ASSIGNED` tekshiruvi |
| 5 | `lesson_generation_service.py` — `start` | `started` holat qayta boshlanishi mumkin | **O'rta** | ✅ Faqat `draft` ruxsat |
| 6 | `lesson_materials.py` schema | `locale` cheklanmagan | **O'rta** | ✅ `^(uz\|ru\|en)$` pattern |
| 7 | `lesson-start/page.tsx` | Bo'sh fanlar va API xatolari ko'rsatilmaydi | **O'rta** | ✅ i18n xabarlar |
| 8 | Frontend formlar (umumiy) | `zod`/`react-hook-form` o'rnatilgan, ishlatilmaydi | **O'rta** | ⏳ Keyingi bosqich |
| 9 | `file_service.py` | MIME faqat client header | **O'rta** | ⏳ Magic-byte validatsiya |
| 10 | `lesson_materials` DB | RLS yo'q | **O'rta** | ⏳ Migration kerak |
| 11 | XSS (xabarlar) | Chiqishda sanitizatsiya | **O'rta** | ⏳ React default escape; backend review |
| 12 | Payme/Click webhook | HMAC/replay | **Kritik** | ✅ Mavjud testlar (`test_payment_webhooks.py`) |

---

## Defense in depth (tuzatishdan keyin)

| Qatlam | PDF/Excel export | O'qituvchi fanlari | Dars yaratish |
|--------|------------------|-------------------|---------------|
| Frontend | `PermissionGate` + content-type tekshiruvi + i18n xato | Bo'sh ro'yxat xabari, `maxLength` | Form `required`, locale yuboriladi |
| Backend | `requires_permission("reports.generate")` | `teacher_subjects` ∪ guruh fanlari | `SUBJECT_NOT_ASSIGNED`, group mismatch |
| DB | — | `teacher_subjects` FK | `lesson_materials.status` |

---

## Migratsiya strategiyasi

- **Eski telefon formatlari**: hozircha o'zgartirilmadi; qat'iylashtirish mavjud ma'lumotlarni rad etmasligi kerak.
- **center_admin + reports.generate**: markaz menejeri sertifikatlar sahifasida reyting eksportini ishlatishi mumkin; moliyaviy ma'lumotlar alohida endpoint orqali cheklangan.

---

## Keyingi qadam

TaMoR v4.0 red-team checklist'iga **Validatsiya** bo'limi qo'shish:
- [ ] Barcha formalar uchun schema validatsiya (Zod)
- [ ] Fayl yuklash magic-byte
- [ ] `lesson_materials` RLS
- [ ] IDOR regression testlari
- [ ] Double-submit / idempotency
