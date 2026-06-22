# TMB — Ta'lim Monitoringi Boshqaruvi

Government-grade education management monitoring platform for Toyloq District, Samarkand Region, Uzbekistan.

## Phase 0 Status (Complete)

Phase 0 delivers the security foundation:

- STRIDE threat model (`docs/threat-model.md`)
- Incident response runbook (`docs/incident-response.md`)
- ER diagram (`docs/er-diagram.md`)
- Architecture Decision Records (`docs/adr/`)
- PostgreSQL schema + Alembic migrations
- Full authentication system (JWT RS256, refresh rotation, MFA/TOTP, RBAC)
- Demo seed script with production safety guards
- Next.js frontend with trilingual i18n skeleton (UZ/RU/EN)
- Login page with girih ornamental design
- Docker Compose dev environment
- CI/CD pipeline (GitHub Actions)

## Phase 1 Status (Complete)

- Centers/Students/Teachers CRUD with RBAC + tenant scoping
- Dashboard KPIs, PINFL encryption/masking
- Trilingual frontend (UZ/RU/EN)

## Phase 2 Status (Complete)

- **Rating engine** — configurable weights, daily compute, tamper-evident `inputs_hash`
- **Certificates** — issue with QR code + integrity hash, idempotency key support
- **Public verification** — `/api/v1/public/verify/{number}` (10 req/min/IP)
- **Reports** — PDF and Excel rating exports
- **Frontend** — ratings table, certificates gallery, public `/verify` page

## Phase 3 Status (Complete)

- **AI analytics microservice** — fastest-growing center, declining centers, high-demand subjects, education gap index
- **RS256 JWT verification** — public key only; read-only DB role without PINFL access
- **Notifications** — in-app, SMS (eskiz.uz stub), email stub; locale-aware templates
- **Integrations** — SSRF-safe HTTP client, SMS webhook signature validation
- **Frontend** — `/dashboard/analytics`, notification bell with unread count
- **Scheduler** — APScheduler daily cron in ai-analytics-service

## Phase 4 Status (Complete)

- **Parent portal** — SMS OTP login, children list, certificates view (`/parent/login`)
- **PWA** — manifest, service worker, installable mobile shell
- **PostgreSQL RLS** — FORCE policies on students, enrollments, certificates, guardians
- **Telegram bot** — webhook with `/verify` and `/status` commands
- **Celery** — daily rating recompute (03:00 Asia/Samarkand)
- **Security hardening** — HSTS/CSP in production, Permissions-Policy
- **Load test** — `scripts/load_test.py`

## Phase 5 Status (Complete)

- **Vault secrets** — KV v2 provider, JWT materialization at startup (ADR-008)
- **Production validation** — fail-fast on dev secrets, DEBUG=true, localhost CORS
- **Nginx edge** — TLS 1.2+, rate limits, reverse proxy (`infra/nginx/`)
- **docker-compose.prod.yml** — production stack with internal network
- **Go-live tooling** — `purge_demo_data.py`, `pre_deploy_check.py`
- **Eskiz.uz SMS** — production API integration path
- **CI gates** — production-gate workflow, Cosign image signing skeleton
- **Docs** — go-live runbook, red-team checklist (Section 24A)

## Phase 7 — OCMS Platform Extension

Full education center management modules on Clean Architecture:

- **Migration `008_ocms`** — courses, lessons, exams, grades, payment_transactions, files, messages
- **Roles** — `accountant`, `student` (+ existing 8-role RBAC)
- **Dashboard** — active students, monthly revenue, debtors, daily/weekly/monthly charts
- **Exams API/UI** — create tests, question bank, submit & score results
- **Grades API/UI** — student grade tracking
- **Payments** — Click/Payme webhook endpoints (`/integrations/click|payme/webhook`)
- **Logging** — structured `core/logging_config.py`
- **Architecture doc** — `docs/ocms-master-architecture.md`

```bash
docker compose exec backend alembic upgrade head
```

## Security Verification

```bash
# Offline (CI / no server)
python3 scripts/red_team_verify.py --offline

# Against running staging
python3 scripts/red_team_verify.py --url https://staging.tamor.uz --production

# Integration security tests (PostgreSQL + Redis required)
cd backend && pytest tests/security/ -v
```

## Staging deployment

See `docs/staging-deploy.md` and `.env.staging.example`.

```bash
cp .env.staging.example .env.staging
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build
```

## Integrations

SMS (eskiz.uz) works in staging/production when configured. **Email is not implemented** — see `docs/integrations.md`.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (optional, for local frontend dev)
- Python 3.12+ (optional, for local backend dev)

### Run with Docker

```bash
docker compose up --build
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- AI Analytics: http://localhost:8001
- API Docs (dev): http://localhost:8000/docs

### Seed Demo Users

After services are running:

```bash
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

Demo credentials are printed to the console only. **Never run in production.**

| Role | Username | Password | MFA |
|------|----------|----------|-----|
| Super Admin | `admin.tmb` | `Tmb#2026Admin!` | TOTP (QR in console) |
| Hokimiyat Operator | `operator.hokimiyat` | `Hokim#Op2026!` | TOTP |
| Center Director | `director.aspect` | `Direktor#2026!` | TOTP |
| Center Admin | `admin.aspect` | `CenterAdmin#26!` | — |
| Teacher | `teacher.dilnoza` | `Teach#Dil2026!` | — |
| Auditor | `auditor.tuman` | `Audit#Check26!` | — |
| Parent | phone `+998901234567` | SMS OTP (dev console) | — |

Parent portal: http://localhost:3000/parent/login

### Local Development (without Docker)

**Backend:**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdir -p /tmp/secrets
openssl genrsa -out /tmp/secrets/jwt_private.pem 2048
openssl rsa -in /tmp/secrets/jwt_private.pem -pubout -out /tmp/secrets/jwt_public.pem
cp .env.example .env
# Start PostgreSQL and Redis, then:
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
backend/          FastAPI API (auth, RBAC, core schema)
frontend/         Next.js 14 + next-intl (UZ/RU/EN)
ai-analytics-service/  AI microservice skeleton (Phase 3)
docs/             Threat model, ADRs, runbooks
infra/            Nginx, deployment configs
```

## Security Notes

- JWT private keys live in `/secrets/` (Vault/KMS in production)
- Refresh tokens in httpOnly Secure SameSite=Strict cookies
- Demo accounts tagged `is_demo_account=true`; CI blocks production deploy if any exist
- See `docs/threat-model.md` for full STRIDE analysis

## Production Readiness Checklist

### Done (Phase 0–5)
- [x] Phase 0: Auth, threat model, i18n skeleton
- [x] Phase 1: CRUD, dashboard, PINFL masking
- [x] Phase 2: Rating engine, certificates, QR verify, PDF/Excel reports
- [x] Phase 3: AI analytics, notifications, integration adapters
- [x] Phase 4: Parent portal, PWA, RLS, Telegram bot, Celery scheduler
- [x] Phase 5: Vault secrets, Nginx/TLS, go-live runbook, deploy gates

### Deferred
- [ ] External penetration test (use `docs/red-team-checklist.md`)

### Required Before Go-Live
- Run `scripts/purge_demo_data.py` and `scripts/pre_deploy_check.py`
- Configure Vault secrets per `docs/go-live-runbook.md`
- Complete `docs/red-team-checklist.md` with sign-off
- CA-signed TLS certificates (not `generate-dev-certs.sh`)
- Data localization on Uzbekistan infrastructure

## License

Government project — Toyloq District Administration.
