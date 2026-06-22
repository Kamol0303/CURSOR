# TMB External Integrations

## SMS — eskiz.uz

| Environment | Behavior |
|-------------|----------|
| `development`, `test` | Stub — OTP printed to backend logs |
| `staging`, `production` | Live API when `ESKIZ_EMAIL`/`ESKIZ_PASSWORD` or `ESKIZ_API_TOKEN` set |

Configure in `.env.production` or `.env.staging`. See `backend/app/integrations/sms_adapter.py`.

## Email — SMTP (Gmail va boshqalar)

| Environment | Behavior |
|-------------|----------|
| `development`, `test` | Stub — logga yoziladi |
| `staging`, `production` | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` bo'lsa yuboradi |

`.env.staging` misoli:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM="TMB <your@gmail.com>"
```

Gmail uchun [App Password](https://myaccount.google.com/apppasswords) ishlating.

## Telegram bot

Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_WEBHOOK_SECRET`. Webhook: `POST /api/v1/integrations/telegram/webhook`.

## AI analytics microservice

Read-only PostgreSQL role without PINFL column access (RT-14). JWT RS256 service-to-service auth.

## Regional statistics API

Outbound calls use SSRF-safe `http_client.py` — internal IPs blocked.
