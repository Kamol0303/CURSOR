# Production Readiness Status

> Last updated: Phase 5 + go-live automation

## Done (in repository)

| Area | Artifacts |
|------|-----------|
| Auth / MFA | Phases 0–5, `backend/app/services/auth_service.py` |
| Staging | `docker-compose.staging.yml`, `docs/staging-deploy.md`, `scripts/verify-staging.sh` |
| Production compose | `docker-compose.prod.yml`, `.env.production.example` |
| Vault bootstrap | `backend/scripts/entrypoint.sh`, `docs/adr/008-vault-secrets.md` |
| Demo purge | `backend/scripts/purge_demo_data.py`, `scripts/purge-demo-data.sh` |
| Pre-deploy gate | `backend/scripts/pre_deploy_check.py`, `scripts/pre-deploy-check.sh` |
| Go-live automation | `scripts/go-live.sh`, `scripts/verify-prod.sh` |
| Red team | `scripts/red_team_verify.py`, `docs/red-team-checklist.md` |
| Backup / restore | `scripts/backup_postgres.sh`, `scripts/restore_postgres.sh` |
| CI gate | `.github/workflows/production-gate.yml` |

## Required before go-live (organizational / infra)

These cannot be completed in code alone:

1. **Uzbekistan-hosted infrastructure** — deploy `docker-compose.prod.yml` on in-country VMs
2. **CA-signed TLS** — replace `infra/nginx/tls/` self-signed certs
3. **Vault cluster** — populate `secret/tmb/prod/jwt_*` keys
4. **External penetration test** — manual RT-07, RT-13, RT-24 sign-off
5. **Incident response owners** — fill `docs/incident-response.md` §17A.6
6. **Red-team sign-off** — `docs/red-team-checklist.md` table

## Go-live command sequence

```bash
cp .env.production.example .env.production
# Fill secrets, install CA certs to infra/nginx/tls/
chmod +x scripts/go-live.sh
./scripts/go-live.sh
```

## Deferred

- External penetration test (track in `docs/red-team-checklist.md`)
- Merge feature branches to `main` when district IT approves
