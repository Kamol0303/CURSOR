# TMB — Git Bash orqali (Docker siz)

## Talablar

| Dastur | O'rnatish (Windows) |
|--------|---------------------|
| **Git Bash** | Git for Windows bilan keladi |
| **Python 3.12+** | https://www.python.org/downloads/ (Add to PATH) |
| **Node.js 20+** | https://nodejs.org/ |
| **PostgreSQL 15+** | https://www.postgresql.org/download/windows/ |
| **OpenSSL** | Git Bash ichida bor |

Redis **shart emas** — lokal rejimda xotira ichida ishlaydi (`USE_MEMORY_REDIS=true`).

**Node yoki psql topilmasa:** [windows-install-prereqs.md](./windows-install-prereqs.md)

---

## 0. Talablarni tekshirish

```bash
cd "/e/kamol sayt/CURSOR"
chmod +x scripts/local/*.sh
./scripts/local/check-prereqs.sh
```

Barcha qatorlar `[OK]` bo'lguncha o'rnatishni davom ettiring.

---

## 1. Bir marta sozlash

```bash
./scripts/local/init-db.sh    # PostgreSQL (postgres paroli so'raladi)
./scripts/local/setup.sh      # venv, migration, npm install
```

`init-db.sh` o'rniga qo'lda:

```bash
psql -U postgres -f scripts/local/init-db.sql
```

---

## 2. Ishga tushirish

### Variant A — bitta oyna (ikkala server)

```bash
./scripts/local/start.sh
```

### Variant B — ikkita Git Bash oyna

**Oyna 1 — Backend:**
```bash
./scripts/local/start-backend.sh
```

**Oyna 2 — Frontend:**
```bash
./scripts/local/start-frontend.sh
```

---

## 3. Brauzer

```
http://localhost:3000
```

| Login | Parol |
|-------|-------|
| `admin.aspect` | `CenterAdmin#26!` |

---

## 4. Muammolar

| Muammo | Yechim |
|--------|--------|
| `node topilmadi` / `psql: command not found` | `./scripts/local/check-prereqs.sh` va [windows-install-prereqs.md](./windows-install-prereqs.md) |
| DB ulanish xatosi | `./scripts/local/init-db.sh` |
| Login 401 | `cd backend && source .venv/Scripts/activate && python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials` |
| Port band | 8000/3000 band portni bo'shating |

---

## Fayllar

| Fayl | Vazifa |
|------|--------|
| `scripts/local/check-prereqs.sh` | Dasturlar tekshiruvi |
| `scripts/local/init-db.sh` | PostgreSQL DB yaratish |
| `backend/.env` | DB va JWT sozlamalari |
| `frontend/.env.local` | API URL |
| `backend/secrets/` | JWT kalitlar |
