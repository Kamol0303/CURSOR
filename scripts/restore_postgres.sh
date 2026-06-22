#!/usr/bin/env bash
# PostgreSQL restore for TaMoR (RT-26) — DESTRUCTIVE
# Usage: ./scripts/restore_postgres.sh backups/tamor_YYYYMMDD.sql.gz
set -euo pipefail

BACKUP_FILE="${1:?Usage: restore_postgres.sh <backup.sql.gz>}"
: "${POSTGRES_USER:=tamor}"
: "${POSTGRES_DB:=tamor}"
: "${PGHOST:=localhost}"
: "${PGPORT:=5432}"

if [[ "${CONFIRM_RESTORE:-}" != "yes" ]]; then
  echo "ERROR: Set CONFIRM_RESTORE=yes to proceed with destructive restore" >&2
  exit 1
fi

echo "Restoring $POSTGRES_DB from $BACKUP_FILE ..."
gunzip -c "$BACKUP_FILE" | PGPASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD required}" \
  psql -h "$PGHOST" -p "$PGPORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1

echo "Restore complete."
