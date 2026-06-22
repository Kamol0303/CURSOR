# ADR-001: Monorepo Structure

## Status
Accepted

## Context
TMB consists of backend API, frontend SPA, AI analytics microservice, and shared documentation. We need a repository layout that supports coordinated releases and shared CI/CD.

## Decision
Use a **monorepo** with top-level directories: `backend/`, `frontend/`, `ai-analytics-service/`, `docs/`, `infra/`.

## Consequences
- Single CI pipeline can gate all components
- Shared documentation and ADRs live alongside code
- Larger clone size; mitigated by sparse checkout in advanced workflows
