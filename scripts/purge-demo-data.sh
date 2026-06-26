#!/usr/bin/env bash
# Purge demo data before production go-live (wrapper for backend container script)
set -euo pipefail

COMPOSE="docker compose -f docker-compose.prod.yml --env-file .env.production"
exec $COMPOSE exec -T backend python scripts/purge_demo_data.py "$@"
