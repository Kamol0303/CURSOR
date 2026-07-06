# TMB — Платформа мониторинга и управления образованием

**Языки:** [English](README.md) · [O'zbek](README.uz.md) · [Русский](README.ru.md)

Государственная платформа мониторинга и управления образованием для **Тойлокского района**, Самаркандская область, Узбекистан.

---

## Итоговый статус (июль 2026)

| Область | Готовность | Примечание |
|---------|------------|------------|
| **Код приложения** | **~100%** | Фазы 0–7, OCMS, панель хокимията, ИИ, аудит |
| **Безопасность (авто)** | **12/12 пройдено** | `python3 scripts/red_team_verify.py --offline` |
| **Go-live (инфра)** | **~85%** | Vault, CA TLS, сервер в УЗ, подпись внешнего pentest |

Полный отчёт: [`docs/security-audit-report.md`](docs/security-audit-report.md)  
Чеклист go-live: [`docs/production-100-checklist-uz.md`](docs/production-100-checklist-uz.md)

---

## Основные возможности

- **RBAC** — 10+ ролей, PostgreSQL RLS, изоляция тенантов
- **Оператор хокимията** — панель только для мониторинга (6 пунктов меню)
- **Сертификаты** — QR-проверка, хеш целостности, `/verify`
- **ИИ** — генератор тестов + материалы урока (презентация / игра в классе)
- **LLM-цепочка** — BazaarLink → Gemini → Mistral (автоматический fallback)
- **Журнал аудита** — `/dashboard/audit` — кто, когда и что изменил
- **Production** — `Dockerfile.prod`, `docker-compose.prod.yml`, Nginx TLS

---

## Проверка безопасности

```bash
# Автоматический red-team (сервер не нужен)
python3 scripts/red_team_verify.py --offline

# Staging / production
python3 scripts/red_team_verify.py --url https://tamor.toyloq.uz --production

# Интеграционные тесты (нужен PostgreSQL)
cd backend && pytest tests/security/ -v
```

**Последний offline-результат:** 12/12 автоматических проверок пройдено.

**Перед production:** подпись внешнего pentest (`docs/red-team-checklist.md`), CA TLS, Vault, очистка demo-данных.

---

## Быстрый старт (Docker)

```bash
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

- Frontend: http://localhost:3000  
- API: http://localhost:8000

### Настройка LLM (`.env` — не коммитьте ключи!)

```env
LLM_API_KEY=sk-bl-...              # BazaarLink (основной)
GEMINI_API_KEY=...                 # резерв 1
MISTRAL_API_KEY=...                # резерв 2
AI_ENABLED=true
```

Windows: `scripts\windows\setup-llm-env.cmd`

---

## Демо-учётные записи (только development)

| Роль | Логин | Пароль |
|------|-------|--------|
| Super Admin | `admin.tmb` | `Tmb#2026Admin!` |
| Оператор хокимията | `operator.hokimiyat` | `Hokim#Op2026!` |
| Админ центра | `admin.aspect` | `CenterAdmin#26!` |
| Учитель | `teacher.dilnoza` | `Teach#Dil2026!` |
| Ученик | `student.sardor` | `Student#2026!` |

---

## Production go-live

```bash
cp .env.production.example .env.production
./scripts/go-live.sh
```

Windows: `scripts\windows\go-live-prep.cmd`  
Проверка сборки: `scripts\windows\verify-prod-build.cmd`

---

## Документация

| Документ | Назначение |
|----------|------------|
| [`docs/threat-model.md`](docs/threat-model.md) | STRIDE-модель угроз |
| [`docs/red-team-checklist.md`](docs/red-team-checklist.md) | Чеклист 24A |
| [`docs/go-live-runbook.md`](docs/go-live-runbook.md) | Развёртывание production |
| [`docs/security-audit-report.md`](docs/security-audit-report.md) | Результаты аудита |

---

## Лицензия

Государственный проект — хокимият Тойлокского района.
