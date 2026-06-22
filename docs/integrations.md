# TaMoR External Integrations

## SMS — eskiz.uz

| Environment | Behavior |
|-------------|----------|
| `development`, `test` | Stub — OTP printed to backend logs |
| `staging`, `production` | Live API when `ESKIZ_EMAIL`/`ESKIZ_PASSWORD` or `ESKIZ_API_TOKEN` set |

Configure in `.env.production` or `.env.staging`. See `backend/app/integrations/sms_adapter.py`.

## Email — not yet implemented

Email notifications are **stub-only**. `send_email()` returns success in dev/test and fails in production/staging:

```
SMTP integration not enabled
```

**Workaround until SMTP is built:** rely on in-app notifications and SMS for critical alerts.

To implement later: configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` and complete `email_adapter.py`.

## Telegram bot

Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_WEBHOOK_SECRET`. Webhook: `POST /api/v1/integrations/telegram/webhook`.

## AI analytics microservice

Read-only PostgreSQL role without PINFL column access (RT-14). JWT RS256 service-to-service auth.

## Regional statistics API

Outbound calls use SSRF-safe `http_client.py` — internal IPs blocked.
