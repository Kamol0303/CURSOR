# ADR-002: Hybrid Locale Routing

## Status
Accepted

## Context
Public pages (certificate verification) benefit from URL-segmented locales for SEO. Authenticated app shell benefits from cookie-based locale without URL churn.

## Decision
**Hybrid approach:** URL segments (`/uz/`, `/ru/`, `/en/`) for public pages; cookie `NEXT_LOCALE` + user `locale_preference` for authenticated routes.

## Consequences
- Public verification page is indexable per locale
- Authenticated users switch language without route change
- Slightly more i18n configuration complexity
