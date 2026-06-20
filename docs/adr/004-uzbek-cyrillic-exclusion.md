# ADR-004: Uzbek Cyrillic Exclusion from v1

## Status
Accepted

## Context
Some district staff may expect Uzbek in Cyrillic script. v1 targets Latin Uzbek, Russian, and English.

## Decision
**Uzbek Cyrillic is out of scope for v1.** Supported locales: `uz` (Latin), `ru`, `en`.

## Consequences
- Reduced translation surface for MVP
- May revisit in Phase 4+ based on user feedback
