# TMB Staging Deployment Guide (HTTPS / production-like)

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
```

`.env.staging` faylini to'ldiring (gitga kirmaydi):
- `POSTGRES_PASSWORD`, `TOTP_ENCRYPTION_KEY`, `PINFL_ENCRYPTION_KEY` (32+ belgi)
- `TELEGRAM_BOT_TOKEN`, `SMTP_*` (ixtiyoriy)
- `PUBLIC_HOST=tamor.staging.local`

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

Uploaded files (student photos, certificate documents) persist in Docker volume `upload_staging` (`FILE_UPLOAD_DIR=/data/uploads`).

**Important:** After a fresh deploy or `down -v`, seed demo users before logging in:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging exec -T backend \
  python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials

./scripts/test-login.sh
```

Quick login (no MFA): `admin.aspect` / `CenterAdmin#26!`  
MFA admin: `admin.tmb` / `Tmb#2026Admin!` → scan QR from seed output or:

```bash
chmod +x scripts/show-mfa-qr.sh
./scripts/show-mfa-qr.sh admin.tmb
```

Seed prints an ASCII QR in the terminal for each MFA user — scan with Google Authenticator.

If QR does not appear after seed, rebuild backend so the container has the latest scripts:

```bash
git pull origin CURSOR/fix-postgres-staging-ccd9
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build backend
./scripts/show-mfa-qr.sh admin.tmb
```

### MFA kod noto'g'ri (xato deyapti)

1. **Seed har safar yangi secret yaratmasin** — oddiy seed eski secretni saqlaydi. Yangilash kerak bo'lsa:
   ```bash
   docker compose ... exec -T backend python scripts/seed_demo_users.py \
     --i-understand-this-creates-demo-credentials --rotate-mfa-secrets
   ```
2. Google Authenticator dan **eski TMB yozuvini o'chiring**, keyin `./scripts/show-mfa-qr.sh admin.tmb` QR ni qayta skanerlang.
3. `Hozirgi kod` qatoridagi 6 raqam Authenticator dagi kod bilan **bir xil** bo'lishi kerak.
4. Test: `chmod +x scripts/test-mfa-login.sh && ./scripts/test-mfa-login.sh`

## 5. Seed demo users (staging only)

See commands in step 4 above if you skipped seeding after deploy.

## Architecture

| Layer | Config |
|-------|--------|
| Nginx | `server_name tamor.staging.local localhost` |
| HTTP :80 | 301 → HTTPS |
| HTTPS :443 | Proxy → `frontend:3000`, `backend:8000` |
| Cookies | `Secure` + `HttpOnly` (ENVIRONMENT=staging) |
| API URL | `https://tamor.staging.local` |

## Troubleshooting

### Postgres unhealthy / backend not running

After `down -v`, postgres must re-initialize. If you see:

```
dependency failed to start: container cursor-postgres-1 is unhealthy
```

1. Check postgres logs:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging logs postgres --tail 50
```

2. Ensure `.env.staging` has `POSTGRES_PASSWORD` and `DATABASE_URL` uses the **same** password.

3. Pull latest code (init script + migration fix), wipe volumes, rebuild:

```bash
git pull origin CURSOR/fix-postgres-staging-ccd9
docker compose -f docker-compose.staging.yml --env-file .env.staging down -v
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build
```

4. Wait until postgres is healthy, then seed:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging ps
docker compose -f docker-compose.staging.yml --env-file .env.staging exec -T backend \
  python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

5. Run diagnostics: `./scripts/diagnose-staging.sh`

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
