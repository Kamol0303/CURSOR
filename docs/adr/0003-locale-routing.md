# ADR 0003: URL-Segmented Locale Routing

## Status
Accepted

## Decision

Use URL-segmented locale routing (`/uz`, `/ru`, `/en`) for both public and authenticated screens in Phase 0, with the selected locale also persisted in the `NEXT_LOCALE` cookie and the user profile where applicable.

## Rationale

URL segmentation gives deterministic routing, clean test coverage across locales, and SEO-friendly public verification pages. It also keeps language state explicit for shared links and screenshots. The cookie still smooths repeat visits, but the route remains the primary source of truth for rendering.
