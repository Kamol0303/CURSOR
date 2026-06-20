# TaMoR - District Education Monitoring & Rating Platform

TaMoR is a multi-tenant-ready education monitoring and rating platform for district administrations. This repository now contains the Phase 0 foundation:

- FastAPI backend with enterprise authentication, JWT/refresh rotation, MFA, demo seed data, and core RBAC primitives
- Next.js frontend shell with trilingual runtime i18n and Uzbek ornamental design tokens
- Alembic migration scaffold for the foundational schema
- Docker Compose, CI, architecture docs, security docs, ER diagram, and ADRs

## Repository layout

```text
.
├── backend
│   ├── alembic
│   ├── app
│   └── tests
├── docs
│   └── adr
├── frontend
│   └── src
└── .github
```

## Quick start

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./backend[dev]
cd backend
alembic -c alembic.ini upgrade head
python -m app.scripts.seed_demo_users
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose

```bash
docker compose up --build
```

## Demo credentials

Run the seed script in a non-production environment:

```bash
cd backend && python -m app.scripts.seed_demo_users
```

It prints:

- Username/password credentials for the six interactive back-office roles
- Seeded TOTP provisioning URIs for mandatory-MFA demo users
- Parent OTP dev-mode behavior instructions
- A generated external API key and HMAC secret

The script hard-fails in production and tags seeded rows with `is_demo_account = true`.

## Phase 0 documents

- [Business Requirements](docs/BRD.md)
- [System Requirements](docs/SRS.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Security Architecture](docs/SECURITY_ARCHITECTURE.md)
- [ER Diagram](docs/ER_DIAGRAM.md)
- [ADR Index](docs/adr)

## Testing

```bash
pytest backend/tests
cd frontend && npm run lint && npm run typecheck
```

## Production reminder

Before go-live:

1. Replace demo secrets, SMS adapters, storage keys, and RS256 development key material.
2. Provision Uzbekistan-resident infrastructure.
3. Purge all rows marked `is_demo_account`.
