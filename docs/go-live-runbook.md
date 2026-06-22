# TMB Go-Live Runbook

> Phase 5 deliverable — production deployment checklist for Toyloq District IT

## Prerequisites (external / organizational)

- [ ] Uzbekistan-hosted infrastructure provisioned (VMs or K8s) — **data localization**
- [ ] HashiCorp Vault cluster operational with `tmb/prod` KV path
- [ ] **CA-signed** TLS certificates installed to `infra/nginx/tls/` (not `generate-dev-certs.sh`)
- [ ] PostgreSQL 15 and Redis 7 on private network (not public internet — RT-24)
- [ ] DNS: `tamor.toyloq.uz` → Nginx edge
- [ ] External penetration test scheduled (`docs/red-team-checklist.md` manual items)

## 1. Secrets Provisioning (Vault)

Store in `secret/tmb/prod/` (KV v2, field name `value`):

| Key | Description |
|-----|-------------|
| `jwt_private_key` | RS256 private PEM |
| `jwt_public_key` | RS256 public PEM |

Environment variables (not in Vault):

- `TOTP_ENCRYPTION_KEY` (32+ random bytes)
- `PINFL_ENCRYPTION_KEY` (32+ random bytes)
- `DATABASE_URL`, `REDIS_URL`
- `ESKIZ_EMAIL` / `ESKIZ_PASSWORD` or `ESKIZ_API_TOKEN`

Backend entrypoint bootstraps JWT PEMs from Vault into `/secrets` on first start.

## 2. Configuration

```bash
cp .env.production.example .env.production
# Edit all CHANGE_ME values — never commit .env.production
```

Required settings:

- `ENVIRONMENT=production`
- `DEBUG=false`
- `SECRETS_BACKEND=vault`
- `VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_SECRET_PREFIX=tmb/prod`
- `CORS_ORIGINS=["https://tamor.toyloq.uz"]`
- `POSTGRES_PASSWORD` must match `DATABASE_URL`

## 3. Automated Go-Live (recommended)

```bash
chmod +x scripts/go-live.sh scripts/verify-prod.sh scripts/purge-demo-data.sh scripts/pre-deploy-check.sh
./scripts/go-live.sh
```

This will: build → dry-run purge → confirm purge → pre-deploy gate → verify-prod.

## 4. Manual Steps (alternative)

### Purge demo data

```bash
# Dry run first
./scripts/purge-demo-data.sh --i-understand-this-deletes-demo-data --dry-run

# Execute purge (production only)
./scripts/purge-demo-data.sh --i-understand-this-deletes-demo-data
```

Staging test (optional): add `--allow-non-production` inside container.

### Pre-deploy gate

```bash
./scripts/pre-deploy-check.sh
```

Must exit 0 before traffic switch.

### Deploy

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

### Post-deploy verification

```bash
PUBLIC_HOST=tamor.toyloq.uz ./scripts/verify-prod.sh
```

## 5. Post-Deploy Manual Checklist

- [ ] Login with real `super_admin` (MFA enforced)
- [ ] Public certificate verify works
- [ ] Parent OTP SMS delivers via eskiz.uz
- [ ] Celery beat log shows scheduled rating job
- [ ] Backup/restore drill: `scripts/backup_postgres.sh` + `scripts/restore_postgres.sh`
- [ ] Load test baseline: `python scripts/load_test.py --url https://tamor.toyloq.uz -c 20 -n 50`
- [ ] Complete sign-off table in `docs/red-team-checklist.md`

## 6. Rollback

```bash
docker compose -f docker-compose.prod.yml down
# Restore PostgreSQL from last snapshot (scripts/restore_postgres.sh)
```

## Staging verification (before prod)

```bash
python scripts/red_team_verify.py --url https://tamor.staging.local --production
python scripts/load_test.py --url https://tamor.staging.local -c 20 -n 50
```

## Ownership

See `docs/incident-response.md` Section 17A.6 — assign named roles before go-live (RT-25).
