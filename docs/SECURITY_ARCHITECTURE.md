# Security Architecture

## 1. Identity model

Phase 0 implements the identity and session model across these storage areas:

- `users`
- `roles`
- `permissions`
- `role_permissions`
- `sessions`
- `refresh_tokens`
- `login_audit_log`
- `password_reset_tokens`
- `password_history`
- `mfa_recovery_codes`
- `api_keys`
- `api_key_scopes`

## 2. Authentication flow

### Back-office users

1. Username/password submission
2. Password policy and lockout checks
3. Audit log write for the attempt
4. MFA challenge for mandatory or enabled users
5. Access token issuance after successful MFA or direct login
6. Refresh token issuance as `httpOnly`, `Secure`, `SameSite=Strict` cookie

### Parent flow

1. Phone number submitted
2. Development SMS adapter writes OTP to console/logs
3. OTP challenge verification
4. Parent session issued through the same JWT/refresh model

### External API consumer

1. API key lookup
2. HMAC-SHA256 signature verification against request method, path, timestamp, and body hash
3. Endpoint-scope authorization
4. Rate-limited aggregate-only response

## 3. Cryptographic controls

- Password hashing: Argon2id
- Access tokens: RS256 JWT with fifteen-minute expiry
- Refresh tokens: 256-bit random opaque secret, DB hash only
- MFA secrets: application-layer encrypted before persistence
- Backup codes: hashed before persistence
- PINFL/JSHSHIR: reserved for encrypted-at-rest storage in Phase 1 entity services

## 4. Session and replay protection

- Refresh-token rotation on every refresh
- `family_id` links token lineage
- Reuse of a revoked token revokes the entire family and blocks silent session continuation
- Logout revokes the active refresh token; short-lived access tokens expire naturally

## 5. Audit coverage

Phase 0 records:

- Successful and failed login attempts
- MFA usage
- Session creation and refresh lineage

The schema also reserves general-purpose `audit_logs` entries for:

- Entity mutation
- Sensitive-field reveal actions such as PINFL unmasking
- Administrative settings changes

## 6. Residual risks and deferred hardening

- CSRF middleware for cookie-backed session refresh should be added when the frontend begins full write operations.
- Production SMS and PKI integrations still need provider-specific threat reviews.
- Secret management must move to Vault or cloud secret storage before production deployment.
