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

## So'nggi o'zgarishlar (2026-yil iyul)

| O'zgarish | Tafsilot |
|-----------|----------|
| **Uch tilli README** | `README.md`, `README.uz.md`, `README.ru.md` — Windows, macOS, Linux dev, Linux production buyruqlari |
| **`scripts/linux-dev-setup.sh`** | Kali/Ubuntu/Debian: prod/staging to'xtatish, port tekshiruvi, dev ishga tushirish |
| **PostgreSQL dev porti** | Host port **5433** (5432 emas) — boshqa Docker/tizim PostgreSQL bilan ziddiyatni oldini oladi |
| **Alembic tuzatish** | `015_lesson_materials` zanjiri to'g'rilandi (`014_certificate_file`); test: `backend/tests/test_alembic_chain.py` |
| **Muammolarni bartaraf etish** | Windows vs Linux buyruqlari, production `backend unhealthy`, 5432 port, orphan konteynerlar |
| **Brauzer** | `http://localhost:3000` — Docker ishlayotgan **shu kompyuterda**; Cursor preview ishlamaydi; Linuxda brauzerni **root** emas, oddiy foydalanuvchi ochsin |

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

Platformangiz uchun **bitta** bo'limni tanlang. Har bir blok to'liq — boshqa OS bo'limlarini o'qishingiz shart emas.

