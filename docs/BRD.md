# TaMoR Business Requirements Document (BRD)

## 1. Executive Summary

**Project:** Education Monitoring & Rating Platform (TaMoR)  
**Client:** Toyloq District Administration (Hokimlik), Samarkand Region, Uzbekistan  
**Version:** 1.0 — Phase 0 Foundation

TaMoR unifies private and public educational centers in Toyloq District into a single digital ecosystem providing real-time oversight, transparent ratings, and public certificate verification.

## 2. Business Objectives

1. Achieve 100% digitalization of the district's non-budget education sector
2. Enable data-driven administrative decisions
3. Encourage healthy competition through transparent, tamper-evident ratings
4. Provide openness and trust via certificate verification and public ratings
5. Architect for multi-tenant scale: district → region → republic

## 3. Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| District Hokimiyat | Oversight, reporting, policy decisions |
| Center Directors | Center management, ratings visibility |
| Teachers | Student/group management |
| Parents/Guardians | Child progress, certificates |
| Auditors | Compliance review, PINFL access |
| Regional Statistics Committee | Aggregated anonymized data via API |

## 4. User Roles (8)

1. Super Admin — system configuration
2. Hokimiyat Operator — district-wide read + reports
3. Center Director — own center management
4. Center Admin — daily operations
5. Teacher — own groups/students
6. Auditor — read-only audit access
7. Parent/Guardian — own child data (phone+OTP)
8. External API Consumer — aggregate statistics only

## 5. Phase 0 Deliverables (This Release)

- [x] Architecture documentation and ADRs
- [x] Full database schema with Alembic migrations
- [x] Complete authentication system (JWT RS256 + refresh rotation + MFA)
- [x] Password policy enforcement and account lockout
- [x] Demo seed script for all 8 roles
- [x] i18n skeleton (UZ/RU/EN) with next-intl
- [x] Uzbek ornamental design system (girih pattern)
- [x] Docker Compose local development stack
- [x] CI/CD pipeline scaffold

## 6. Success KPIs

| Metric | Target |
|--------|--------|
| API p95 response time | < 300ms |
| Simple reads | < 100ms |
| Uptime | ≥ 99.5% |
| Concurrent users | ≥ 500 |
| Language switch latency | < 150ms perceived |
| Capacity | 500 centers, 50K students, 2K teachers |

## 7. Constraints

- Data localization within Uzbekistan
- PINFL/JSHSHIR encrypted at rest, masked by default
- Trilingual UI: Uzbek (Latin), Russian, English
- Government-grade security (OWASP ASVS alignment)
