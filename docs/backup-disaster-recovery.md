# TaMoR Backup and Disaster Recovery Plan

## Recovery Objectives

| Metric | Target |
|--------|--------|
| RPO (Recovery Point Objective) | ≤ 1 hour |
| RTO (Recovery Time Objective) | ≤ 4 hours |

## Backup Strategy

### PostgreSQL
- **Daily full backup**: `pg_dump` at 02:00 UTC, encrypted with GPG, stored off-site
- **Hourly WAL archiving**: Continuous WAL shipping for point-in-time recovery (PITR)
- **Retention**: 30 daily full backups, 7 days hourly WAL

### MinIO (File Storage)
- **Daily sync**: `mc mirror` to secondary MinIO instance or S3-compatible off-site bucket
- **Encryption**: Server-side encryption (SSE-S3) enabled

### Redis
- **RDB snapshots**: Every 15 minutes (acceptable data loss for cache/session in DR scenario)
- Redis is reconstructable from PostgreSQL; not critical for RPO

## Backup Encryption

All backups encrypted at rest using AES-256-GPG before transfer to off-site storage. Encryption keys stored in secrets manager, separate from backup storage.

## Restore Procedure

1. Provision replacement PostgreSQL instance
2. Restore latest full backup: `pg_restore -d tamor latest.dump`
3. Replay WAL archives to target timestamp: `pg_wal_replay`
4. Verify encrypted fields decrypt correctly (PINFL, TOTP secrets)
5. Restore MinIO files from mirror
6. Update DNS/load balancer to point to restored infrastructure
7. Run health checks and smoke tests (login flow, API reads)

## Quarterly Restore Testing

Every quarter, perform a full restore to an isolated staging environment:
- Verify database integrity (row counts, FK constraints)
- Verify encrypted field decryption
- Verify auth tables (users, refresh_tokens, sessions)
- Document restore time and any issues

## Pre-Production Checklist

- [ ] Configure automated backup cron jobs
- [ ] Verify off-site backup storage is in Uzbekistan
- [ ] Test one full restore before go-live
- [ ] Document on-call restore runbook
