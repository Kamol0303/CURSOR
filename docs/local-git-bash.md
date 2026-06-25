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

---

## 1. Bir marta sozlash

Git Bash da:

```bash
cd "/e/kamol sayt/CURSOR"
chmod +x scripts/local/*.sh
./scripts/local/setup.sh
```

PostgreSQL birinchi marta (postgres paroli so'raladi):

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
| `psql: command not found` | PostgreSQL bin ni PATH ga qo'shing |
| DB ulanish xatosi | `psql -U postgres -f scripts/local/init-db.sql` |
| Login 401 | `cd backend && source .venv/Scripts/activate && python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials` |
| Port band | 8000/3000 band portni bo'shating |

---

## Fayllar

| Fayl | Vazifa |
|------|--------|
| `backend/.env` | DB va JWT sozlamalari |
| `frontend/.env.local` | API URL |
| `backend/secrets/` | JWT kalitlar |
