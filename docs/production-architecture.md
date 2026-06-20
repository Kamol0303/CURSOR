# TaMoR Production Architecture

```mermaid
flowchart TB
    subgraph clients [Clients]
        Browser[Web Browser]
        Mobile[PWA Mobile]
        ExtAPI[External API Consumer]
    end

    subgraph edge [Edge Layer]
        Nginx[Nginx Reverse Proxy + TLS]
    end

    subgraph app [Application Layer]
        Frontend[Next.js Frontend :3000]
        Backend[FastAPI Backend :8000]
        AI[AI Analytics Service :8001]
        Celery[Celery Workers]
        Beat[Celery Beat]
    end

    subgraph data [Data Layer]
        PG[(PostgreSQL 15)]
        Redis[(Redis)]
        MinIO[(MinIO S3)]
    end

    subgraph observability [Observability]
        Prom[Prometheus]
        Graf[Grafana]
        Loki[Loki]
        Sentry[Sentry]
    end

    Browser --> Nginx
    Mobile --> Nginx
    ExtAPI --> Nginx
    Nginx --> Frontend
    Nginx --> Backend
    Nginx --> AI
    Backend --> PG
    Backend --> Redis
    Backend --> MinIO
    AI --> PG
    AI --> Redis
    Celery --> PG
    Celery --> Redis
    Beat --> Celery
    Backend --> Prom
    AI --> Prom
    Prom --> Graf
    Backend --> Loki
    Backend --> Sentry
```

## Service Responsibilities

| Service | Port | Responsibility |
|---------|------|----------------|
| frontend | 3000 | Next.js SSR/SPA, i18n, girih design system |
| backend | 8000 | REST API, auth, RBAC, business logic |
| ai-analytics | 8001 | ML predictions, trend analysis (JWT verify only) |
| celery-worker | — | Background jobs: ratings, reports, notifications |
| celery-beat | — | Scheduled tasks: daily rating recompute at 03:00 |
| postgres | 5432 | Primary data store |
| redis | 6379 | Cache, sessions, rate limits, Celery broker |
| minio | 9000 | Encrypted file storage (licenses, diplomas) |
| nginx | 80/443 | SSL termination, reverse proxy |

## Deployment Environments

| Environment | Purpose | Database |
|-------------|---------|----------|
| development | Local Docker Compose | Local PostgreSQL |
| staging | Pre-production testing | Staging PostgreSQL |
| production | Live district deployment | Production PostgreSQL (Uzbekistan DC) |

## Disaster Recovery

- RPO ≤ 1 hour (hourly WAL backups)
- RTO ≤ 4 hours
- Daily full backup + encrypted off-site storage
- Quarterly restore testing
