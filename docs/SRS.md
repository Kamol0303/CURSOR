# TMB System Requirements Specification (SRS) — Phase 0

## 1. Authentication (Section 2)
- RS256 JWT access tokens (15 min)
- Opaque refresh tokens with rotation (7 days, httpOnly cookie)
- argon2id password hashing
- TOTP MFA for privileged roles
- Per-IP and per-account rate limiting
- Constant-time login path

## 2. Authorization
- 8 roles with permission matrix
- Server-side `@requires_permission` enforcement
- Tenant scoping via `center_id`

## 3. Internationalization
- Locales: uz (default), ru, en
- Runtime language switching without page reload
- Error codes from API, localized in frontend

## 4. Non-Functional
- API p95 < 300ms (target)
- 99.5% uptime (target)
- 500 concurrent users (design capacity)

## 5. Security
- STRIDE threat model (docs/threat-model.md)
- OWASP ASVS Level 2 (Level 3 for auth/crypto/audit)
- Incident response runbook (docs/incident-response.md)
