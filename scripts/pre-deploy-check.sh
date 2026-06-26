#!/usr/bin/env bash
# Pre-deploy safety gate (wrapper for backend container script)
set -euo pipefail

COMPOSE="docker compose -f docker-compose.prod.yml --env-file .env.production"
exec $COMPOSE exec -T backend python scripts/pre_deploy_check.py "$@"
