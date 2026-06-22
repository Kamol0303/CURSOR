#!/usr/bin/env bash
# PostgreSQL backup for TaMoR (RT-26)
# Usage: ./scripts/backup_postgres.sh [output_dir]
set -euo pipefail

OUTPUT_DIR="${1:-./backups}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUTPUT_DIR"

: "${POSTGRES_USER:=tamor}"
: "${POSTGRES_DB:=tamor}"
: "${PGHOST:=localhost}"
: "${PGPORT:=5432}"

FILE="$OUTPUT_DIR/tamor_${TIMESTAMP}.sql.gz"

echo "Backing up $POSTGRES_DB to $FILE ..."
PGPASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD required}" \
  pg_dump -h "$PGHOST" -p "$PGPORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --format=plain \
  | gzip > "$FILE"

echo "Backup complete: $FILE ($(du -h "$FILE" | cut -f1))"
