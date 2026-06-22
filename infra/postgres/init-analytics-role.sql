-- Read-only role for AI analytics microservice (no PINFL access).
-- Table/column grants run in Alembic migration 006 after schema exists.
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'tamor_analytics') THEN
        CREATE ROLE tamor_analytics WITH LOGIN PASSWORD 'tamor_dev';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE tamor TO tamor_analytics;
GRANT USAGE ON SCHEMA public TO tamor_analytics;
