# TaMoR Go-Live Runbook

> Phase 5 deliverable — production deployment checklist for Toyloq District IT

## Prerequisites

- [ ] Uzbekistan-hosted infrastructure provisioned (VMs or K8s)
- [ ] HashiCorp Vault cluster operational with `tamor/prod` KV path
- [ ] CA-signed TLS certificates (not self-signed)
- [ ] PostgreSQL 15 and Redis 7 on private network
- [ ] DNS: `tamor.toyloq.uz` → Nginx edge

## 1. Secrets Provisioning (Vault)

Store in `secret/tamor/prod/`:

| Key | Description |
|-----|-------------|
| `jwt_private_key` | RS256 private PEM |
| `jwt_public_key` | RS256 public PEM |

Environment variables (not in Vault):

- `TOTP_ENCRYPTION_KEY` (32+ random bytes)
- `PINFL_ENCRYPTION_KEY` (32+ random bytes)
- `DATABASE_URL`, `REDIS_URL`
- `ESKIZ_EMAIL` / `ESKIZ_PASSWORD` or `ESKIZ_API_TOKEN`

## 2. Configuration

```bash
cp .env.production.example .env.production
# Edit all CHANGE_ME values
```

Required settings:
- `ENVIRONMENT=production`
- `DEBUG=false`
- `SECRETS_BACKEND=vault`
- `CORS_ORIGINS=["https://tamor.toyloq.uz"]`

## 3. Purge Demo Data

```bash
# Dry run first
docker compose -f docker-compose.prod.yml exec backend \
  python scripts/purge_demo_data.py --i-understand-this-deletes-demo-data --dry-run

# Execute purge
docker compose -f docker-compose.prod.yml exec backend \
  python scripts/purge_demo_data.py --i-understand-this-deletes-demo-data
```

## 4. Pre-Deploy Gate

```bash
docker compose -f docker-compose.prod.yml exec backend \
  python scripts/pre_deploy_check.py
```

Must exit 0 before traffic switch.

## 5. Deploy

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

## 6. Post-Deploy Verification

- [ ] `curl -sf https://tamor.toyloq.uz/health`
- [ ] Login with real super_admin (MFA enforced)
- [ ] Public certificate verify works
- [ ] Parent OTP SMS delivers via eskiz.uz
- [ ] Celery beat log shows scheduled rating job
- [ ] No `/docs` endpoint exposed (DEBUG=false)

## 7. Rollback

```bash
docker compose -f docker-compose.prod.yml down
# Restore PostgreSQL from last snapshot
```

### Staging verification

```bash
# After docker compose up on staging:
python scripts/red_team_verify.py --url https://staging.tamor.uz
python scripts/load_test.py --url https://staging.tamor.uz -c 20 -n 50
python scripts/pre_deploy_check.py  # must pass before go-live
```

## Ownership

See `docs/incident-response.md` Section 17A.6 for named roles.
