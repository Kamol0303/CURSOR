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

- `TOTP_ENCRYPTION_KEY` (32+ random bytes) — `openssl rand -base64 32`
- `PINFL_ENCRYPTION_KEY` (32+ random bytes)
- `CLICK_SERVICE_ID`, `CLICK_SECRET_KEY` — from Click merchant cabinet
- `PAYME_SECRET_KEY` — from Payme Merchant API
- `DATABASE_URL`, `REDIS_URL`
- `ESKIZ_EMAIL` / `ESKIZ_PASSWORD` or `ESKIZ_API_TOKEN`

**Never set** `PAYMENT_WEBHOOK_ALLOW_UNSIGNED_DEV=true` in production.

## 2a. CA TLS certificates

1. Obtain CA-signed certificate for `PUBLIC_HOST` (district CA or approved provider).
2. Install to `infra/nginx/tls/`:
   - `fullchain.pem`
   - `privkey.pem`
3. Verify: `openssl x509 -in infra/nginx/tls/fullchain.pem -noout -dates`
4. Do **not** use `generate-dev-certs.sh` in production.

## 2b. Vault checklist

- [ ] Vault cluster reachable from app network only
- [ ] KV path `secret/tmb/prod/jwt_private_key` and `jwt_public_key` populated
- [ ] App role/token with read-only access to `tmb/prod/*`
- [ ] Token rotation procedure documented with district IT

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

**O'zbekcha qadamlar:** `docs/go-live-steps-uz.md`  
**Windows tayyorgarlik:** `scripts/windows/go-live-prep.cmd`  
**Build tekshiruvi:** `scripts/verify-prod-build.sh` · Windows: `scripts/windows/verify-prod-build.cmd`

Production frontend uses `frontend/Dockerfile.prod` (Next.js `output: "standalone"`). Uploads persist in Docker volume `upload_data` (`FILE_UPLOAD_DIR=/data/uploads`).

**LLM (AI):** BazaarLink primary (`LLM_API_KEY`), Gemini fallback (`GEMINI_API_KEY`) — see `docs/production-100-checklist-uz.md`.

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
