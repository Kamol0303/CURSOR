# ADR-003: Separate Translation Columns (name_uz, name_ru, name_en)

## Status
Accepted

## Context
Database entities with user-facing names need trilingual support. Options: separate columns vs JSONB locale map.

## Decision
Use **separate columns** (`name_uz`, `name_ru`, `name_en`) for all translatable entity names (roles, subjects, mahallas, etc.).

## Justification
- Explicit schema enables per-locale indexing and NOT NULL constraints.
- SQL queries and reports can select specific locale without JSON parsing.
- Type safety in SQLAlchemy models is clearer.
- Static UI strings remain in JSON locale files (`auth.json`, `students.json`).

## Consequences
- Adding a fourth locale requires migration; acceptable for v1 (UZ/RU/EN fixed scope).
