# TMB — Education Monitoring & Management Platform

**Languages:** [English](README.md) · [O'zbek](README.uz.md) · [Русский](README.ru.md)

Government-grade education management and monitoring platform for **Toyloq District**, Samarkand Region, Uzbekistan.

---

## Final status (July 2026)

| Area | Readiness | Notes |
|------|-----------|-------|
| **Application code** | **~100%** | All phases 0–7, OCMS, Hokimiyat dashboard, AI, audit |
| **Security (automated)** | **12/12 passed** | `python3 scripts/red_team_verify.py --offline` |
| **Go-live (infrastructure)** | **~85%** | Vault, CA TLS, UZ VPS, external pentest sign-off remain |

Full security report: [`docs/security-audit-report.md`](docs/security-audit-report.md)  
Go-live checklist: [`docs/production-100-checklist-uz.md`](docs/production-100-checklist-uz.md)

---

## Recent changes (July 2026)

| Change | Details |
|--------|---------|
| **Trilingual README** | `README.md`, `README.uz.md`, `README.ru.md` — run commands for Windows, macOS, Linux dev, Linux production |
| **`scripts/linux-dev-setup.sh`** | Kali/Ubuntu/Debian: stops prod/staging conflicts, checks ports, starts dev |
| **PostgreSQL dev port** | Host port **5433** (not 5432) — avoids conflict with other Docker/system PostgreSQL |
| **Alembic fix** | Migration `015_lesson_materials` chain corrected (`014_certificate_file`); test: `backend/tests/test_alembic_chain.py` |
| **Troubleshooting** | Windows vs Linux commands, production `backend unhealthy`, port 5432, orphan containers |
| **Browser access** | Open `http://localhost:3000` on the **same machine** where Docker runs — not Cursor cloud preview; do not run browser as **root** on Linux |

---

## Key features

- **RBAC** — 10+ roles, PostgreSQL RLS, tenant isolation
- **Hokimiyat operator** — monitoring-only dashboard (6 menu items)
- **Certificates** — QR verify, integrity hash, public `/verify`
- **AI** — exam generator + teacher lesson materials (presentation / classroom game)
- **LLM providers** — BazaarLink → Gemini → Mistral (automatic fallback)
- **Audit log** — `/dashboard/audit` — who changed what and when
- **Production stack** — `Dockerfile.prod`, `docker-compose.prod.yml`, Nginx TLS

---

## Security verification

```bash
# Automated red-team (offline — no server required)
python3 scripts/red_team_verify.py --offline

# Against staging/production
python3 scripts/red_team_verify.py --url https://tamor.toyloq.uz --production

# Integration security tests (PostgreSQL required)
cd backend && pytest tests/security/ -v
```

**Latest offline result:** 12/12 automated checks passed (see `docs/security-audit-report.md`).

**Still required before production:** external penetration test sign-off (`docs/red-team-checklist.md`), CA TLS, Vault secrets, demo data purge on prod host.

---

## Prerequisites

| Tool | Windows | macOS | Linux server |
|------|---------|-------|--------------|
| **Docker** | [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Docker Desktop for Mac | Docker Engine + Compose plugin |
| **Git** | Git for Windows | Xcode CLI or Homebrew `git` | `apt install git` / `dnf install git` |
| **Node.js 20+** | Optional (local frontend dev) | Optional | Optional |

---

## How to run

Choose **one** section for your platform. Each block is complete — you do not need to read other OS sections.

| Platform | Section |
|----------|---------|
| Windows (dev) | [§1 Windows — development](#1-windows--development-full) |
| Windows (staging) | [§2 Windows — staging](#2-windows--staging) |
| Windows (prod test) | [§3 Windows — production prep](#3-windows--production-prep) |
| macOS (dev) | [§4 macOS — development](#4-macos--development-full) |
| macOS (staging) | [§5 macOS — staging](#5-macos--staging) |
| Linux Kali/Ubuntu (dev) | [§6 Linux — development](#6-linux-kaliubuntudebian--development-full) |
| Linux (staging) | [§7 Linux — staging](#7-linux--staging) |
| Linux VPS (production) | [§8 Linux server — production](#8-linux-server--production-full) |

---

### 1. Windows — development (full)

**Requirements:** Windows 10/11, [Docker Desktop](https://www.docker.com/products/docker-desktop/), Git for Windows, PowerShell or CMD.

**Step 1 — Install Docker Desktop**

1. Install Docker Desktop and restart if prompted.
2. Open Docker Desktop from the Start menu.
3. Wait until the tray whale icon is green (2–3 minutes).
4. Verify:

```cmd
docker info
docker compose version
```

**Step 2 — Clone the project**

```cmd
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**Step 3 — Environment file**

```cmd
copy .env.example .env
scripts\windows\setup-llm-env.cmd
```

(Optional) Edit `.env` in Notepad for `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`.

**Step 4 — Start dev stack** (git pull, Docker build, migrations, seed)

```cmd
scripts\windows\update-main.cmd
```

**Step 5 — Verify**

```cmd
docker compose ps
curl -s http://localhost:8000/health
```

Expected health response: `{"status":"ok","environment":"development"}`

**Step 6 — Open in browser**

Open **on this PC**: http://localhost:3000

Dev logins are shown locally (not in README):

```cmd
scripts\windows\show-credentials.cmd
```

**URLs (Windows dev)**

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| PostgreSQL (host) | `localhost:5433` |

**Stop / restart (Windows dev)**

```cmd
docker compose down
docker compose down -v
scripts\windows\update-main.cmd
scripts\windows\backend-logs.cmd
```

> **Docker error?** Start Docker Desktop and wait for the green whale icon, then run `scripts\windows\update-main.cmd` again.

---

### 2. Windows — staging

HTTPS local staging with Nginx + TLS.

```cmd
cd CURSOR
scripts\windows\setup-staging-env.cmd
bash infra/nginx/generate-dev-certs.sh
scripts\windows\staging-up.cmd
```

Add to `C:\Windows\System32\drivers\etc\hosts` (as Administrator):

```
127.0.0.1 tamor.staging.local
```

Open: https://tamor.staging.local

Logs: `scripts\windows\backend-logs.cmd staging`

Stop:

```cmd
docker compose -f docker-compose.staging.yml --env-file .env.staging down
```

---

### 3. Windows — production prep

Local production build test only. Real production runs on a **Linux server** (§8).

```cmd
cd CURSOR
copy .env.production.example .env.production
REM Edit .env.production — fill ALL CHANGE_ME values
scripts\windows\go-live-prep.cmd
scripts\windows\verify-prod-build.cmd
```

Stop:

```cmd
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

---

### 4. macOS — development (full)

**Requirements:** macOS 12+, [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/), Git (Xcode CLI or Homebrew).

**Step 1 — Install Docker**

```bash
docker --version
docker compose version
docker info
```

Open Docker Desktop if `docker info` fails.

**Step 2 — Clone**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**Step 3 — Environment**

```bash
cp .env.example .env
nano .env
```

Set optional AI keys: `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`, `AI_ENABLED=true`.

**Step 4 — Start (recommended)**

```bash
chmod +x scripts/start.sh scripts/restart-fresh.sh
./scripts/start.sh dev
```

**Step 4 (alternative) — Manual start**

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

**Step 5 — Verify**

```bash
docker compose ps
curl -s http://localhost:8000/health
curl -s http://localhost:3000 | head -5
```

**Step 6 — Open in browser**

```bash
open http://localhost:3000
```

Dev credentials are printed in the terminal after seed (not in README).

**URLs (macOS dev)**

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| PostgreSQL (host) | `localhost:5433` |

**Stop / restart (macOS dev)**

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

Stop:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging down
```

---

### 6. Linux (Kali/Ubuntu/Debian) — development (full)

**Requirements:** Kali, Ubuntu 22.04+, or Debian 12+. Docker Engine + Compose plugin + Git.

**Step 1 — Install Docker** (once per machine)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git curl
sudo usermod -aG docker $USER
```

Log out and log back in (or `newgrp docker`), then verify:

```bash
docker info
docker compose version
```

> Do **not** use `copy` or `scripts\windows\...` on Linux — those are Windows-only.

**Step 2 — Clone**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

Use the full path if needed, e.g. `/home/YOUR_USER/CURSOR` (not `/root/CURSOR` unless you always work as root).

**Step 3 — Environment**

```bash
cp .env.example .env
nano .env
```

Optional: `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`.

**Step 4 — Start (recommended)**

```bash
chmod +x scripts/linux-dev-setup.sh scripts/start.sh
./scripts/linux-dev-setup.sh
```

This script: stops prod/staging conflicts, frees ports 5432/5433/6379, creates `.env`, starts dev.

**Step 4 (alternative) — Manual start**

```bash
docker compose down --remove-orphans 2>/dev/null || true
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

**Step 5 — Verify**

```bash
docker compose ps
curl -s http://localhost:8000/health
curl -s http://localhost:3000 | head -5
```

**Step 6 — Open in browser**

Open **on this machine**: http://localhost:3000

Do **not** run Firefox/Chrome as `root`. Use your normal user:

```bash
exit
firefox http://localhost:3000 &
```

Or from a root shell:

```bash
su - YOUR_USER -c "firefox http://localhost:3000 &"
```

Dev credentials are printed in the terminal after seed (not in README).

**URLs (Linux dev)**

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| PostgreSQL (host) | `localhost:5433` |

**Stop / restart (Linux dev)**

```bash
docker compose down
docker compose down -v
./scripts/linux-dev-setup.sh
docker compose logs backend --tail 80
```

**Port 5432 conflict?**

Dev uses host port **5433**. If startup still fails:

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

Open: https://tamor.staging.local

Stop:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging down
```

---

### 8. Linux server — production (full)

**Requirements:** Ubuntu/Debian VPS in Uzbekistan, Docker Engine, domain (e.g. `tamor.toyloq.uz`), CA TLS certificates, HashiCorp Vault.

**Not for local laptops** — use §6 for Kali/Ubuntu dev.

**Step 1 — Clone on the server**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**Step 2 — Production secrets**

```bash
cp .env.production.example .env.production
nano .env.production
```

Fill **all** `CHANGE_ME` values:

- `POSTGRES_PASSWORD`, `DATABASE_URL`
- `VAULT_ADDR`, `VAULT_TOKEN`
- `TOTP_ENCRYPTION_KEY`, `PINFL_ENCRYPTION_KEY` (32+ chars)
- `CLICK_*`, `PAYME_*` payment keys
- `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`

**Step 3 — TLS certificates (CA-signed)**

```bash
ls -la infra/nginx/tls/fullchain.pem infra/nginx/tls/privkey.pem
```

Place CA-signed files (not `generate-dev-certs.sh` for production):

- `infra/nginx/tls/fullchain.pem`
- `infra/nginx/tls/privkey.pem`

**Step 4 — Go live**

```bash
chmod +x scripts/go-live.sh scripts/verify-prod.sh
./scripts/go-live.sh
```

Non-interactive demo purge:

```bash
GO_LIVE_PURGE=yes ./scripts/go-live.sh
```

**Step 5 — Verify**

```bash
PUBLIC_HOST=tamor.toyloq.uz ./scripts/verify-prod.sh
python3 scripts/red_team_verify.py --url https://tamor.toyloq.uz --production
curl -fsS https://tamor.toyloq.uz/health
```

**Production management**

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f backend
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

**Production staging on server**

```bash
cp .env.staging.example .env.staging
nano .env.staging
./scripts/start.sh staging
./scripts/verify-staging.sh
```

---

### LLM configuration (all platforms)

Add to `.env` (dev) or `.env.production` (prod). **Never commit real keys to git.**

```env
LLM_API_KEY=sk-bl-...              # BazaarLink (primary)
GEMINI_API_KEY=...                 # fallback 1
MISTRAL_API_KEY=...                # fallback 2
AI_ENABLED=true
```

| Platform | Helper script |
|----------|---------------|
| Windows | `scripts\windows\setup-llm-env.cmd` |
| macOS / Linux | Edit `.env` directly |

After changing `.env`, restart the stack:

```bash
docker compose up -d --build          # dev
# or
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build  # prod
```

---

## Troubleshooting

### Used Windows commands on Linux?

On **Linux/macOS** use `cp` (not `copy`) and forward slashes:

```bash
cp .env.example .env
./scripts/linux-dev-setup.sh    # recommended on Kali/Ubuntu/Debian
# or
./scripts/start.sh dev
```

Windows `.cmd` scripts (`scripts\windows\...`) work **only on Windows**.

### `backend is unhealthy` in production

Production requires a fully configured `.env.production`:

- Real passwords (not `CHANGE_ME_...`)
- **HashiCorp Vault** reachable at `VAULT_ADDR` with valid `VAULT_TOKEN`
- JWT keys materialized to `/secrets/jwt_private.pem` and `/secrets/jwt_public.pem`
- CA TLS certs in `infra/nginx/tls/`
- Payment gateway keys (`CLICK_*`, `PAYME_*`)

**On a local laptop (Kali, Ubuntu, etc.) use dev mode, not production:**

```bash
./scripts/linux-dev-setup.sh
```

Check backend logs:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs backend --tail 100
```

### `port 5432 is already allocated`

Another Docker container or system PostgreSQL is using port 5432. **Dev mode now uses host port 5433** for PostgreSQL (internal `postgres:5432` unchanged).

```bash
git pull origin main
./scripts/linux-dev-setup.sh
```

If it still fails, stop the conflicting container manually:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production down 2>/dev/null || true
docker compose down --remove-orphans
sudo systemctl stop postgresql
docker ps --format '{{.Names}} {{.Ports}}' | grep 5432
# stop the foreign container shown above (example):
docker stop some-postgres

./scripts/linux-dev-setup.sh
```

Host DB access (optional): `postgresql://tamor:tamor_dev@localhost:5433/tamor`

### `orphan containers (cursor-nginx-1)`

After switching from prod to dev:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production down --remove-orphans
docker compose down --remove-orphans
./scripts/start.sh dev
```

### Alembic `KeyError: '014_certificate_file_id'`

Pull latest `main` (migration chain was fixed), then reset dev DB:

```bash
git pull origin main
docker compose down -v
./scripts/linux-dev-setup.sh
```

### Opening the app in a browser

- URL: **http://localhost:3000** (same computer where Docker runs)
- Verify: `curl -s http://localhost:8000/health` → `{"status":"ok",...}`
- **Do not** use Cursor/Cloud preview URLs — they cannot reach your local Docker
- On Linux/Kali: open the browser as your **normal user**, not `root`:

```bash
exit                          # leave root shell
firefox http://localhost:3000 &
# or from root:
su - xushnud -c "firefox http://localhost:3000 &"
```

---

## Development access

After `seed_demo_users.py` (or `update-main.cmd` / `linux-dev-setup.sh`), credentials are shown **only in your local terminal**:

| Platform | Command |
|----------|---------|
| Windows | `scripts\windows\show-credentials.cmd` |
| Linux/macOS | Printed by `./scripts/start.sh dev` or `./scripts/linux-dev-setup.sh` |

Credentials are **not published in this repository** for security. Use only in local/staging environments.

---

## Project structure

```
backend/                 FastAPI API
frontend/                Next.js 14 (UZ/RU/EN)
ai-analytics-service/    District analytics microservice
docs/                    Threat model, ADRs, runbooks, security report
infra/nginx/             TLS edge proxy
scripts/                 Go-live, red-team, backup
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [`docs/threat-model.md`](docs/threat-model.md) | STRIDE analysis |
| [`docs/red-team-checklist.md`](docs/red-team-checklist.md) | Section 24A checklist |
| [`docs/go-live-runbook.md`](docs/go-live-runbook.md) | Production deployment |
| [`docs/security-audit-report.md`](docs/security-audit-report.md) | Latest audit results |

---

## License

Government project — Toyloq District Administration.
