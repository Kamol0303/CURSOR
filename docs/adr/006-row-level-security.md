# ADR-006: Row-Level Security (RLS)

## Status
Accepted (Phase 1 implementation)

## Context
Application-level tenant scoping (`center_id`) is the primary control. SQL injection could bypass application logic.

## Decision
**Strongly recommend PostgreSQL RLS** on `students`, `enrollments`, and `certificates` as defense-in-depth. Phase 0 establishes schema and application scoping; RLS policies added in Phase 1 before MVP security gate.

## Consequences
- Dual enforcement layer (app + DB)
- Requires session variable (`SET app.current_center_id`) set per request
- Additional migration and test complexity
