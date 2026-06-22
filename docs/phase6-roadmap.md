# Phase 6 — Operatsion platforma kengaytmasi

## Yetkazildi (bu bosqich)

- Guruhlar API + UI (yaratish, ro'yxat, fan biriktirish)
- Davomat: qo'lda belgilash + QR sessiya
- To'lovlar: asosiy CRUD (Click/Payme keyinroq)
- O'quvchilar: frontend CRUD (rol bo'yicha)
- RBAC kengaytirildi: `groups.*`, `attendance.*`, `payments.*`
- O'qituvchi: o'quvchi qo'shish/tahrirlash
- Navigatsiya faqat ruxsat bo'yicha ko'rinadi

## Migration

`007_phase6` — groups maydonlari, `attendance_*`, `student_payments`

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging exec backend alembic upgrade head
```

## Keyingi prioritetlar

1. Guruhga o'quvchi biriktirish UI
2. Click / Payme adapterlar
3. Face ID (har bir markaz mobil qurilmasi)
4. O'qituvchi profili: maosh, jadval, reyting
5. Baholar va sertifikat avtogeneratsiya bog'lanishi
6. Excel/PDF hisobotlar (davomat, to'lov)
