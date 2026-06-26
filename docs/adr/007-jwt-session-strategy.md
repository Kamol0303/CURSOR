# ADR-007: JWT + Refresh Token Strategy

## Status
Accepted

## Context
Need stateless API access for microservices while protecting against XSS session theft.

## Decision
- **Access token:** JWT, RS256, 15-minute expiry, bearer header
- **Refresh token:** Opaque, httpOnly Secure SameSite=Strict cookie, 7-day expiry, rotation with family tracking
- **Emergency revocation:** Redis JWT denylist by `jti` for force-logout
- **Default:** No denylist on normal logout (access token expires naturally in 15 min)

Private signing key in Vault/KMS in production; dev uses mounted key files never committed to repo.

## Consequences
- AI microservice verifies tokens with public key only
- XSS cannot steal refresh token (httpOnly)
- 15-minute window for stolen access tokens unless denylisted
