# TaMoR System Requirements Specification (SRS) — Phase 0

## 1. Authentication Requirements

### 1.1 Password Policy (AUTH-PWD)
- Minimum 12 characters with uppercase, lowercase, digit, special character
- Checked against breached-password blocklist (top 100k static list)
- bcrypt cost 12 or argon2id hashing
- Password history: reject last 5 passwords
- Forced rotation: Super Admin/Director 90 days; others 180 days
- Lockout: 5 failed attempts → 15-minute lockout with exponential backoff

### 1.2 JWT Lifecycle (AUTH-JWT)
- Access token: JWT RS256, 15-minute expiry
- Refresh token: opaque, 7-day expiry, httpOnly Secure SameSite=Strict cookie
- Refresh rotation with family_id replay detection
- Claims: sub, role, center_id, permissions, locale, iat, exp, jti

### 1.3 MFA (AUTH-MFA)
- Mandatory: Super Admin, Hokimiyat Operator, Center Director
- Optional: Center Admin, Teacher, Auditor
- TOTP primary (RFC 6238); SMS-OTP fallback
- 10 backup recovery codes, hashed storage
- TOTP secret encrypted at rest

### 1.4 Parent Login (AUTH-PARENT)
- Phone number + SMS-OTP (passwordless)
- Dev mode: OTP logged to console

### 1.5 External API (AUTH-API)
- API key + HMAC-SHA256 request signing
- Scoped to aggregate_stats.read, 10 req/min
- 24-hour key rotation grace window

## 2. Internationalization Requirements

### 2.1 Locales
- uz (default), ru, en
- Uzbek Cyrillic explicitly excluded (ADR-004)

### 2.2 Switching
- Persistent switcher on all screens including login
- No full page reload after initial bundle cache
- Intl.NumberFormat and Intl.DateTimeFormat for numbers/dates
- ICU pluralization (Russian 1/2-4/5+ forms)
- Backend returns error codes, not prose

## 3. API Requirements

- REST `/api/v1/...`
- Standard response envelope with success/data/meta/error
- Pagination: page/per_page
- Rate limiting per role
- OpenAPI auto-generated documentation

## 4. Database Requirements

- PostgreSQL 15+
- UUID primary keys
- Soft delete via deleted_at
- Monthly partitioning for audit_logs, login_audit_log
- Trilingual name columns (name_uz, name_ru, name_en)

## 5. Security Requirements

- TLS 1.2+ for all traffic
- PINFL encrypted at rest, masked by default
- Audit log on sensitive field reads (PINFL reveal)
- CSRF protection, CSP headers
- File uploads via encrypted MinIO with signed URLs

## 6. Phase 0 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/login | Username/password login |
| POST | /api/v1/auth/login/otp/request | Parent OTP request |
| POST | /api/v1/auth/login/otp/verify | Parent OTP verify |
| POST | /api/v1/auth/mfa/verify | TOTP verification step |
| POST | /api/v1/auth/refresh | Refresh token rotation |
| POST | /api/v1/auth/logout | Revoke refresh token |
| GET | /api/v1/auth/me | Current user profile |
| POST | /api/v1/auth/mfa/setup | MFA enrollment |
| POST | /api/v1/auth/password/change | Password change |
| GET | /api/v1/health | Health check |
