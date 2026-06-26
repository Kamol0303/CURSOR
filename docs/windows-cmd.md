# Windows CMD (qora oyna) — qisqa qo'llanma

Siz hozir **CMD** (Command Prompt) ishlatyapsiz — bu **Git Bash emas**.

| Buyruq | CMD da | Git Bash da |
|--------|--------|-------------|
| `chmod +x ...` | **Kerak emas** | Ba'zan kerak |
| `cd "/e/kamol sayt/CURSOR"` | **Ishlamaydi** | Ishlaydi |
| To'g'ri papka | `E:\kamol sayt\CURSOR` | `/e/kamol sayt/CURSOR` |

---

## CMD da ishga tushirish (eng oson)

Loyiha papkasida (`E:\kamol sayt\CURSOR`):

```cmd
git pull origin main
scripts\local\check-prereqs.cmd
scripts\local\init-db.cmd
scripts\local\setup.cmd
scripts\local\start.cmd
```

`chmod` **kerak emas** — `.cmd` fayllar Git Bash orqali `.sh` skriptlarni ishga tushiradi.

Brauzer: http://localhost:3000

---

## Git Bash ochish (ixtiyoriy)

1. Loyiha papkasida o'ng tugma → **Git Bash Here**
2. Yoki Start → **Git Bash**

Git Bash da:

```bash
cd "/e/kamol sayt/CURSOR"
./scripts/local/check-prereqs.sh
./scripts/local/setup.sh
./scripts/local/start.sh
```

---

## Node.js va PostgreSQL

Agar `check-prereqs` da `node` yoki `psql` topilmasa:

- Node.js: https://nodejs.org/
- PostgreSQL: https://www.postgresql.org/download/windows/

Batafsil: [windows-install-prereqs.md](./windows-install-prereqs.md)

O'rnatgach CMD yoki Git Bash ni **qayta oching**.

---

## Demo login

| Login | Parol |
|-------|-------|
| `admin.aspect` | `CenterAdmin#26!` |

---

## Docker orqali (Node/PostgreSQL o'rnatish shart emas)

1. **Docker Desktop** o'rnating va ishga tushiring: https://docs.docker.com/desktop/setup/install/windows-install/
2. Loyiha papkasida:

```cmd
git pull origin main
scripts\start.cmd
```

Yoki PowerShell:

```powershell
cd "E:\kamol sayt\CURSOR"
.\scripts\start.ps1 dev
```

Brauzer: **http://localhost:3000** (faqat shu manzil — cloud preview ishlamaydi)

To'xtatish:

```cmd
docker compose down
```

**Backend `exited (127)` bo'lsa:**

```cmd
git pull origin main
docker compose down -v
docker compose build --no-cache backend
scripts\start.cmd
```

Batafsil: [local-run-guide.md](./local-run-guide.md)
