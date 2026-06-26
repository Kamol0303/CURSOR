# ADR 0001: Monorepo for Phase 0

## Status
Accepted

## Decision

Use a monorepo containing backend, frontend, and documentation.

## Rationale

TaMoR is being built from zero with tightly coupled API, auth, and governance requirements. A monorepo simplifies coordinated review of schema changes, auth contracts, i18n behavior, CI, and architecture documentation while still allowing separate deployment units. The operational overhead of a polyrepo is not justified at this stage.
