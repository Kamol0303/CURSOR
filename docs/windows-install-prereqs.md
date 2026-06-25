# Windows — dasturlarni o'rnatish (Git Bash, Docker siz)

Sizda quyidagi xatolar chiqsa, dasturlar o'rnatilmagan yoki PATH ga qo'shilmagan:

```
XATO: node topilmadi
bash: psql: command not found
```

---

## 1. Tekshirish

Git Bash da loyiha papkasida:

```bash
cd "/e/kamol sayt/CURSOR"
chmod +x scripts/local/*.sh
./scripts/local/check-prereqs.sh
```

Har bir qator `[OK]` bo'lishi kerak.

---

## 2. Node.js 20+

1. https://nodejs.org/ — **LTS** versiyani yuklab oling
2. O'rnatishda standart sozlamalar qoldiring
3. **Git Bash oynasini yoping va yangisini oching**
4. Tekshiring: `node --version` va `npm --version`

Agar hali ham topilmasa, qo'lda PATH:

```bash
export PATH="/c/Program Files/nodejs:$PATH"
```

---

## 3. PostgreSQL 15+

1. https://www.postgresql.org/download/windows/
2. O'rnatishda **postgres** foydalanuvchisi uchun parol yozib qo'ying (eslab qoling)
3. Port: `5432` (standart)
4. O'rnatgach **Git Bash ni qayta oching**

Tekshirish:

```bash
psql --version
```

Agar `command not found`:

```bash
export PATH="/c/Program Files/PostgreSQL/16/bin:$PATH"
```

(Raqam `16` o'rniga sizdagi versiya bo'lishi mumkin.)

DB yaratish:

```bash
./scripts/local/init-db.sh
```

Yoki qo'lda:

```bash
psql -U postgres -f scripts/local/init-db.sql
```

**postgres xizmati ishlamasa:** Windows → Services → `postgresql-x64-16` → Start

---

## 4. Python 3.12+

1. https://www.python.org/downloads/
2. **Add python.exe to PATH** belgisini qo'ying
3. Git Bash ni qayta oching
4. Tekshiring: `python --version`

---

## 5. To'liq o'rnatish tartibi

```bash
git pull origin main
chmod +x scripts/local/*.sh
./scripts/local/check-prereqs.sh    # hammasi OK bo'lguncha
./scripts/local/init-db.sh          # PostgreSQL
./scripts/local/setup.sh            # venv, migration, npm
./scripts/local/start.sh            # ishga tushirish
```

Brauzer: http://localhost:3000

| Login | Parol |
|-------|-------|
| `admin.aspect` | `CenterAdmin#26!` |

---

## 6. Tez-tez savollar

| Muammo | Yechim |
|--------|--------|
| Dastur o'rnatdim, lekin topilmaydi | Git Bash ni to'liq yoping va qayta oching |
| `psql` topilmaydi | PATH ga PostgreSQL `bin` qo'shing (yuqorida) |
| postgres paroli noto'g'ri | O'rnatishda yozgan parolingizni kiriting |
| `node` faqat PowerShell da ishlaydi | Node.js ni qayta o'rnating, PATH ni tekshiring |
| Login 401 | `cd backend && source .venv/Scripts/activate && python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials` |
