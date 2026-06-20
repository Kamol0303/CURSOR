# ADR-005: Monorepo Structure

## Status
Accepted

## Context
TaMoR comprises backend API, frontend SPA, AI analytics microservice, and shared documentation.

## Decision
Single **monorepo** at repository root:
```
tamor/
├── backend/           # FastAPI main API
├── frontend/          # Next.js 14 App Router
├── ai-analytics-service/  # Python analytics microservice
├── docs/              # BRD, SRS, ADRs, diagrams
├── docker/            # Docker configs
└── .github/workflows/ # CI/CD
```

## Justification
- Atomic commits across API contract changes and frontend consumers.
- Shared Docker Compose for local dev.
- Single CI pipeline with path-filtered jobs.

## Consequences
- Larger repo; mitigated by path-filtered CI jobs per service.
