# TaMoR — Education Monitoring & Rating Platform

**TaMoR** (Ta'lim Monitoring va Reyting) is a government-grade, multi-tenant-ready, trilingual (UZ/RU/EN) education monitoring system for Toyloq District Administration, Samarkand Region, Uzbekistan.

## Phase 0 Status

This release delivers the foundational architecture:

- Full authentication system (JWT RS256 + refresh rotation + MFA/TOTP + parent OTP)
- PostgreSQL schema with Alembic migrations
- RBAC with 8 roles and granular permissions
- Demo seed script for all 8 roles
- Next.js frontend with next-intl (runtime language switching)
- Uzbek girih ornamental design system
- Docker Compose local development stack
- CI/CD pipeline (GitHub Actions)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OR: Python 3.12+, Node.js 20+, PostgreSQL 15+, Redis 7+

### Docker Compose (Recommended)

```bash
# Clone and start all services
cp .env.example .env
docker compose up --build
```

Services:
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| AI Analytics | http://localhost:8001 |
| MinIO Console | http://localhost:9001 |

The backend automatically runs migrations and seeds demo users on first start.

### Manual Setup (WSL / Linux)

```bash
cd backend

# 1. Python 3.12 virtual environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# 2. Install dependencies (choose one)
pip install -r requirements.txt          # simple
# OR
pip install -e ".[dev]"                  # editable install

# 3. Database — SQLite (no PostgreSQL required)
export DATABASE_URL_SYNC=sqlite:///./tamor.db
export DATABASE_URL=sqlite+aiosqlite:///./tamor.db
export PYTHONPATH=$(pwd)

# 4. Migrate + seed
python -m alembic -c alembic.ini upgrade head
python -m scripts.seed_demo_users

# 5. Run API
uvicorn app.main:app --reload --port 8000
```

Or use the setup script:

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

> **Note:** Alembic uses a **synchronous** driver (`sqlite3` or `psycopg2`).  
> `DATABASE_URL_SYNC` must be `sqlite:///...` or `postgresql://...` — never `+asyncpg` or `+aiosqlite`.

### Manual Setup — PostgreSQL

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Demo Credentials

> **Warning:** These accounts are for development/staging only. All are tagged `is_demo_account=true` and must be purged before production launch.

| Role | Username | Password | MFA |
|------|----------|----------|-----|
| Super Admin | `admin.tamor` | `Tamor#2026Admin!` | TOTP (QR in seed output) |
| Hokimiyat Operator | `operator.hokimiyat` | `Hokim#Op2026!` | TOTP |
| Center Director | `director.aspect` | `Direktor#2026!` | TOTP |
| Center Admin | `admin.aspect` | `CenterAdmin#26!` | — |
| Teacher | `teacher.dilnoza` | `Teach#Dil2026!` | — |
| Auditor | `auditor.tuman` | `Audit#Check26!` | — |
| Parent | `+998901234567` | SMS OTP (logged to console) | — |
| External API | Printed at seed time | HMAC signing | — |

### Running the Seed Script

```bash
cd backend
python -m scripts.seed_demo_users
```

The script prints:
1. A warning banner (non-production only)
2. All demo credentials in a table
3. TOTP secrets and ASCII QR codes for MFA-enabled accounts
4. API key ID and HMAC secret for the external API consumer

**The script hard-fails if `ENVIRONMENT=production`.**

## Project Structure

```
tamor/
├── backend/                 # FastAPI main API
│   ├── app/
│   │   ├── api/v1/          # REST endpoints
│   │   ├── core/            # Security, dependencies
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── alembic/             # Database migrations
│   ├── scripts/             # seed_demo_users.py
│   └── tests/
├── frontend/                # Next.js 14 App Router
│   └── src/
│       ├── app/             # Pages (login, dashboard, verify)
│       ├── components/      # UI components (GirihPattern, LanguageSwitcher)
│       ├── messages/        # i18n JSON (uz, ru, en)
│       └── lib/             # API client
├── ai-analytics-service/    # ML microservice (Phase 3 skeleton)
├── docs/                    # BRD, SRS, ADRs, architecture diagrams
└── docker-compose.yml
```

## API Authentication

### Username/Password + MFA

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin.aspect", "password": "CenterAdmin#26!"}'

# Use access_token from response
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Parent OTP Login

```bash
# Request OTP (code printed in backend console in dev mode)
curl -X POST http://localhost:8000/api/v1/auth/login/otp/request \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567"}'

# Verify OTP
curl -X POST http://localhost:8000/api/v1/auth/login/otp/verify \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567", "code": "123456"}'
```

Refresh tokens are delivered via `httpOnly` cookie and rotated on each `/auth/refresh` call.

## Internationalization

Three locales supported: **UZ** (default), **RU**, **EN**.

- Language switcher (`UZ | RU | EN`) on every screen including login
- Switching updates cookie and re-renders without full page reload
- Russian ICU pluralization (1 / 2-4 / 5+ forms) configured
- Numbers and dates formatted via `Intl.NumberFormat` / `Intl.DateTimeFormat`

## Documentation

| Document | Path |
|----------|------|
| Business Requirements | `docs/BRD.md` |
| System Requirements | `docs/SRS.md` |
| ER Diagram | `docs/er-diagram.md` |
| Security Architecture | `docs/security-architecture.md` |
| Production Architecture | `docs/production-architecture.md` |
| Backup & DR Plan | `docs/backup-disaster-recovery.md` |
| ADRs | `docs/adr/` |

## Production Readiness Checklist

### Done (Phase 0)
- [x] Architecture documentation and ADRs
- [x] Database schema with migrations
- [x] JWT RS256 + refresh token rotation
- [x] MFA/TOTP with backup codes
- [x] Password policy enforcement
- [x] Account lockout (5 attempts → 15 min)
- [x] Parent phone+OTP login
- [x] External API key scaffold
- [x] Demo seed for all 8 roles
- [x] i18n skeleton (3 locales)
- [x] Girih design system
- [x] Docker Compose
- [x] CI/CD pipelines

### Deferred to Later Phases
- [ ] Centers/Students/Teachers CRUD (Phase 1)
- [ ] Hokimiyat dashboard with live data (Phase 1)
- [ ] Rating engine (Phase 2)
- [ ] PDF/Excel reports and certificates (Phase 2)
- [ ] AI analytics computations (Phase 3)
- [ ] Notifications (SMS/email) (Phase 3)
- [ ] PWA / parent portal (Phase 4)

### Required Before Go-Live
- [ ] **Purge all `is_demo_account=true` rows**
- [ ] Generate production JWT RS256 key pair
- [ ] Set production `TOTP_ENCRYPTION_KEY` and `PINFL_ENCRYPTION_KEY`
- [ ] Configure real SMS gateway (eskiz.uz or equivalent)
- [ ] TLS certificates on Nginx
- [ ] Deploy to Uzbekistan data center
- [ ] Penetration test on auth/MFA flow
- [ ] Quarterly backup restore test

## License

Proprietary — Toyloq District Administration, Samarkand Region, Republic of Uzbekistan.
