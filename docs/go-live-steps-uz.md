# TMB — Go-Live Qadamlari (O'zbekcha)

> Toyloq tumani Ta'lim Monitoringi Boshqaruvi tizimini ishga tushirish tartibi.

## Kimlar uchun

- **Tuman IT** — server, TLS, Vault, backup
- **Platforma admin** — demo tozalash, tekshiruv, foydalanuvchilar
- **Xavfsizlik** — pentest va red-team ro'yxati

## 1. Infratuzilma (tashqi — kod tashqarida)

| # | Vazifa | Holat |
|---|--------|-------|
| 1 | O'zbekistonda joylashgan server/VPS | ☐ |
| 2 | DNS: `tamor.toyloq.uz` → Nginx | ☐ |
| 3 | CA imzolangan TLS (`infra/nginx/tls/`) | ☐ |
| 4 | HashiCorp Vault (`secret/tmb/prod/`) | ☐ |
| 5 | PostgreSQL 15 + Redis 7 (ichki tarmoq) | ☐ |

Batafsil: `docs/go-live-runbook.md`

## 2. Konfiguratsiya

```bash
cp .env.production.example .env.production
# Barcha CHANGE_ME qiymatlarni to'ldiring — hech qachon git ga commit qilmang
```

Majburiy:

- `ENVIRONMENT=production`
- `DEBUG=false`
- `SECRETS_BACKEND=vault`
- `POSTGRES_PASSWORD` — `DATABASE_URL` bilan mos
- `CORS_ORIGINS=["https://tamor.toyloq.uz"]`

## 3. Avtomatik go-live (Linux server — tavsiya)

```bash
chmod +x scripts/go-live.sh scripts/verify-prod.sh scripts/purge-demo-data.sh scripts/pre-deploy-check.sh
./scripts/go-live.sh
```

Skript ketma-ketligi: build → dry-run purge → tasdiqlash → purge → pre-deploy → verify.

## 4. Windows da tayyorgarlik (lokal test)

```cmd
scripts\windows\go-live-prep.cmd
```

Bu skript: Docker tekshiruvi → prod compose up → dry-run purge → `pre_deploy_check.py`.

**Eslatma:** haqiqiy trafik almashinuvi production Linux serverda amalga oshiriladi.

## 5. Demo ma'lumotlarni tozalash

```bash
# Avval dry-run
./scripts/purge-demo-data.sh --i-understand-this-deletes-demo-data --dry-run

# Keyin bajarish (faqat production)
./scripts/purge-demo-data.sh --i-understand-this-deletes-demo-data
```

Staging test: konteyner ichida `--allow-non-production` qo'shing.

Tozalanadigan jadvallar: foydalanuvchilar, markazlar, talabalar, o'qituvchilar, sertifikatlar, imtihonlar, baholar, to'lovlar, davomat, kurslar, xabarlar, fayllar va bog'liq audit yozuvlari.

## 6. Pre-deploy gate

```bash
./scripts/pre-deploy-check.sh
```

Chiqish kodi `0` bo'lishi shart — aks holda trafik yo'naltirmang.

## 7. Deploy

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

Production frontend: `frontend/Dockerfile.prod` (Next.js standalone, `npm run build`).

## 8. Post-deploy tekshiruv

```bash
PUBLIC_HOST=tamor.toyloq.uz ./scripts/verify-prod.sh
```

Qo'lda:

- [ ] `super_admin` bilan kirish (MFA majburiy)
- [ ] Sertifikat QR tekshiruvi
- [ ] Ota-ona OTP SMS (eskiz.uz)
- [ ] Celery beat reyting vazifasi
- [ ] Backup/restore drill
- [ ] `docs/red-team-checklist.md` imzolash

## 9. Rollback

```bash
docker compose -f docker-compose.prod.yml down
# PostgreSQL snapshot dan tiklash: scripts/restore_postgres.sh
```

## Hokimiyat operatori

`hokimiyat_operator` roli faqat monitoring paneliga kiradi (6 ta menyu: bosh sahifa, markazlar, o'qituvchilar, talabalar, sertifikatlar, analitika). Batafsil: `docs/rbac-role-page-matrix.md`.

## Yordamchi skriptlar

| Skript | Maqsad |
|--------|--------|
| `scripts/windows/update-main.cmd` | Dev muhit yangilash |
| `scripts/windows/show-credentials.cmd` | Demo loginlar |
| `scripts/windows/go-live-prep.cmd` | Prod tayyorgarlik (Windows) |
| `scripts/go-live.sh` | To'liq go-live (Linux) |