| Platforma | Bo'lim |
|----------|--------|
| Windows (dev) | [§1 Windows — development](#1-windows--development-toliq) |
| Windows (staging) | [§2 Windows — staging](#2-windows--staging) |
| Windows (prod test) | [§3 Windows — production prep](#3-windows--production-prep) |
| macOS (dev) | [§4 macOS — development](#4-macos--development-toliq) |
| macOS (staging) | [§5 macOS — staging](#5-macos--staging) |
| Linux Kali/Ubuntu (dev) | [§6 Linux — development](#6-linux-kaliubuntudebian--development-toliq) |
| Linux (staging) | [§7 Linux — staging](#7-linux--staging) |
| Linux VPS (production) | [§8 Linux server — production](#8-linux-server--production-toliq) |

---

### 1. Windows — development (to'liq)

**Talablar:** Windows 10/11, [Docker Desktop](https://www.docker.com/products/docker-desktop/), Git for Windows, PowerShell yoki CMD.

**1-qadam — Docker Desktop o'rnatish**

1. Docker Desktop ni o'rnating va so'ralsa qayta ishga tushiring.
2. Start menyudan Docker Desktop ni oching.
3. Traydagi balina belgisi yashil bo'lguncha kuting (2–3 daqiqa).
4. Tekshiring:

```cmd
docker info
docker compose version
```

**2-qadam — Loyihani klonlash**

```cmd
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**3-qadam — Muhit fayli**

```cmd
copy .env.example .env
scripts\windows\setup-llm-env.cmd
```

(Ixtiyoriy) `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY` uchun `.env` ni Notepad da tahrirlang.

**4-qadam — Dev stackni ishga tushirish** (git pull, Docker build, migratsiya, seed)

```cmd
scripts\windows\update-main.cmd
```

**5-qadam — Tekshirish**

```cmd
docker compose ps
curl -s http://localhost:8000/health
```

Kutilgan health javobi: `{"status":"ok","environment":"development"}`

**6-qadam — Brauzerda ochish**

**Shu kompyuterda** oching: http://localhost:3000

Dev loginlar mahalliy ko'rsatiladi (README da emas):

```cmd
scripts\windows\show-credentials.cmd
```

**URL lar (Windows dev)**

| Xizmat | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API hujjatlari | http://localhost:8000/docs |
| PostgreSQL (host) | `localhost:5433` |

**To'xtatish / qayta ishga tushirish (Windows dev)**

```cmd
docker compose down
docker compose down -v
scripts\windows\update-main.cmd
scripts\windows\backend-logs.cmd
```

> **Docker xatosi?** Docker Desktop ni oching va traydagi balina yashil bo'lguncha kuting, keyin `scripts\windows\update-main.cmd` ni qayta ishga tushiring.

---

### 2. Windows — staging

Nginx + TLS bilan mahalliy HTTPS staging.

```cmd
cd CURSOR
scripts\windows\setup-staging-env.cmd
bash infra/nginx/generate-dev-certs.sh
scripts\windows\staging-up.cmd
```

`C:\Windows\System32\drivers\etc\hosts` ga qo'shing (Administrator sifatida):

```
127.0.0.1 tamor.staging.local
```

Oching: https://tamor.staging.local

Loglar: `scripts\windows\backend-logs.cmd staging`

To'xtatish:

```cmd
docker compose -f docker-compose.staging.yml --env-file .env.staging down
```

---

### 3. Windows — production prep

Faqat mahalliy production build testi. Haqiqiy production **Linux serverda** ishlaydi (§8).

```cmd
cd CURSOR
copy .env.production.example .env.production
REM Edit .env.production — fill ALL CHANGE_ME values
scripts\windows\go-live-prep.cmd
scripts\windows\verify-prod-build.cmd
```

To'xtatish:

```cmd
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

---

### 4. macOS — development (to'liq)

**Talablar:** macOS 12+, [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/), Git (Xcode CLI yoki Homebrew).

**1-qadam — Docker o'rnatish**

```bash
docker --version
docker compose version
docker info
```

Agar `docker info` xato bersa, Docker Desktop ni oching.

**2-qadam — Klonlash**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**3-qadam — Muhit**

```bash
cp .env.example .env
nano .env
```

Ixtiyoriy AI kalitlari: `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`, `AI_ENABLED=true`.

**4-qadam — Ishga tushirish (tavsiya etiladi)**

```bash
chmod +x scripts/start.sh scripts/restart-fresh.sh
./scripts/start.sh dev
```

**4-qadam (muqobil) — Qo'lda ishga tushirish**

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

**5-qadam — Tekshirish**

```bash
docker compose ps
curl -s http://localhost:8000/health
curl -s http://localhost:3000 | head -5
```

**6-qadam — Brauzerda ochish**

```bash
open http://localhost:3000
```

Dev hisob ma'lumotlari seeddan keyin terminalda chiqadi (README da emas).

**URL lar (macOS dev)**

| Xizmat | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API hujjatlari | http://localhost:8000/docs |
| PostgreSQL (host) | `localhost:5433` |

**To'xtatish / qayta ishga tushirish (macOS dev)**

```bash
docker compose down
docker compose down -v
./scripts/restart-fresh.sh dev
docker compose logs backend --tail 80
./scripts/show-mfa-qr.sh
```

---

### 5. macOS — staging

```bash
cd CURSOR
chmod +x scripts/start.sh
./scripts/start.sh staging
sudo sh -c 'echo "127.0.0.1 tamor.staging.local" >> /etc/hosts'
open https://tamor.staging.local
./scripts/verify-staging.sh
```

To'xtatish:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging down
```

---

### 6. Linux (Kali/Ubuntu/Debian) — development (to'liq)

**Talablar:** Kali, Ubuntu 22.04+ yoki Debian 12+. Docker Engine + Compose plugin + Git.

**1-qadam — Docker o'rnatish** (mashinada bir marta)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git curl
sudo usermod -aG docker $USER
```

Chiqib qayta kiring (yoki `newgrp docker`), keyin tekshiring:

```bash
docker info
docker compose version
```

> Linuxda `copy` yoki `scripts\windows\...` ishlatmang — ular faqat Windows uchun.

**2-qadam — Klonlash**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

Kerak bo'lsa to'liq yo'lni ishlating, masalan `/home/YOUR_USER/CURSOR` (`/root/CURSOR` emas, agar doim root sifatida ishlamasangiz).

**3-qadam — Muhit**

```bash
cp .env.example .env
nano .env
```

Ixtiyoriy: `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`.

**4-qadam — Ishga tushirish (tavsiya etiladi)**

```bash
chmod +x scripts/linux-dev-setup.sh scripts/start.sh
./scripts/linux-dev-setup.sh
```

Bu skript: prod/staging ziddiyatlarini to'xtatadi, 5432/5433/6379 portlarini bo'shatadi, `.env` yaratadi, dev ni ishga tushiradi.

**4-qadam (muqobil) — Qo'lda ishga tushirish**

```bash
docker compose down --remove-orphans 2>/dev/null || true
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

**5-qadam — Tekshirish**

```bash
docker compose ps
curl -s http://localhost:8000/health
curl -s http://localhost:3000 | head -5
```

**6-qadam — Brauzerda ochish**

**Shu mashinada** oching: http://localhost:3000

Firefox/Chrome ni `root` sifatida ishga tushirmang. Oddiy foydalanuvchingizdan foydalaning:

```bash
exit
firefox http://localhost:3000 &
```

Yoki root shell dan:

```bash
su - YOUR_USER -c "firefox http://localhost:3000 &"
```

Dev hisob ma'lumotlari seeddan keyin terminalda chiqadi (README da emas).

**URL lar (Linux dev)**

| Xizmat | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API hujjatlari | http://localhost:8000/docs |
| PostgreSQL (host) | `localhost:5433` |

**To'xtatish / qayta ishga tushirish (Linux dev)**

```bash
docker compose down
docker compose down -v
./scripts/linux-dev-setup.sh
docker compose logs backend --tail 80
```

**5432 port ziddiyati?**

Dev host port **5433** dan foydalanadi. Agar ishga tushirish yana muvaffaqiyatsiz bo'lsa:

```bash
docker ps --format '{{.Names}} {{.Ports}}' | grep 5432
docker stop CONTAINER_NAME
sudo systemctl stop postgresql
./scripts/linux-dev-setup.sh
```

---

### 7. Linux — staging

```bash
cd CURSOR
cp .env.staging.example .env.staging
nano .env.staging
bash infra/nginx/generate-dev-certs.sh
chmod +x scripts/start.sh scripts/verify-staging.sh
./scripts/start.sh staging
echo "127.0.0.1 tamor.staging.local" | sudo tee -a /etc/hosts
./scripts/verify-staging.sh
```

Oching: https://tamor.staging.local

To'xtatish:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging down
```

---

### 8. Linux server — production (to'liq)

**Talablar:** O'zbekistondagi Ubuntu/Debian VPS, Docker Engine, domen (masalan, `tamor.toyloq.uz`), CA TLS sertifikatlari, HashiCorp Vault.

**Mahalliy noutbuklar uchun emas** — Kali/Ubuntu dev uchun §6 dan foydalaning.

**1-qadam — Serverda klonlash**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**2-qadam — Production maxfiy kalitlari**

```bash
cp .env.production.example .env.production
nano .env.production
```

Barcha `CHANGE_ME` qiymatlarini to'ldiring:

- `POSTGRES_PASSWORD`, `DATABASE_URL`
- `VAULT_ADDR`, `VAULT_TOKEN`
- `TOTP_ENCRYPTION_KEY`, `PINFL_ENCRYPTION_KEY` (32+ belgi)
- `CLICK_*`, `PAYME_*` to'lov kalitlari
- `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`

**3-qadam — TLS sertifikatlari (CA imzolangan)**

```bash
ls -la infra/nginx/tls/fullchain.pem infra/nginx/tls/privkey.pem
```

CA imzolangan fayllarni joylashtiring (production uchun `generate-dev-certs.sh` emas):

- `infra/nginx/tls/fullchain.pem`
- `infra/nginx/tls/privkey.pem`

**4-qadam — Go live**

```bash
chmod +x scripts/go-live.sh scripts/verify-prod.sh
./scripts/go-live.sh
```

Interaktiv bo'lmagan demo tozalash:

```bash
GO_LIVE_PURGE=yes ./scripts/go-live.sh
```

**5-qadam — Tekshirish**

```bash
PUBLIC_HOST=tamor.toyloq.uz ./scripts/verify-prod.sh
python3 scripts/red_team_verify.py --url https://tamor.toyloq.uz --production
curl -fsS https://tamor.toyloq.uz/health
```

**Production boshqaruvi**

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f backend
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

**Serverda production staging**

```bash
cp .env.staging.example .env.staging
nano .env.staging
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
docker stop some-postgres
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

### Alembic `KeyError: '014_certificate_file_id'`

Oxirgi `main` ni oling (migratsiya zanjiri tuzatildi), keyin dev bazani qayta yarating:

```bash
git pull origin main
docker compose down -v
./scripts/linux-dev-setup.sh
```

### Brauzerda ochish

- Manzil: **http://localhost:3000** (Docker ishlayotgan shu kompyuterda)
- Tekshiruv: `curl -s http://localhost:8000/health` → `{"status":"ok",...}`
- Cursor/Cloud preview URL lari mahalliy Docker ga **ulanmaydi**
- Linux/Kali: brauzerni **root** emas, oddiy foydalanuvchi (`xushnud`) ochsin:

```bash
exit
firefox http://localhost:3000 &
# yoki root dan:
su - xushnud -c "firefox http://localhost:3000 &"
```

---

## Development kirish

`seed_demo_users.py` (yoki `update-main.cmd` / `linux-dev-setup.sh`) dan keyin loginlar **faqat mahalliy terminalda** chiqadi:

| Platforma | Buyruq |
|-----------|--------|
| Windows | `scripts\windows\show-credentials.cmd` |
| Linux/macOS | `./scripts/start.sh dev` yoki `./scripts/linux-dev-setup.sh` chiqishi |

Login va parollar **xavfsizlik uchun README da ko'rsatilmaydi**. Faqat mahalliy/staging muhitda ishlating.

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
