# ADR-001: JWT Access Token + Opaque Refresh Token (Hybrid)

## Status
Accepted

## Context
TaMoR requires stateless API authentication for microservices (AI analytics must verify tokens without shared signing secrets beyond the public key), while protecting against XSS token theft.

## Decision
- **Access tokens**: JWT signed with RS256, 15-minute expiry, claims include `sub`, `role`, `center_id`, `permissions`, `locale`, `jti`.
- **Refresh tokens**: Opaque random tokens stored hashed in PostgreSQL, delivered via `httpOnly`, `Secure`, `SameSite=Strict` cookies.
- **No access token blacklisting** on logout for MVP — access tokens remain valid until natural expiry (15 min). Documented tradeoff.

## Consequences
- AI analytics microservice can verify JWTs with only the public key.
- XSS cannot steal refresh tokens (httpOnly cookie).
- Logout is not instantaneous for access tokens; acceptable for government MVP with 15-min window.
