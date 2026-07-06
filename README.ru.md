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

## Требования

| Инструмент | Windows | macOS | Linux-сервер |
|------------|---------|-------|--------------|
| **Docker** | [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Docker Desktop for Mac | Docker Engine + Compose plugin |
| **Git** | Git for Windows | Xcode CLI или Homebrew `git` | `apt install git` / `dnf install git` |
| **Node.js 20+** | Опционально (локальный frontend) | Опционально | Опционально |

---

## Запуск проекта

### Windows (development)

**1. Клонирование репозитория**

```cmd
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**2. Файл окружения и LLM-ключи**

```cmd
copy .env.example .env
scripts\windows\setup-llm-env.cmd
```

**3. Запуск полного dev-стека** (обновляет `main`, собирает Docker, миграции, seed)

```cmd
scripts\windows\update-main.cmd
```

**4. Показать демо-логины**

```cmd
scripts\windows\show-credentials.cmd
```

| URL | Адрес |
|-----|-------|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

**Windows — staging (HTTPS, локально)**

```cmd
scripts\windows\setup-staging-env.cmd
bash infra/nginx/generate-dev-certs.sh
scripts\windows\staging-up.cmd
```

Добавьте в `C:\Windows\System32\drivers\etc\hosts`: `127.0.0.1 tamor.staging.local`  
Откройте: https://tamor.staging.local

**Windows — полезные команды**

```cmd
scripts\windows\backend-logs.cmd              REM логи backend (dev)
scripts\windows\backend-logs.cmd staging      REM логи backend (staging)
docker compose down                           REM остановить dev
docker compose down -v                        REM остановить dev + очистить БД
docker compose logs backend --tail 80           REM последние строки backend
```

**Windows — подготовка production** (локальный тест prod-сборки; реальный prod — на Linux)

```cmd
copy .env.production.example .env.production
REM Отредактируйте .env.production — заполните все CHANGE_ME
scripts\windows\go-live-prep.cmd
scripts\windows\verify-prod-build.cmd
```

> Если `docker info` выдаёт ошибку: откройте **Docker Desktop** из меню Пуск и дождитесь зелёного кита в трее (2–3 минуты).

---

### macOS (development)

**1. Клонирование и настройка**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
cp .env.example .env
# Отредактируйте .env — LLM_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY (опционально)
```

**2. Запуск одной командой** (рекомендуется)

```bash
chmod +x scripts/start.sh scripts/restart-fresh.sh
./scripts/start.sh dev
```

**3. Или запуск вручную**

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

| URL | Адрес |
|-----|-------|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

**macOS — staging (HTTPS, локально)**

```bash
./scripts/start.sh staging
# Добавьте в /etc/hosts: 127.0.0.1 tamor.staging.local
sudo sh -c 'echo "127.0.0.1 tamor.staging.local" >> /etc/hosts'
open https://tamor.staging.local
```

**macOS — полезные команды**

```bash
docker compose down                    # остановить dev
docker compose down -v                 # остановить + очистить БД
./scripts/restart-fresh.sh dev         # полный сброс и перезапуск
docker compose logs backend --tail 80  # последние строки backend
./scripts/show-mfa-qr.sh               # MFA QR для admin.tmb
```

---

### Linux (development)

Те же команды, что и на macOS. Нужны Docker Engine и Compose plugin:

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER   # выйдите и войдите снова
```

**Linux (Kali/Ubuntu) — самый простой способ:**

```bash
chmod +x scripts/linux-dev-setup.sh
./scripts/linux-dev-setup.sh
```

Скрипт останавливает production-стек, проверяет конфликт портов и запускает dev.

---

### Linux-сервер (production)

Запуск на production VPS (например, `tamor.toyloq.uz`). Используются `docker-compose.prod.yml` и `.env.production`.

**1. Клонирование и секреты**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
cp .env.production.example .env.production
nano .env.production   # заполните ВСЕ CHANGE_ME: пароль БД, JWT secret, LLM-ключи и т.д.
```

**2. TLS-сертификаты от CA** (не dev self-signed)

```bash
# Разместите CA-сертификаты:
#   infra/nginx/tls/fullchain.pem
#   infra/nginx/tls/privkey.pem
ls -la infra/nginx/tls/
```

**3. Go-live** (сборка, миграции, очистка demo, pre-deploy, проверка)

```bash
chmod +x scripts/go-live.sh scripts/verify-prod.sh
./scripts/go-live.sh
```

Неинтерактивная очистка (CI / автоматизация):

```bash
GO_LIVE_PURGE=yes ./scripts/go-live.sh
```

**4. Проверка после деплоя**

```bash
PUBLIC_HOST=tamor.toyloq.uz ./scripts/verify-prod.sh
python3 scripts/red_team_verify.py --url https://tamor.toyloq.uz --production
```

**Linux-сервер — управление production**

```bash
# Статус
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# Логи
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f backend

# Перезапуск
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Миграции после обновления
docker compose -f docker-compose.prod.yml --env-file .env.production \
  exec backend alembic upgrade head

# Остановка
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

**Linux-сервер — staging**

```bash
cp .env.staging.example .env.staging
nano .env.staging
bash infra/nginx/generate-dev-certs.sh   # или реальные сертификаты для staging-хоста
./scripts/start.sh staging
./scripts/verify-staging.sh
```

---

### Настройка LLM (все платформы)

Добавьте в `.env` (dev) или `.env.production` (prod). **Не коммитьте реальные ключи в git!**

```env
LLM_API_KEY=sk-bl-...              # BazaarLink (основной)
GEMINI_API_KEY=...                 # резерв 1
MISTRAL_API_KEY=...                # резерв 2
AI_ENABLED=true
```

| Платформа | Вспомогательный скрипт |
|-----------|------------------------|
| Windows | `scripts\windows\setup-llm-env.cmd` |
| macOS / Linux | Редактировать `.env` вручную |

После изменения `.env` перезапустите стек:

```bash
docker compose up -d --build          # dev
# или
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build  # prod
```

---

## Устранение неполадок

### Использовали Windows-команды на Linux?

На **Linux/macOS** используйте `cp` (не `copy`) и прямые слэши:

```bash
cp .env.example .env
./scripts/linux-dev-setup.sh    # рекомендуется для Kali/Ubuntu/Debian
# или
./scripts/start.sh dev
```

Windows-скрипты `.cmd` (`scripts\windows\...`) работают **только на Windows**.

### `backend is unhealthy` в production

Production требует полностью настроенный `.env.production`:

- Реальные пароли (не `CHANGE_ME_...`)
- **HashiCorp Vault** (`VAULT_ADDR` + `VAULT_TOKEN`)
- JWT-ключи в `/secrets/`
- CA TLS-сертификаты в `infra/nginx/tls/`
- Ключи платёжных систем (`CLICK_*`, `PAYME_*`)

**На локальном ПК (Kali, Ubuntu) используйте dev, а не production:**

```bash
./scripts/linux-dev-setup.sh
```

Логи backend:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs backend --tail 100
```

### `port 5432 is already allocated`

Порт 5432 занят другим PostgreSQL. Решение:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production down 2>/dev/null || true
docker compose down --remove-orphans
sudo systemctl stop postgresql
ss -tlnp | grep 5432
./scripts/linux-dev-setup.sh
```

### `orphan containers (cursor-nginx-1)`

При переключении с prod на dev:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production down --remove-orphans
docker compose down --remove-orphans
./scripts/start.sh dev
```

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
