# OCMS — O'quv Markazi Boshqaruv Tizimi (Master Architecture)

Production-ready education center management platform built on the TMB monorepo.

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Database | PostgreSQL 16 (RLS, soft delete, indexes) |
| Cache / Queue | Redis, Celery + Beat |
| Auth | JWT RS256, refresh rotation, MFA/TOTP, RBAC |
| Frontend | Next.js 14, TypeScript, TailwindCSS |
| Edge | Nginx, Docker Compose, GitHub Actions CI/CD |
| Integrations | Telegram, SMS (Eskiz), Click/Payme webhooks |

## Clean Architecture Layers

```
frontend/src/          → Presentation (pages, components, i18n)
backend/app/api/       → HTTP adapters (thin controllers)
backend/app/services/  → Business logic (domain rules)
backend/app/models/    → Persistence (SQLAlchemy ORM)
backend/app/schemas/   → DTO / validation (Pydantic)
backend/app/core/      → Cross-cutting (auth, RBAC, logging, security)
backend/app/integrations/ → External systems
```

**SOLID / DRY / KISS**
- One service per domain (`exam_service`, `grade_service`, …)
- Permissions centralized in `core/permissions.py`
- Tenant scoping via `core/tenant.py` + PostgreSQL RLS
- API routes delegate to services; no business logic in routes

## Roles (RBAC)

| Spec role | System code | MFA |
|-----------|-------------|-----|
| Super Admin | `super_admin` | Yes |
| Operator | `hokimiyat_operator` | Yes |
| Direktor | `center_director` | Yes |
| Menejer | `center_admin` | No |
| O'qituvchi | `teacher` | No |
| Buxgalter | `accountant` | No |
| O'quvchi | `student` | No |
| Ota-ona | `parent` | OTP |

Permissions use `module.action` format (`exams.create`, `grades.read`, …).

## Database Schema (migration `008_ocms`)

| Table | Purpose |
|-------|---------|
| `users`, `roles`, `permissions` | Identity & RBAC |
| `training_centers` | Filiallar (branches) |
| `students`, `guardians`, `teachers` | People |
| `subjects`, `courses`, `lessons` | Curriculum |
| `groups`, `enrollments` | Guruhlar |
| `attendance_sessions`, `attendance_records` | Davomat |
| `student_payments`, `payment_transactions` | To'lovlar |
| `exams`, `exam_questions`, `exam_results` | Imtihon |
| `grades` | Baholar |
| `certificates` | Sertifikatlar |
| `notifications`, `messages` | Xabarnomalar |
| `files` | Rasm / pasport |
| `audit_logs` | Audit |

All domain tables: PK (UUID), FK, indexes, `created_at` / `updated_at`, soft delete where applicable.

## Module Status

| Module | Backend | Frontend | Notes |
|--------|---------|----------|-------|
| Dashboard KPI + charts | ✅ | ✅ | Revenue, debtors, time series |
| Students | ✅ | ✅ | PINFL encrypt, CRUD |
| Teachers | ✅ | ✅ | Salary/KPI fields in DB |
| Groups | ✅ | ✅ | Enroll API; UI enroll next |
| Attendance | ✅ | ✅ | Manual + QR; Face ID planned |
| Payments | ✅ | ✅ | Click/Payme webhooks stub |
| Exams | ✅ | ✅ | Create, submit, results |
| Grades | ✅ | ✅ | Monthly grades |
| Certificates | ✅ | ✅ | QR + public verify |
| Ratings | ✅ | ✅ | Daily Celery job |
| Parent portal | ✅ | ✅ | SMS OTP |
| Telegram | ✅ | — | Webhook bot |
| Reports | ⚠️ | ⚠️ | Ratings PDF/Excel; more exports planned |
| File upload | ⚠️ | — | Schema ready |
| Push notifications | ❌ | — | PWA shell only |

## API

- Base: `/api/v1`
- Swagger: `/docs` (DEBUG/staging)
- Standard envelope: `{ success, data, meta, error }`
- Pagination: `page`, `per_page`
- Versioning: URL prefix `v1`

## Security

- JWT + refresh token rotation
- MFA for admin roles
- Rate limiting (nginx + app)
- XSS/CSRF headers, SQL injection via ORM
- Audit log on sensitive actions
- Encryption: PINFL at rest, TLS in transit
- Backup: `scripts/backup_postgres.sh`

## One-Command Start

```bash
docker compose up -d --build
# Migrations
docker compose exec backend alembic upgrade head
# Demo users
docker compose exec backend python scripts/seed_demo_users.py
```

Frontend: http://localhost:3000  
API docs: http://localhost:8000/docs

## Testing

```bash
cd backend && pytest tests/unit/ -v
cd backend && pytest tests/security/ -v   # needs PostgreSQL
cd frontend && npm run build
```

## Deployment

See `docs/go-live-runbook.md`, `docs/staging-deploy.md`, `scripts/go-live.sh`.

## Next Phases

1. Guruhga o'quvchi biriktirish UI
2. Face ID attendance (mobile SDK)
3. Full Click/Payme HMAC verification
4. Student personal cabinet (`student` role login)
5. Shadcn UI component migration
6. E2E tests (Playwright)
