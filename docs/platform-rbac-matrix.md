# TMB — Rol va amallar matritsasi (RBAC)

> Har bir kasb faqat o'z vakolati doirasida CRUD amallarini bajaradi.

## Rol nomlari

| Sizning nom | Tizimdagi kod | Vazifa |
|-------------|---------------|--------|
| Super Admin | `super_admin` | Tizim, barcha markazlar, sozlamalar |
| Hokimiyat operatori | `hokimiyat_operator` | Tuman monitoringi (faqat ko'rish + hisobot) |
| Direktor | `center_director` | Markaz boshqaruvi, hujjatlar, o'qituvchilar |
| Menejer | `center_admin` | Kundalik operatsiya: o'quvchi, guruh, davomat |
| O'qituvchi | `teacher` | O'z guruhidagi o'quvchilar, davomat |
| Auditor | `auditor` | Tekshiruv, PINFL ochish (audit bilan) |

## Modul bo'yicha ruxsatlar

| Modul | Super Admin | Hokimiyat | Direktor | Menejer | O'qituvchi |
|-------|:-----------:|:---------:|:--------:|:-------:|:----------:|
| Markazlar CRUD | ✅ to'liq | 👁 o'qish | ✏️ yangilash | 👁 | — |
| O'quvchilar | ✅ | 👁 | ✅ CRUD | ✅ qo'shish/tahrir | ✅ qo'shish/tahrir |
| O'qituvchilar | ✅ | 👁 | ✅ CRUD | 👁 | — |
| Guruhlar | ✅ | 👁 | ✅ | ✅ | 👁 |
| Davomat | ✅ | 👁 | ✅ | ✅ | ✅ belgilash |
| To'lovlar | ✅ | 👁 | ✅ | ✅ kiritish | — |
| Reyting | ✅ | 👁 | 👁 | 👁 | 👁 |
| Sertifikat | ✅ | — | ✅ | — | — |
| AI tahlil | ✅ | 👁 | 👁 | — | — |

## Keyingi bosqichlar (reja)

- [ ] Click / Payme to'lov webhook
- [ ] Face ID davomat (mobil SDK)
- [ ] O'qituvchi maosh va dars jadvali
- [ ] Pasport/rasm yuklash (fayl saqlash)
- [ ] Baholar moduli
- [ ] Push bildirishnomalar (PWA)

Batafsil texnik rejа: `docs/phase6-roadmap.md`
