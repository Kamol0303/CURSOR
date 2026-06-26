# ADR-003: Translation Column Strategy

## Status
Accepted

## Context
User-facing entity names must display in UZ/RU/EN. Options: separate columns vs JSONB locale map.

## Decision
Use **separate columns** (`name_uz`, `name_ru`, `name_en`) for database entities. Static UI strings use `next-intl` JSON files per module.

## Consequences
- Explicit schema; easy SQL filtering per locale
- More columns than JSONB; acceptable for three fixed locales
