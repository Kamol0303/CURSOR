# TMB Red-Team Checklist (Section 24A)

> Execute before production go-live.

## Automated verification

```bash
# Offline (CI / no server)
python scripts/red_team_verify.py --offline

# Against staging or production URL
python scripts/red_team_verify.py --url https://tamor.toyloq.uz --production

# Full production gate (includes pre_deploy_check)
PUBLIC_HOST=tamor.toyloq.uz ./scripts/verify-prod.sh
```

| Auto | ID | Check |
|:----:|----|-------|
| CI | RT-01 | Login rate limit per account |
| CI | RT-02 | Refresh token reuse revokes family |
| CI | RT-06 | Parent OTP max attempts |
| CI | RT-12 | PINFL encrypted at rest |
| CI | RT-08 | Teacher cannot reveal PINFL |
| CI | RT-09 | Parent sees only linked guardian children |
| CI | RT-10 | RLS FORCE on students, enrollments, certificates, guardians |
| CI | RT-11 | Auditor PINFL reveal returns decrypted value |
| CI | RT-17/18 | Verify rate limit + certificate tamper detection |
| script | RT-03–05, RT-19, RT-21–23, RT-29–30 | `red_team_verify.py --offline` |
| script | RT-16, RT-27 | `pre_deploy_check.py` + `purge_demo_data.py` |
| script | RT-26 | `scripts/backup_postgres.sh`, `scripts/restore_postgres.sh` |
| manual | RT-07, RT-13–15, RT-20, RT-24–25, RT-28 | Human verification / external pentest |

- [ ] **RT-29** Click/Payme webhooks reject invalid signatures — *automated*
- [ ] **RT-30** JWT access token revoked on logout — *automated + P-05 pentest*

## External pentest

Full scenario list: `docs/pentest-checklist.md`

## Authentication & Session

- [ ] **RT-01** Password login rate-limited (10/account, 30/IP per 5 min) — *CI*
- [ ] **RT-02** Refresh token reuse revokes entire family — *CI*
- [ ] **RT-03** MFA enforced for super_admin, hokimiyat_operator, center_director — *automated*
- [ ] **RT-04** JWT uses RS256; private key not in repo or env — *automated*
- [ ] **RT-05** Access token expires in 15 minutes — *automated*
- [ ] **RT-06** Parent OTP expires in 5 minutes, max 5 attempts — *CI*

## Authorization & Tenant Isolation

- [ ] **RT-07** Center A director cannot read Center B students (IDOR test) — *manual pentest*
- [ ] **RT-08** Teacher cannot access admin endpoints — *CI*
- [ ] **RT-09** Parent sees only linked guardian children — *CI*
- [ ] **RT-10** RLS policies active (FORCE) on students, enrollments, certificates, guardians — *CI*
- [ ] **RT-11** PINFL reveal requires auditor role + audit log entry — *CI*

## Data Protection

- [ ] **RT-12** PINFL stored encrypted at rest — *CI*
- [ ] **RT-13** PINFL masked in API responses by default — *manual*
- [ ] **RT-14** No PINFL in AI analytics service queries — *CI*
- [ ] **RT-15** Production errors return generic `INTERNAL_ERROR` only — *live check*
- [ ] **RT-16** No demo accounts remain (`./scripts/pre-deploy-check.sh` passes) — *automated*

## Public Endpoints

- [ ] **RT-17** Certificate verify rate-limited (10/min/IP) — *CI / live*
- [ ] **RT-18** Certificate tamper (modified integrity_hash) rejected — *CI*
- [ ] **RT-19** SSRF blocked on outbound integrations (internal IP ranges) — *automated*

## Infrastructure

- [ ] **RT-20** TLS 1.2+ only; HSTS with preload — *manual CA certs + `--production` check*
- [ ] **RT-21** Nginx rate limits on login and verify endpoints — *automated*
- [ ] **RT-22** Container images signed (Cosign workflow) — *CI*
- [ ] **RT-23** Secrets from Vault, not plaintext in compose files — *automated*
- [ ] **RT-24** Database not exposed to public internet — *infra review*

## Operational

- [ ] **RT-25** Incident response roles assigned (Section 17A.6) — *organizational*
- [ ] **RT-26** Backup/restore tested for PostgreSQL — *run scripts on prod host*
- [ ] **RT-27** `purge_demo_data.py` executed and verified — *`./scripts/go-live.sh`*
- [ ] **RT-28** Load test baseline recorded (`scripts/load_test.py`) — *manual record*

## Sign-Off

Complete after all checks pass. External pentest report attached before final signature.

| Role | Name | Date | Signature |
|------|------|------|-----------|
| District IT Lead | | | |
| Security Reviewer | | | |
| Hokimlik Representative | | | |
