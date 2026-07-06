# TMB — Ta'lim Monitoringi Boshqaruvi

**Tillar:** [English](README.md) · [O'zbek](README.uz.md) · [Русский](README.ru.md)

Samarqand viloyati, Toyloq tumani uchun davlat darajasidagi ta'lim monitoringi va boshqaruv platformasi.

---

## Yakuniy holat (2026-yil iyul)

| Soha | Tayyorlik | Izoh |
|------|-----------|------|
| **Ilova kodi** | **~100%** | 0–7 fazalar, OCMS, Hokimiyat paneli, AI, audit |
| **Xavfsizlik (avtomat)** | **12/12 o'tdi** | `python3 scripts/red_team_verify.py --offline` |
| **Go-live (infratuzilma)** | **~85%** | Vault, CA TLS, UZ server, tashqi pentest imzosi qoldi |

To'liq xavfsizlik hisoboti: [`docs/security-audit-report.md`](docs/security-audit-report.md)  
Go-live ro'yxati: [`docs/production-100-checklist-uz.md`](docs/production-100-checklist-uz.md)

---

## Asosiy imkoniyatlar

- **RBAC** — 10+ rol, PostgreSQL RLS, tenant izolyatsiyasi
- **Hokimiyat operatori** — faqat monitoring paneli (6 ta menyu)
- **Sertifikatlar** — QR tekshiruv, yaxlitlik xeshi, `/verify`
- **Sun'iy intellekt** — imtihon testlari + dars materiallari (prezentatsiya / sinf o'yini)
- **LLM zanjirlari** — BazaarLink → Gemini → Mistral (avtomatik zaxira)
- **Audit jurnali** — `/dashboard/audit` — kim, qachon, nima o'zgartirdi
- **Production** — `Dockerfile.prod`, `docker-compose.prod.yml`, Nginx TLS

---

## Xavfsizlik tekshiruvi

```bash
# Avtomatik red-team (server shart emas)
python3 scripts/red_team_verify.py --offline

# Staging / production
python3 scripts/red_team_verify.py --url https://tamor.toyloq.uz --production

# Integratsion testlar (PostgreSQL kerak)
cd backend && pytest tests/security/ -v
```

**So'nggi offline natija:** 12/12 avtomatik tekshiruv o'tdi.

**Production oldidan:** tashqi pentest imzosi (`docs/red-team-checklist.md`), CA TLS, Vault, demo ma'lumotlarni tozalash.

---

## Talablar

