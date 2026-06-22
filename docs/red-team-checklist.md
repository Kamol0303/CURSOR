# TaMoR Red-Team Checklist (Section 24A)

> Execute before production go-live. Automated checks: `python scripts/red_team_verify.py --offline` (CI) or against staging URL.

| Auto | ID | Check |
|:----:|----|-------|
| CI | RT-07 | Center A director cannot read Center B students |
| CI | RT-08 | Teacher cannot reveal PINFL |
| CI | RT-09 | Parent sees only linked guardian children |
| CI | RT-10 | RLS FORCE on students, enrollments, certificates, guardians |
| CI | RT-11 | Auditor PINFL reveal returns decrypted value |
| CI | RT-17/18 | Verify rate limit + certificate tamper detection |
| ✓ | RT-03–05, RT-19, RT-21–23 | `red_team_verify.py --offline` |

## Authentication & Session

- [ ] **RT-01** Password login rate-limited (10/account, 30/IP per 5 min)
- [ ] **RT-02** Refresh token reuse revokes entire family
- [ ] **RT-03** MFA enforced for super_admin, hokimiyat_operator, center_director
- [ ] **RT-04** JWT uses RS256; private key not in repo or env
- [ ] **RT-05** Access token expires in 15 minutes
- [ ] **RT-06** Parent OTP expires in 5 minutes, max 5 attempts

## Authorization & Tenant Isolation

- [ ] **RT-07** Center A director cannot read Center B students (IDOR test)
- [ ] **RT-08** Teacher cannot access admin endpoints
- [ ] **RT-09** Parent sees only linked guardian children
- [ ] **RT-10** RLS policies active (FORCE) on students, enrollments, certificates, guardians
- [ ] **RT-11** PINFL reveal requires auditor role + audit log entry

## Data Protection

- [ ] **RT-12** PINFL stored encrypted at rest
- [ ] **RT-13** PINFL masked in API responses by default
- [ ] **RT-14** No PINFL in AI analytics service queries
- [ ] **RT-15** Production errors return generic `INTERNAL_ERROR` only
- [ ] **RT-16** No demo accounts remain (`pre_deploy_check.py` passes)

## Public Endpoints

- [ ] **RT-17** Certificate verify rate-limited (10/min/IP)
- [ ] **RT-18** Certificate tamper (modified integrity_hash) rejected
- [ ] **RT-19** SSRF blocked on outbound integrations (internal IP ranges)

## Infrastructure

- [ ] **RT-20** TLS 1.2+ only; HSTS with preload
- [ ] **RT-21** Nginx rate limits on login and verify endpoints
- [ ] **RT-22** Container images signed (Cosign workflow)
- [ ] **RT-23** Secrets from Vault, not plaintext in compose files
- [ ] **RT-24** Database not exposed to public internet

## Operational

- [ ] **RT-25** Incident response roles assigned (Section 17A.6)
- [ ] **RT-26** Backup/restore tested for PostgreSQL
- [ ] **RT-27** `purge_demo_data.py` executed and verified
- [ ] **RT-28** Load test baseline recorded (`scripts/load_test.py`)

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| District IT Lead | | | |
| Security Reviewer | | | |
| Hokimlik Representative | | | |
