# TaMoR Staging Deployment Guide (HTTPS / production-like)

> Use **mkcert** for trusted local HTTPS on `tamor.staging.local`

## 1. Hosts file

**Windows** (`C:\Windows\System32\drivers\etc\hosts` as Administrator):

```
127.0.0.1   tamor.staging.local
```

**WSL** (`/etc/hosts`):

```
127.0.0.1   tamor.staging.local
```

## 2. Environment

```bash
cp .env.staging.example .env.staging
# Set POSTGRES_PASSWORD, TOTP_ENCRYPTION_KEY, PINFL_ENCRYPTION_KEY (32+ chars each)
# PUBLIC_HOST=tamor.staging.local
```

## 3. TLS certificates (required)

### Option A — mkcert (recommended, trusted in browser)

```bash
chmod +x infra/nginx/generate-mkcert.sh
./infra/nginx/generate-mkcert.sh
```

Creates `infra/nginx/tls/fullchain.pem` and `privkey.pem`.

### Option B — self-signed (browser warning)

```bash
./infra/nginx/generate-dev-certs.sh
```

## 4. Deploy

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build
chmod +x scripts/verify-staging.sh
PUBLIC_HOST=tamor.staging.local ./scripts/verify-staging.sh
```

Open: **https://tamor.staging.local**

## 5. Seed demo users (staging only)

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging exec backend \
  python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

Login: `admin.tamor` / `Tamor#2026Admin!` → MFA setup → dashboard

## Architecture

| Layer | Config |
|-------|--------|
| Nginx | `server_name tamor.staging.local localhost` |
| HTTP :80 | 301 → HTTPS |
| HTTPS :443 | Proxy → `frontend:3000`, `backend:8000` |
| Cookies | `Secure` + `HttpOnly` (ENVIRONMENT=staging) |
| API URL | `https://tamor.staging.local` |

## Troubleshooting

### Nginx welcome page

Rebuild custom image:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build nginx
docker compose -f docker-compose.staging.yml exec nginx nginx -T | grep server_name
```

### Nginx won't start — TLS missing

```bash
ls -la infra/nginx/tls/
./infra/nginx/generate-mkcert.sh
docker compose -f docker-compose.staging.yml --env-file .env.staging restart nginx
```

### Login works but session lost

- Use **https://** not http://
- Check `NEXT_PUBLIC_API_URL` matches `https://tamor.staging.local`
- Rebuild frontend after env change: `docker compose ... up -d --build frontend`

### mkcert on Windows

Run `generate-mkcert.sh` inside **WSL** from the project directory.

## Before production

See `docs/go-live-runbook.md` — CA-signed certs, Vault, no demo seed.
