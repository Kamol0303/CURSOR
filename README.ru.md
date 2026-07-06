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

## Последние изменения (июль 2026)

| Изменение | Описание |
|-----------|----------|
| **README на 3 языках** | `README.md`, `README.uz.md`, `README.ru.md` — команды для Windows, macOS, Linux dev, Linux production |
| **`scripts/linux-dev-setup.sh`** | Kali/Ubuntu/Debian: остановка prod/staging, проверка портов, запуск dev |
| **Порт PostgreSQL в dev** | Хост-порт **5433** (не 5432) — избегает конфликта с другим Docker/системным PostgreSQL |
| **Исправление Alembic** | Цепочка `015_lesson_materials` (`014_certificate_file`); тест: `backend/tests/test_alembic_chain.py` |
| **Устранение неполадок** | Windows vs Linux, production `backend unhealthy`, порт 5432, orphan-контейнеры |
| **Браузер** | `http://localhost:3000` на **той же машине**, где Docker; preview Cursor не работает; на Linux не запускайте браузер от **root** |

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

Выберите **один** раздел для вашей платформы. Каждый блок полный — читать разделы других ОС не нужно.

| Платформа | Раздел |
|----------|--------|
| Windows (dev) | [§1 Windows — development](#1-windows--development-полный) |
| Windows (staging) | [§2 Windows — staging](#2-windows--staging) |
| Windows (prod test) | [§3 Windows — production prep](#3-windows--production-prep) |
| macOS (dev) | [§4 macOS — development](#4-macos--development-полный) |
| macOS (staging) | [§5 macOS — staging](#5-macos--staging) |
| Linux Kali/Ubuntu (dev) | [§6 Linux — development](#6-linux-kaliubuntudebian--development-полный) |
| Linux (staging) | [§7 Linux — staging](#7-linux--staging) |
| Linux VPS (production) | [§8 Linux server — production](#8-linux-server--production-полный) |

---

### 1. Windows — development (полный)

**Требования:** Windows 10/11, [Docker Desktop](https://www.docker.com/products/docker-desktop/), Git for Windows, PowerShell или CMD.

**Шаг 1 — Установка Docker Desktop**

1. Установите Docker Desktop и перезагрузите компьютер, если потребуется.
2. Откройте Docker Desktop из меню Пуск.
3. Дождитесь зелёного значка кита в трее (2–3 минуты).
4. Проверьте:

```cmd
docker info
docker compose version
```

**Шаг 2 — Клонирование проекта**

```cmd
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**Шаг 3 — Файл окружения**

```cmd
copy .env.example .env
scripts\windows\setup-llm-env.cmd
```

(Опционально) Отредактируйте `.env` в Notepad для `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`.

**Шаг 4 — Запуск dev-стека** (git pull, сборка Docker, миграции, seed)

```cmd
scripts\windows\update-main.cmd
```

**Шаг 5 — Проверка**

```cmd
docker compose ps
curl -s http://localhost:8000/health
```

Ожидаемый ответ health: `{"status":"ok","environment":"development"}`

**Шаг 6 — Открытие в браузере**

Откройте **на этом ПК**: http://localhost:3000

Учётные данные dev показываются локально (не в README):

```cmd
scripts\windows\show-credentials.cmd
```

**URL (Windows dev)**

| Сервис | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| PostgreSQL (host) | `localhost:5433` |

**Остановка / перезапуск (Windows dev)**

```cmd
docker compose down
docker compose down -v
scripts\windows\update-main.cmd
scripts\windows\backend-logs.cmd
```

> **Ошибка Docker?** Запустите Docker Desktop и дождитесь зелёного кита в трее, затем снова выполните `scripts\windows\update-main.cmd`.

---

### 2. Windows — staging

Локальный HTTPS staging с Nginx + TLS.

```cmd
cd CURSOR
scripts\windows\setup-staging-env.cmd
bash infra/nginx/generate-dev-certs.sh
scripts\windows\staging-up.cmd
```

Добавьте в `C:\Windows\System32\drivers\etc\hosts` (от имени администратора):

```
127.0.0.1 tamor.staging.local
```

Откройте: https://tamor.staging.local

Логи: `scripts\windows\backend-logs.cmd staging`

Остановка:

```cmd
docker compose -f docker-compose.staging.yml --env-file .env.staging down
```

---

### 3. Windows — production prep

Только локальный тест production-сборки. Реальный production работает на **Linux-сервере** (§8).

```cmd
cd CURSOR
copy .env.production.example .env.production
REM Edit .env.production — fill ALL CHANGE_ME values
scripts\windows\go-live-prep.cmd
scripts\windows\verify-prod-build.cmd
```

Остановка:

```cmd
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

---

### 4. macOS — development (полный)

**Требования:** macOS 12+, [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/), Git (Xcode CLI или Homebrew).

**Шаг 1 — Установка Docker**

```bash
docker --version
docker compose version
docker info
```

Откройте Docker Desktop, если `docker info` выдаёт ошибку.

**Шаг 2 — Клонирование**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**Шаг 3 — Окружение**

```bash
cp .env.example .env
nano .env
```

Установите опциональные AI-ключи: `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`, `AI_ENABLED=true`.

**Шаг 4 — Запуск (рекомендуется)**

```bash
chmod +x scripts/start.sh scripts/restart-fresh.sh
./scripts/start.sh dev
```

**Шаг 4 (альтернатива) — Ручной запуск**

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

**Шаг 5 — Проверка**

```bash
docker compose ps
curl -s http://localhost:8000/health
curl -s http://localhost:3000 | head -5
```

**Шаг 6 — Открытие в браузере**

```bash
open http://localhost:3000
```

Учётные данные dev выводятся в терминале после seed (не в README).

**URL (macOS dev)**

| Сервис | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| PostgreSQL (host) | `localhost:5433` |

**Остановка / перезапуск (macOS dev)**

```bash
docker compose down
docker compose down -v
./scripts/restart-fresh.sh dev
docker compose logs backend --tail 80
./scripts/show-mfa-qr.sh
```

---

### 5. macOS — staging

```bash
cd CURSOR
chmod +x scripts/start.sh
./scripts/start.sh staging
sudo sh -c 'echo "127.0.0.1 tamor.staging.local" >> /etc/hosts'
open https://tamor.staging.local
./scripts/verify-staging.sh
```

Остановка:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging down
```

---

### 6. Linux (Kali/Ubuntu/Debian) — development (полный)

**Требования:** Kali, Ubuntu 22.04+ или Debian 12+. Docker Engine + Compose plugin + Git.

**Шаг 1 — Установка Docker** (один раз на машине)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git curl
sudo usermod -aG docker $USER
```

Выйдите и войдите снова (или `newgrp docker`), затем проверьте:

```bash
docker info
docker compose version
```

> На Linux **не** используйте `copy` или `scripts\windows\...` — это только для Windows.

**Шаг 2 — Клонирование**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

При необходимости используйте полный путь, например `/home/YOUR_USER/CURSOR` (не `/root/CURSOR`, если вы не всегда работаете от root).

**Шаг 3 — Окружение**

```bash
cp .env.example .env
nano .env
```

Опционально: `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`.

**Шаг 4 — Запуск (рекомендуется)**

```bash
chmod +x scripts/linux-dev-setup.sh scripts/start.sh
./scripts/linux-dev-setup.sh
```

Этот скрипт: останавливает конфликты prod/staging, освобождает порты 5432/5433/6379, создаёт `.env`, запускает dev.

**Шаг 4 (альтернатива) — Ручной запуск**

```bash
docker compose down --remove-orphans 2>/dev/null || true
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

**Шаг 5 — Проверка**

```bash
docker compose ps
curl -s http://localhost:8000/health
curl -s http://localhost:3000 | head -5
```

**Шаг 6 — Открытие в браузере**

Откройте **на этой машине**: http://localhost:3000

**Не** запускайте Firefox/Chrome от `root`. Используйте обычного пользователя:

```bash
exit
firefox http://localhost:3000 &
```

Или из root-оболочки:

```bash
su - YOUR_USER -c "firefox http://localhost:3000 &"
```

Учётные данные dev выводятся в терминале после seed (не в README).

**URL (Linux dev)**

| Сервис | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| PostgreSQL (host) | `localhost:5433` |

**Остановка / перезапуск (Linux dev)**

```bash
docker compose down
docker compose down -v
./scripts/linux-dev-setup.sh
docker compose logs backend --tail 80
```

**Конфликт порта 5432?**

Dev использует хост-порт **5433**. Если запуск всё ещё не удаётся:

```bash
docker ps --format '{{.Names}} {{.Ports}}' | grep 5432
docker stop CONTAINER_NAME
sudo systemctl stop postgresql
./scripts/linux-dev-setup.sh
```

---

### 7. Linux — staging

```bash
cd CURSOR
cp .env.staging.example .env.staging
nano .env.staging
bash infra/nginx/generate-dev-certs.sh
chmod +x scripts/start.sh scripts/verify-staging.sh
./scripts/start.sh staging
echo "127.0.0.1 tamor.staging.local" | sudo tee -a /etc/hosts
./scripts/verify-staging.sh
```

Откройте: https://tamor.staging.local

Остановка:

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging down
```

---

### 8. Linux server — production (полный)

**Требования:** Ubuntu/Debian VPS в Узбекистане, Docker Engine, домен (например, `tamor.toyloq.uz`), CA TLS-сертификаты, HashiCorp Vault.

**Не для локальных ноутбуков** — для Kali/Ubuntu dev используйте §6.

**Шаг 1 — Клонирование на сервере**

```bash
git clone https://github.com/Kamol0303/CURSOR.git
cd CURSOR
```

**Шаг 2 — Production-секреты**

```bash
cp .env.production.example .env.production
nano .env.production
```

Заполните **все** значения `CHANGE_ME`:

- `POSTGRES_PASSWORD`, `DATABASE_URL`
- `VAULT_ADDR`, `VAULT_TOKEN`
- `TOTP_ENCRYPTION_KEY`, `PINFL_ENCRYPTION_KEY` (32+ символов)
- `CLICK_*`, `PAYME_*` платёжные ключи
- `LLM_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`

**Шаг 3 — TLS-сертификаты (подписанные CA)**

```bash
ls -la infra/nginx/tls/fullchain.pem infra/nginx/tls/privkey.pem
```

Разместите файлы, подписанные CA (не `generate-dev-certs.sh` для production):

- `infra/nginx/tls/fullchain.pem`
- `infra/nginx/tls/privkey.pem`

**Шаг 4 — Go live**

```bash
chmod +x scripts/go-live.sh scripts/verify-prod.sh
./scripts/go-live.sh
```

Неинтерактивная очистка demo:

```bash
GO_LIVE_PURGE=yes ./scripts/go-live.sh
```

**Шаг 5 — Проверка**

```bash
PUBLIC_HOST=tamor.toyloq.uz ./scripts/verify-prod.sh
python3 scripts/red_team_verify.py --url https://tamor.toyloq.uz --production
curl -fsS https://tamor.toyloq.uz/health
```

**Управление production**

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f backend
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

**Production staging на сервере**

```bash
cp .env.staging.example .env.staging
nano .env.staging
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

Порт 5432 занят другим Docker-контейнером или системным PostgreSQL. **Dev-режим теперь использует хост-порт 5433**.

```bash
git pull origin main
./scripts/linux-dev-setup.sh
```

Если ошибка повторяется:

```bash
docker ps --format '{{.Names}} {{.Ports}}' | grep 5432
docker stop some-postgres
./scripts/linux-dev-setup.sh
```

Доступ к БД с хоста: `postgresql://tamor:tamor_dev@localhost:5433/tamor`

### `orphan containers (cursor-nginx-1)`

При переключении с prod на dev:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production down --remove-orphans
docker compose down --remove-orphans
./scripts/start.sh dev
```

### Alembic `KeyError: '014_certificate_file_id'`

Обновите `main` (цепочка миграций исправлена), затем пересоздайте dev-БД:

```bash
git pull origin main
docker compose down -v
./scripts/linux-dev-setup.sh
```

### Открытие в браузере

- URL: **http://localhost:3000** (на той же машине, где работает Docker)
- Проверка: `curl -s http://localhost:8000/health` → `{"status":"ok",...}`
- Preview URL Cursor **не подключается** к локальному Docker
- На Linux/Kali открывайте браузер **не от root**:

```bash
exit
firefox http://localhost:3000 &
# или от root:
su - xushnud -c "firefox http://localhost:3000 &"
```

---

## Доступ в development

После `seed_demo_users.py` (или `update-main.cmd` / `linux-dev-setup.sh`) учётные данные выводятся **только в локальном терминале**:

| Платформа | Команда |
|-----------|---------|
| Windows | `scripts\windows\show-credentials.cmd` |
| Linux/macOS | Вывод `./scripts/start.sh dev` или `./scripts/linux-dev-setup.sh` |

Логины и пароли **не публикуются в README** из соображений безопасности. Используйте только локально/staging.

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
