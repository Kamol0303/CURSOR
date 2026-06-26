# TMB Production Architecture

```mermaid
flowchart TB
    subgraph Internet["Untrusted: Public Internet"]
        Users[Users / Parents / Public]
    end
    subgraph DMZ["Semi-trusted: Edge"]
        Nginx[Nginx + WAF + Rate Limiter + TLS]
    end
    subgraph AppTier["Trusted: Application Tier"]
        Frontend[Next.js Frontend]
        Backend[FastAPI Backend]
        AI[AI Analytics Service]
    end
    subgraph DataTier["Highly Trusted: Data Tier"]
        PG[(PostgreSQL 15)]
        Redis[(Redis)]
        MinIO[(MinIO S3)]
        Vault[(Vault / KMS)]
    end

    Users --> Nginx
    Nginx --> Frontend
    Nginx --> Backend
    Backend --> AI
    Backend --> PG
    Backend --> Redis
    Backend --> MinIO
    Backend --> Vault
    AI --> PG
```

## Trust Boundaries
See `docs/threat-model.md` for full STRIDE analysis.

## Phase 0 Components
- Docker Compose for local dev
- GitHub Actions CI
- JWT keys generated at container start (dev); Vault in production
