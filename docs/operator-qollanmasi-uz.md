# Hokimiyat operatori qo'llanmasi (UZ)

Bu hujjat `hokimiyat_operator` roli uchun TMB tizimidan foydalanish bo'yicha amaliy qo'llanmadir.

## 1. Kirish

1. Brauzerda tizim manzilini oching (masalan: `http://localhost:3000` yoki staging URL).
2. **Login:** `operator.hokimiyat`
3. **Parol:** seed chiqishidagi parol (demo: `Hokim#Op2026!`).
4. Birinchi kirishda **MFA (Authenticator)** sozlash talab qilinadi — Google Authenticator yoki shunga o'xshash ilovada QR kodni skanerlang.

## 2. Bosh panel (Dashboard)

- **Jami filiallar** — tuman bo'yicha ro'yxatdan o'tgan markazlar soni.
- **Faol o'quvchilar** — joriy davrda faol ro'yxatdan o'tganlar.
- **Oylik ro'yxatdan o'tishlar** — so'nggi oy dinamikasi.
- **Litsenziya muddati tugayotgan markazlar** — 30 kun ichida tekshiruv talab qilinadiganlar.

Operator faqat **ko'rish** huquqiga ega — ma'lumot qo'shish yoki o'chirish mumkin emas.

## 3. Monitoring bo'limlari

| Bo'lim | Yo'l | Vazifa |
|--------|------|--------|
| Markazlar | `/dashboard/centers` | Filiallar ro'yxati, STIR, direktor |
| O'quvchilar | `/dashboard/students` | Umumiy statistika (PINFL yashirin) |
| O'qituvchilar | `/dashboard/teachers` | Kadrlar monitoringi |
| Guruhlar | `/dashboard/groups` | Guruhlar va to'ldirilganlik |
| Davomat | `/dashboard/attendance` | Davomat ko'rsatkichlari |
| To'lovlar | `/dashboard/payments` | Moliyaviy holat (faqat ko'rish) |

## 4. Reyting va AI tahlil

- **Reyting** (`/dashboard/ratings`) — markazlar reytingi, o'sish/tushish dinamikasi.
- **AI tahlil** (`/dashboard/analytics`) — bashoratlar va ta'lim bo'shliqlari indeksi.

## 5. Hisobotlar

- `reports.generate` huquqi orqali PDF/Excel hisobotlar eksport qilinadi (API orqali).
- Hisobotlarni faqat rasmiy maqsadlarda tarqatish kerak.

## 6. Tillar

Yuqori o'ng burchakdagi til tanlovi orqali **O'zbek**, **Русский**, **English** interfeysini almashtiring.

## 7. Xavfsizlik

- Parolni boshqalar bilan baham ko'rmang.
- Sessiyadan keyin **Chiqish** tugmasini bosing.
- MFA zaxira kodlarini xavfsiz joyda saqlang (Xavfsizlik bo'limi).
- Shubhali faollikni IT xavfsizlik guruhiga xabar bering.

## 8. Muammolarni bartaraf etish

| Belgilar | Yechim |
|----------|--------|
| 401 / chiqib ketish | Qayta login, MFA kodini tekshiring |
| MFA_INVALID | Vaqt sinxronizatsiyasini tekshiring, zaxira kod ishlating |
| Bo'sh dashboard | Markazlar hali kiritilmagan — ma'lumot kiritish markaz adminlari vazifasi |
| Sekin yuklanish | Tarmoqni tekshiring, brauzer keshini tozalang |

## 9. Tashqi API (statistika)

Hududiy statistika organlari uchun alohida API kalit beriladi:

```
GET /api/v1/external/aggregate-stats
Header: X-Api-Key: <kalit>
```

Kalit faqat o'qish uchun — shaxsiy ma'lumotlar qaytarilmaydi.

## 10. Aloqa

Texnik yordam: tizim administratori yoki `docs/go-live-runbook.md` dagi kontaktlar.
