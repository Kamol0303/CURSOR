# TaMoR Security Architecture

## 1. Authentication Flow

```
┌─────────┐     POST /login      ┌─────────┐
│ Client  │ ──────────────────►  │ FastAPI │
│         │ ◄── access_token ──  │         │
│         │     (JSON body)      │         │
│         │ ◄── refresh_token ── │         │
│         │     (httpOnly cookie)│         │
└─────────┘                      └─────────┘
     │
     │  If MFA required
     ▼
┌─────────┐   POST /mfa/verify   ┌─────────┐
│ Client  │ ──────────────────►  │ FastAPI │
│         │ ◄── access_token ──  │ pyotp   │
└─────────┘                      └─────────┘
```

## 2. Token Lifecycle

| Token | Type | Storage | Expiry | Rotation |
|-------|------|---------|--------|----------|
| Access | JWT RS256 | Memory/Authorization header | 15 min | On refresh |
| Refresh | Opaque random | httpOnly cookie + DB hash | 7 days | Every refresh |
| MFA TOTP | Secret | Encrypted in DB | Persistent | On enrollment |

### Refresh Token Rotation
1. Client sends refresh cookie to `/auth/refresh`
2. Server validates hash, issues new access + refresh tokens
3. Old refresh token marked `used_at`, new token gets same `family_id`
4. If revoked token reused → entire family invalidated (replay attack)

## 3. Password Security

- **Hashing**: bcrypt cost factor 12
- **Blocklist**: Static top-100k breached passwords shipped in `backend/data/breached_passwords.txt`
- **History**: Last 5 hashes stored in `password_history` table
- **Lockout**: 5 failures → 15 min lock; exponential backoff on repeat

## 4. MFA Implementation

- **TOTP**: RFC 6238 via `pyotp`, 30-second window, ±1 step tolerance
- **Secret storage**: Fernet encryption with `TOTP_ENCRYPTION_KEY` from secrets manager
- **Backup codes**: 10 codes, bcrypt-hashed, single-use
- **Mandatory roles**: super_admin, hokimiyat_operator, center_director

## 5. PINFL/JSHSHIR Protection

- Encrypted at rest with application-layer Fernet encryption
- Default display: masked `••••••12345` (last 5 digits)
- Full reveal requires Auditor role in audit context OR logged reveal action for Super Admin
- Every reveal writes to `audit_logs` with actor, timestamp, reason

## 6. External API Authentication

```
Authorization: Tamor-HMAC key_id="...",timestamp="...",signature="..."
X-Tamor-Signature: HMAC-SHA256(timestamp + method + path + sha256(body))
```

- Rate limit: 10 req/min per key
- Scope: `aggregate_stats.read` only
- Key rotation: 24-hour grace window via `key_version`

## 7. OWASP Mitigations

| Threat | Mitigation |
|--------|------------|
| SQL Injection | SQLAlchemy ORM, parameterized queries |
| XSS | httpOnly cookies, CSP headers |
| CSRF | SameSite=Strict cookies, CSRF tokens on mutations |
| Brute Force | Account lockout + login_audit_log |
| Token Theft | Refresh rotation, family invalidation |
| Sensitive Data | Encryption at rest, role-based masking |

## 8. Logout Tradeoff (ADR-001)

Access tokens are NOT blacklisted on logout. They remain valid until natural 15-minute expiry. This is an intentional MVP tradeoff documented for security review.

## 9. Pre-Production Checklist

- [ ] Purge all `is_demo_account = true` users
- [ ] Rotate JWT RS256 key pair
- [ ] Replace TOTP_ENCRYPTION_KEY and PINFL_ENCRYPTION_KEY
- [ ] Configure real SMS gateway (replace console provider)
- [ ] Enable TLS certificates on Nginx
- [ ] Run penetration test on auth/MFA flow
- [ ] Verify PINFL masking in all API responses
