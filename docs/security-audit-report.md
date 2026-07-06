# TMB Security Audit Report

> Date: 2026-07-06 · Branch: `main` · Tool: `scripts/red_team_verify.py`

## Executive summary

| Layer | Result | Notes |
|-------|--------|-------|
| **Offline automated red-team** | **12/12 PASSED** | `python3 scripts/red_team_verify.py --offline` |
| **CI security integration tests** | Configured | `tests/security/`, GitHub Actions `tamor-ci` |
| **Production gate** | Configured | `production-gate.yml`, `pre_deploy_check.py` |
| **External pentest (third party)** | **Pending** | Organizational — sign-off in `docs/red-team-checklist.md` |

The platform passes all **automated** security checks available without a live production host. Remaining items require staging/production URL verification or district IT sign-off.

## Offline automated checks (passed)

| ID | Check |
|----|-------|
| RT-03 | MFA mandatory for super_admin, hokimiyat_operator, center_director |
| RT-04 | No PEM/JWT private keys in repository |
| RT-05 | Access token TTL ≤ 15 minutes |
| RT-19 | SSRF blocks internal URLs (127.0.0.1, etc.) |
| RT-21 | Nginx rate limit zones configured |
| RT-22 | Cosign workflow present |
| RT-23 | Vault secrets ADR documented |
| RT-26 | Backup/restore scripts exist |
| RT-29 | Click webhook rejects invalid signature |
| RT-29b | Payme webhook rejects invalid auth |
| RT-29c | Payment gateway stubs removed |
| RT-30 | JWT `jti` deny-list on logout |

## Manual / live checks (before go-live)

| ID | Action |
|----|--------|
| RT-07 | IDOR pentest — Center A vs Center B |
| RT-13 | PINFL masking in API responses |
| RT-15 | Generic errors only in production (`DEBUG=false`) |
| RT-17 | Certificate verify rate limit (live) |
| RT-20 | CA TLS + HSTS on production host |
| RT-24 | PostgreSQL not on public internet |
| RT-25 | Incident response roles assigned |
| RT-27 | Demo data purged (`purge_demo_data.py`) |
| RT-28 | Load test baseline recorded |

## How to re-run

```bash
# Offline (no server)
python3 scripts/red_team_verify.py --offline

# Staging / production
python3 scripts/red_team_verify.py --url https://tamor.staging.local --production

# Full integration suite (Docker + PostgreSQL)
cd backend && pytest tests/security/ -v
```

## Security architecture highlights

- JWT RS256, refresh token rotation + reuse detection
- PostgreSQL RLS (FORCE) on sensitive tables
- PINFL encrypted at rest, reveal audited
- RBAC + tenant scoping + portal isolation
- Audit log (`/dashboard/audit`) for change tracking
- LLM API keys via environment only (never in git)

## Verdict

**Code-level security: READY** for staging and production deployment pending infrastructure checklist (Vault, CA TLS, UZ hosting) and external pentest sign-off.
