# ADR 0002: RS256 JWT Access Tokens with Opaque Refresh Tokens

## Status
Accepted

## Decision

Use fifteen-minute RS256 JWT access tokens and seven-day opaque refresh tokens stored only as hashes in the database and delivered via secure cookies.

## Rationale

This balances API ergonomics, service-to-service verification, and browser security. RS256 allows the future analytics service to verify tokens using only the public key. Opaque refresh tokens avoid leaking reusable session state through client-side JavaScript and enable replay detection with token-family revocation. Short-lived access tokens intentionally expire naturally after logout rather than introducing MVP-stage blacklist complexity.
