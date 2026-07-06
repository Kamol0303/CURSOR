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

### Windows (development)

**1. Clone the repository**

```cmd
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**2. Create environment file and LLM keys**

```cmd
copy .env.example .env
scripts\windows\setup-llm-env.cmd
```

**3. Start the full dev stack** (pulls `main`, builds Docker, migrates DB, seeds demo users)

```cmd
scripts\windows\update-main.cmd
```

**4. Show demo logins**

```cmd
scripts\windows\show-credentials.cmd
```

| URL | Address |
|-----|---------|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

**Windows — staging (HTTPS, local)**

```cmd
scripts\windows\setup-staging-env.cmd
bash infra/nginx/generate-dev-certs.sh
scripts\windows\staging-up.cmd
```

Add to `C:\Windows\System32\drivers\etc\hosts`: `127.0.0.1 tamor.staging.local`  
Open: https://tamor.staging.local

**Windows — useful commands**

```cmd
scripts\windows\backend-logs.cmd              REM backend logs (dev)
scripts\windows\backend-logs.cmd staging      REM backend logs (staging)
docker compose down                           REM stop dev
docker compose down -v                        REM stop dev + wipe DB
docker compose logs backend --tail 80           REM recent backend output
```

**Windows — production prep** (test prod build locally; real prod runs on Linux)

```cmd
copy .env.production.example .env.production
REM Edit .env.production — fill all CHANGE_ME values
scripts\windows\go-live-prep.cmd
scripts\windows\verify-prod-build.cmd
```

> If `docker info` fails: open **Docker Desktop** from the Start menu and wait until the tray whale icon turns green (2–3 minutes).

---

### macOS (development)

**1. Clone and configure**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
cp .env.example .env
# Edit .env — add LLM_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY (optional)
```

**2. One-command start** (recommended)

```bash
chmod +x scripts/start.sh scripts/restart-fresh.sh
./scripts/start.sh dev
```

**3. Or start manually**

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

| URL | Address |
|-----|---------|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

**macOS — staging (HTTPS, local)**

```bash
./scripts/start.sh staging
# Add to /etc/hosts: 127.0.0.1 tamor.staging.local
sudo sh -c 'echo "127.0.0.1 tamor.staging.local" >> /etc/hosts'
open https://tamor.staging.local
```

**macOS — useful commands**

```bash
docker compose down                    # stop dev
docker compose down -v                 # stop + wipe DB
./scripts/restart-fresh.sh dev         # full reset and restart
docker compose logs backend --tail 80  # recent backend output
./scripts/show-mfa-qr.sh               # MFA QR for admin.tmb
```

---

### Linux (development)

Same commands as macOS. Requires Docker Engine and the Compose plugin:

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER   # log out and back in
```

Then follow the **macOS** steps above (`./scripts/start.sh dev`).

---

### Linux server (production)

Run on the production VPS (e.g. `tamor.toyloq.uz`). Production uses `docker-compose.prod.yml` and `.env.production`.

**1. Clone and configure secrets**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
cp .env.production.example .env.production
nano .env.production   # fill ALL CHANGE_ME values: DB password, JWT secret, LLM keys, etc.
```

**2. Install CA-signed TLS certificates** (not dev self-signed)

```bash
# Place your CA certificates:
#   infra/nginx/tls/fullchain.pem
#   infra/nginx/tls/privkey.pem
ls -la infra/nginx/tls/
```

**3. Go live** (build, migrate, purge demo data, pre-deploy gate, verify)

```bash
chmod +x scripts/go-live.sh scripts/verify-prod.sh
./scripts/go-live.sh
```

Non-interactive purge (CI / automation):

```bash
GO_LIVE_PURGE=yes ./scripts/go-live.sh
```

**4. Post-deploy verification**

```bash
PUBLIC_HOST=tamor.toyloq.uz ./scripts/verify-prod.sh
python3 scripts/red_team_verify.py --url https://tamor.toyloq.uz --production
```

**Linux server — production management**

```bash
# Status
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# Logs
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f backend

# Restart stack
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Run migrations after update
docker compose -f docker-compose.prod.yml --env-file .env.production \
  exec backend alembic upgrade head

# Stop
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

**Linux server — staging**

```bash
cp .env.staging.example .env.staging
nano .env.staging
bash infra/nginx/generate-dev-certs.sh   # or install real certs for staging host
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

## Demo credentials (development only)

| Role | Username | Password |
|------|----------|----------|
| Super Admin | `admin.tmb` | `Tmb#2026Admin!` |
| Hokimiyat Operator | `operator.hokimiyat` | `Hokim#Op2026!` |
| Center Admin | `admin.aspect` | `CenterAdmin#26!` |
| Teacher | `teacher.dilnoza` | `Teach#Dil2026!` |
| Student | `student.sardor` | `Student#2026!` |

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