| Vosita | Windows | macOS | Linux server |
|--------|---------|-------|--------------|
| **Docker** | [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Docker Desktop for Mac | Docker Engine + Compose plugin |
| **Git** | Git for Windows | Xcode CLI yoki Homebrew `git` | `apt install git` / `dnf install git` |
| **Node.js 20+** | Ixtiyoriy (mahalliy frontend) | Ixtiyoriy | Ixtiyoriy |

---

## Ishga tushirish

### Windows (development)

**1. Repozitoriyani klonlash**

```cmd
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**2. Muhit fayli va LLM kalitlari**

```cmd
copy .env.example .env
scripts\windows\setup-llm-env.cmd
```

**3. To'liq dev stackni ishga tushirish** (`main` yangilanadi, Docker build, migratsiya, seed)

```cmd
scripts\windows\update-main.cmd
```

**4. Demo loginlarni ko'rsatish**

```cmd
scripts\windows\show-credentials.cmd
```

| URL | Manzil |
|-----|--------|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API hujjatlari | http://localhost:8000/docs |

**Windows — staging (HTTPS, mahalliy)**

```cmd
scripts\windows\setup-staging-env.cmd
bash infra/nginx/generate-dev-certs.sh
scripts\windows\staging-up.cmd
```

`C:\Windows\System32\drivers\etc\hosts` ga qo'shing: `127.0.0.1 tamor.staging.local`  
Brauzerda: https://tamor.staging.local

**Windows — foydali buyruqlar**

```cmd
scripts\windows\backend-logs.cmd              REM backend loglari (dev)
scripts\windows\backend-logs.cmd staging      REM backend loglari (staging)
docker compose down                           REM dev ni to'xtatish
docker compose down -v                        REM dev + bazani tozalash
docker compose logs backend --tail 80           REM so'nggi backend chiqishi
```

**Windows — production tayyorgarlik** (mahalliy prod build testi; haqiqiy prod Linuxda)

```cmd
copy .env.production.example .env.production
REM .env.production ni tahrirlang — barcha CHANGE_ME qiymatlarini to'ldiring
scripts\windows\go-live-prep.cmd
scripts\windows\verify-prod-build.cmd
```

> Agar `docker info` xato bersa: **Docker Desktop** ni Start menyudan oching va traydagi balina yashil bo'lguncha kuting (2–3 daqiqa).

---

### macOS (development)

**1. Klonlash va sozlash**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
cp .env.example .env
# .env ni tahrirlang — LLM_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY (ixtiyoriy)
```

**2. Bitta buyruq bilan ishga tushirish** (tavsiya etiladi)

```bash
chmod +x scripts/start.sh scripts/restart-fresh.sh
./scripts/start.sh dev
```

**3. Yoki qo'lda ishga tushirish**

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

| URL | Manzil |
|-----|--------|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API hujjatlari | http://localhost:8000/docs |

**macOS — staging (HTTPS, mahalliy)**

```bash
./scripts/start.sh staging
# /etc/hosts ga qo'shing: 127.0.0.1 tamor.staging.local
sudo sh -c 'echo "127.0.0.1 tamor.staging.local" >> /etc/hosts'
open https://tamor.staging.local
```

**macOS — foydali buyruqlar**

```bash
docker compose down                    # dev ni to'xtatish
docker compose down -v                 # to'xtatish + bazani tozalash
./scripts/restart-fresh.sh dev         # to'liq qayta ishga tushirish
docker compose logs backend --tail 80  # so'nggi backend chiqishi
./scripts/show-mfa-qr.sh               # admin.tmb uchun MFA QR
```

---

### Linux (development)

macOS bilan bir xil buyruqlar. Docker Engine va Compose plugin kerak:

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER   # chiqib qayta kiring
```

**Linux (Kali/Ubuntu) — eng oson yo'l:**

```bash
chmod +x scripts/linux-dev-setup.sh
./scripts/linux-dev-setup.sh
```

Bu skript production stackni to'xtatadi, port ziddiyatini tekshiradi va dev ni ishga tushiradi.

---

### Linux server (production)

Production VPS da ishga tushiriladi (masalan, `tamor.toyloq.uz`). `docker-compose.prod.yml` va `.env.production` ishlatiladi.

**1. Klonlash va maxfiy kalitlar**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
cp .env.production.example .env.production
nano .env.production   # BARCHA CHANGE_ME: DB parol, JWT secret, LLM kalitlari va h.k.
```

**2. CA imzolangan TLS sertifikatlari** (dev self-signed emas)

```bash
# CA sertifikatlarni joylashtiring:
#   infra/nginx/tls/fullchain.pem
#   infra/nginx/tls/privkey.pem
ls -la infra/nginx/tls/
```

**3. Go-live** (build, migratsiya, demo tozalash, pre-deploy, tekshiruv)

```bash
chmod +x scripts/go-live.sh scripts/verify-prod.sh
./scripts/go-live.sh
```

Interaktiv bo'lmagan tozalash (CI / avtomatlashtirish):

```bash
GO_LIVE_PURGE=yes ./scripts/go-live.sh
```

**4. Deploydan keyin tekshiruv**

```bash
PUBLIC_HOST=tamor.toyloq.uz ./scripts/verify-prod.sh
python3 scripts/red_team_verify.py --url https://tamor.toyloq.uz --production
```

**Linux server — production boshqaruvi**

```bash
# Holat
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# Loglar
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f backend

# Qayta ishga tushirish
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Yangilashdan keyin migratsiya
docker compose -f docker-compose.prod.yml --env-file .env.production \
  exec backend alembic upgrade head

# To'xtatish
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

**Linux server — staging**

```bash
cp .env.staging.example .env.staging
nano .env.staging
bash infra/nginx/generate-dev-certs.sh   # yoki staging host uchun haqiqiy sertifikat
./scripts/start.sh staging
./scripts/verify-staging.sh
```

---

### LLM sozlash (barcha platformalar)

`.env` (dev) yoki `.env.production` (prod) ga qo'shing. **Haqiqiy kalitlarni gitga commit qilmang!**

```env
LLM_API_KEY=sk-bl-...              # BazaarLink (asosiy)
GEMINI_API_KEY=...                 # zaxira 1
MISTRAL_API_KEY=...                # zaxira 2
AI_ENABLED=true
```

| Platforma | Yordamchi skript |
|-----------|------------------|
| Windows | `scripts\windows\setup-llm-env.cmd` |
| macOS / Linux | `.env` ni qo'lda tahrirlash |

`.env` o'zgargach, stackni qayta ishga tushiring:

```bash
docker compose up -d --build          # dev
# yoki
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build  # prod
```

---

## Muammolarni bartaraf etish

### Linuxda Windows buyruqlarini ishlatdingizmi?

**Linux/macOS** da `copy` emas, `cp` ishlating:

```bash
cp .env.example .env
./scripts/linux-dev-setup.sh    # Kali/Ubuntu/Debian uchun tavsiya
# yoki
./scripts/start.sh dev
```

Windows `.cmd` skriptlari (`scripts\windows\...`) **faqat Windows** da ishlaydi.

### Production da `backend is unhealthy`

Production uchun to'liq sozlangan `.env.production` kerak:

- Haqiqiy parollar (`CHANGE_ME_...` emas)
- **HashiCorp Vault** (`VAULT_ADDR` + `VAULT_TOKEN`)
- JWT kalitlar `/secrets/` da
- CA TLS sertifikatlar `infra/nginx/tls/` da
- To'lov kalitlari (`CLICK_*`, `PAYME_*`)

**Mahalliy kompyuterda (Kali, Ubuntu) dev rejimini ishlating, production emas:**

```bash
./scripts/linux-dev-setup.sh
```

Backend loglari:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs backend --tail 100
```

### `port 5432 is already allocated`

5432 port boshqa Docker konteyner yoki tizim PostgreSQL tomonidan band. **Dev rejim endi host port 5433** dan foydalanadi.

```bash
git pull origin main
./scripts/linux-dev-setup.sh
```

Agar yana xato bersa:

```bash
docker ps --format '{{.Names}} {{.Ports}}' | grep 5432
docker stop <konteyner_nomi>
./scripts/linux-dev-setup.sh
```

Hostdan DB: `postgresql://tamor:tamor_dev@localhost:5433/tamor`

### `orphan containers (cursor-nginx-1)`

Prod dan dev ga o'tganda:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production down --remove-orphans
docker compose down --remove-orphans
./scripts/start.sh dev
```

---

## Demo loginlar (faqat development)

| Rol | Login | Parol |
|-----|-------|-------|
| Super Admin | `admin.tmb` | `Tmb#2026Admin!` |
| Hokimiyat operatori | `operator.hokimiyat` | `Hokim#Op2026!` |
| Markaz admini | `admin.aspect` | `CenterAdmin#26!` |
| O'qituvchi | `teacher.dilnoza` | `Teach#Dil2026!` |
| O'quvchi | `student.sardor` | `Student#2026!` |

---

## Hujjatlar

| Hujjat | Maqsad |
|--------|--------|
| [`docs/threat-model.md`](docs/threat-model.md) | STRIDE tahdid modeli |
| [`docs/red-team-checklist.md`](docs/red-team-checklist.md) | 24A xavfsizlik ro'yxati |
| [`docs/go-live-runbook.md`](docs/go-live-runbook.md) | Production deploy |
| [`docs/security-audit-report.md`](docs/security-audit-report.md) | Audit natijalari |

---

## Litsenziya

Davlat loyihasi — Toyloq tumani hokimligi.
