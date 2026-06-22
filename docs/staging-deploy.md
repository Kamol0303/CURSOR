# TaMoR Staging Deployment Guide

> Production-like verification environment before go-live

## 1. Server prerequisites

- Ubuntu 22.04+ VM (Uzbekistan-hosted recommended)
- Docker Engine 24+ and Docker Compose v2
- DNS A record: `tamor.staging.local` → server IP (or `/etc/hosts` for internal testing)
- Ports 80 and 443 open to your test network only (not public internet)

## 2. Prepare TLS certificates

```bash
./infra/nginx/generate-dev-certs.sh
# For staging with a real hostname, replace infra/nginx/tls/*.pem with CA-signed certs
```

## 3. Configure environment

```bash
cp .env.staging.example .env.staging
# Edit all CHANGE_ME values — use strong random passwords (32+ chars for encryption keys)
```

Required values:
- `POSTGRES_PASSWORD` — unique staging password
- `TOTP_ENCRYPTION_KEY`, `PINFL_ENCRYPTION_KEY` — 32+ random characters each
- `PUBLIC_HOST` — hostname users will access (e.g. `tamor.staging.local`)

## 4. Deploy stack

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build
```

Wait for health:

```bash
docker compose -f docker-compose.staging.yml ps
curl -k https://tamor.staging.local/health
```

## 5. Seed test users (staging only)

```bash
docker compose -f docker-compose.staging.yml exec backend \
  python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

## 6. Automated verification

### GitHub Actions (recommended)

Run workflow **staging-verify** with `staging_url=https://tamor.staging.local`

### Manual

```bash
# From repo checkout on CI runner or admin laptop with VPN access
python3 scripts/red_team_verify.py --url https://tamor.staging.local --production

cd backend
export DATABASE_URL=postgresql+asyncpg://tamor:PASSWORD@localhost:5432/tamor
export REDIS_URL=redis://localhost:6379/0
export ENVIRONMENT=test
pytest tests/security/ -v
```

## 7. Manual smoke tests

| Test | Steps |
|------|-------|
| Admin MFA first login | Login as `admin.tamor` → MFA setup screen → scan TOTP → dashboard |
| Parent OTP | `/parent/login` → `+998901234567` → OTP from backend logs (if eskiz not configured) |
| Certificate verify | `/verify/TAMOR-...` public page |
| Backup | `POSTGRES_PASSWORD=... ./scripts/backup_postgres.sh` |
| Restore drill | `CONFIRM_RESTORE=yes ./scripts/restore_postgres.sh backups/tamor_*.sql.gz` |

## 8. Before promoting to production

- [ ] `pre_deploy_check.py` passes against production config
- [ ] `purge_demo_data.py` dry-run reviewed
- [ ] `docs/red-team-checklist.md` signed off
- [ ] Vault secrets provisioned (`docs/go-live-runbook.md`)
- [ ] Demo seed **not** run on production

## Rollback

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging down
# Restore volume from backup if needed
```
