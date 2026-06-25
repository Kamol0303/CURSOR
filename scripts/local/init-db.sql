-- PostgreSQL init (Docker siz, bir marta)
-- Git Bash: psql -U postgres -f scripts/local/init-db.sql

CREATE USER tamor WITH PASSWORD 'tamor_dev';
CREATE DATABASE tamor OWNER tamor;
GRANT ALL PRIVILEGES ON DATABASE tamor TO tamor;
