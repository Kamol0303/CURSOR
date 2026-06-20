# Business Requirements Document (BRD)

## 1. Executive summary

TaMoR is a district-scale platform for monitoring educational centers, measuring performance, and improving public trust through transparent reporting and certificate verification. The primary customer is the Toyloq district administration, with an architecture that must scale to region and republic levels without a rewrite.

## 2. Business goals

1. Digitize oversight of public and private educational centers.
2. Replace anecdotal decision-making with verifiable statistics and trends.
3. Publish trustworthy rating signals for parents and the public.
4. Reduce operational risk around sensitive student data and district reporting.
5. Prepare the platform for multi-tenant expansion.

## 3. Stakeholders

- District administration leadership
- District IT department
- Hokimiyat operators
- Center directors and center administrators
- Teachers
- Auditors
- Parents/guardians
- External aggregate-statistics consumers

## 4. Phase 0 scope

Phase 0 establishes the foundation required before functional modules can scale safely:

- Core architecture and repo structure
- PostgreSQL schema and migration baseline
- Authentication and authorization system for all eight roles
- JWT + refresh-token lifecycle
- MFA for mandatory roles
- Demo seed data and non-production-only credentials bootstrap
- Frontend i18n shell for Uzbek, Russian, and English
- CI/CD scaffolding and local deployment path
- Architecture, security, and ADR documentation

## 5. Non-functional priorities

- Security-first handling of minors' data and PINFL/JSHSHIR
- Trilingual runtime UX
- Auditability of sign-in and sensitive data access
- Multi-tenant-ready domain modeling
- Observable and testable delivery pipeline

## 6. Success measures for Phase 0

- All required demo identities can authenticate through real backend flows.
- Mandatory-MFA roles complete TOTP challenge before session issuance.
- Parent OTP login works in development through console-logged OTP flow.
- Refresh-token rotation and reuse detection are covered by tests.
- Locale switch works on public and authenticated pages without full-page refresh.
- The repository can be bootstrapped locally through documented setup instructions.
