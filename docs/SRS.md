# System Requirements Specification (SRS)

## 1. Functional requirements in Phase 0

### 1.1 Authentication

- Username/password login for Super Admin, Hokimiyat Operator, Center Director, Center Admin, Teacher, and Auditor.
- Parent/guardian phone + OTP login.
- External API consumer authentication with API key + HMAC request signing.
- Server-side password policy with composition rules, history checks, and breach-list rejection.
- Account lockout after five failed attempts with increasing lockout duration.
- RS256 access tokens with fifteen-minute lifetime.
- Opaque refresh tokens stored hashed and rotated on each refresh.
- MFA enrollment and challenge verification using TOTP.
- Backup recovery code support.

### 1.2 Authorization

- Role and permission tables.
- Permission guard dependency for API routes.
- Center-scoped claims for tenant-safe access decisions.

### 1.3 Internationalization

- Supported locales: `uz`, `ru`, `en`
- Permanent language switcher on public and authenticated pages
- Locale preference persistence
- Locale-aware formatting with `Intl` APIs in the frontend shell

### 1.4 Platform scaffolding

- Alembic migration baseline
- Docker Compose environment
- CI for backend and frontend validation
- Architecture, security, ER, and ADR documentation

## 2. Non-functional requirements

- Sensitive credential and MFA material never stored in plaintext.
- API responses use stable error codes instead of localized prose.
- Core auth paths have automated tests.
- Repo structure must support independent backend/frontend/microservice evolution.
- Default deployment architecture targets Uzbekistan-resident infrastructure.

## 3. Out-of-scope for Phase 0

- Full CRUD for centers, students, teachers, and reports
- Rating computation jobs
- AI analytics service implementation
- Production SMS gateway and PKI integrations
- Complete parent portal and public verification workflow

These are intentionally deferred to Phase 1 and later phases, while the foundational schema keeps space for them.
