# ADR 0004: Locale-Suffixed Columns for Structured Entities

## Status
Accepted

## Decision

Store structured user-facing entity names in locale-suffixed columns (`name_uz`, `name_ru`, `name_en`) and reserve the `translations` table for templated system content such as notifications and certificate/report copy.

## Rationale

District reporting and administrative SQL queries benefit from explicit columns that are easy to index, export, validate, and inspect. JSONB would reduce schema width but complicates routine reporting and makes accidental partial population easier. Templated content, however, benefits from a table-based storage model because it is dynamic and versionable. This keeps each category of translatable data in the storage form that best fits its access pattern.
