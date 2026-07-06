# TMB — 100% Tayyorlik Ro'yxati

> Kod va go-live holati — oxirgi yangilanish

## Kod tayyorligi (~100%)

| Komponent | Holat | Izoh |
|-----------|-------|------|
| Auth + MFA + RBAC | ✅ | Barcha rollar, RLS, portal routing |
| Hokimiyat operator paneli | ✅ | Monitoring-only |
| AI imtihon generatori | ✅ | BazaarLink → Gemini → mock |
| AI dars materiallari | ✅ | `/teacher/lesson-start` |
| Audit jurnali | ✅ | API + `/dashboard/audit` |
| Production Docker | ✅ | `Dockerfile.prod`, `docker-compose.prod.yml` |
| Demo purge | ✅ | OCMS jadvallari bilan |
| CI + build verify | ✅ | `prod-build` job |
| i18n (uz/ru/en) | ✅ | |

## Go-live tayyorligi

### Siz bajarishingiz kerak (infratuzilma)

| # | Vazifa | Skript/hujjat |
|---|--------|---------------|
| 1 | O'zbekiston server/VPS | `docs/go-live-runbook.md` |
| 2 | CA TLS sertifikat | `infra/nginx/tls/` |
| 3 | HashiCorp Vault | `docs/adr/008-vault-secrets.md` |
| 4 | `.env.production` to'ldirish | `.env.production.example` |
| 5 | Demo purge + deploy | `./scripts/go-live.sh` |
| 6 | Pentest imzosi | `docs/red-team-checklist.md` |

### Windows ketma-ketligi

```cmd
scripts\windows\setup-llm-env.cmd
scripts\windows\update-main.cmd
scripts\windows\verify-prod-build.cmd
scripts\windows\go-live-prep.cmd
```

## LLM sozlash (ikki provayder)

`.env` faylida (gitga kirmaydi):

```env
LLM_API_KEY=sk-bl-BAZAARLINK_KALITINGIZ
LLM_BASE_URL=https://bazaarlink.ai/api/v1
LLM_MODEL=openai/gpt-4o-mini

GEMINI_API_KEY=SIZNING_GEMINI_KALITINGIZ
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
GEMINI_MODEL=gemini-2.0-flash

AI_ENABLED=true
```

**Ishlash tartibi:** BazaarLink limit tugasa → avtomatik Gemini → ikkalasi ishlamasa → mock (dev).

**Xavfsizlik:** API kalitlarni hech qachon gitga commit qilmang. Chatda yuborilgan kalitlarni provider dashboarddan yangilang.

## Tekshiruv

```bash
cd backend && pytest tests/test_llm_service.py tests/test_purge_demo_data.py -v
./scripts/verify-prod-build.sh
```
