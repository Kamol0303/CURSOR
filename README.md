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

## Quick start (Docker)

```bash
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

- Frontend: http://localhost:3000  
- API: http://localhost:8000  
- Docs (dev): http://localhost:8000/docs

### LLM configuration (`.env` — never commit keys)

```env
LLM_API_KEY=sk-bl-...              # BazaarLink (primary)
GEMINI_API_KEY=...                 # fallback 1
MISTRAL_API_KEY=...                # fallback 2
AI_ENABLED=true
```

Windows: `scripts\windows\setup-llm-env.cmd`

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

## Production go-live

```bash
cp .env.production.example .env.production   # fill secrets
./scripts/go-live.sh                          # Linux server
```

Windows prep: `scripts\windows\go-live-prep.cmd`  
Build verify: `scripts\windows\verify-prod-build.cmd`

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
