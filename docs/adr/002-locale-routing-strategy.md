# ADR-002: Hybrid Locale Routing (URL-Segmented Public + Cookie Authenticated)

## Status
Accepted

## Context
Public certificate verification pages benefit from SEO-friendly locale URLs. Authenticated app shell benefits from simpler routing without locale segments in every internal link.

## Decision
- **Public pages** (`/verify`, landing): URL-segmented — `/uz/verify`, `/ru/verify`, `/en/verify`.
- **Authenticated app**: Cookie-based locale (`NEXT_LOCALE` cookie) with `next-intl` middleware; routes at `/dashboard`, `/login` without locale prefix.
- All three locale bundles pre-fetched on initial load to achieve <150ms switch latency.

## Consequences
- SEO-friendly public pages; simpler internal navigation.
- Middleware must handle both routing strategies.
