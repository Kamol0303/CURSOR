# TMB — mahalliy ishga tushirish qo'llanmasi

## 0. Talablar

| Dastur | Versiya |
|--------|---------|
| Docker Desktop | 4.x+ (WSL 2) |
| Git | 2.x |
| RAM | kamida 4 GB bo'sh |

---

## 1. Docker ni WSL da yoqish (muhim!)

Agar `The command 'docker' could not be found` chiqsa:

1. **Windows** da Docker Desktop ni oching
2. **Settings → Resources → WSL Integration**
3. **Ubuntu** (yoki sizdagi distro) ni yoqing
4. **Apply & Restart**
5. WSL terminalni **yoping va qayta oching**

Tekshirish:

```bash
docker --version
docker compose version
```

Agar WSL da ishlamasa — **PowerShell** dan ishga tushiring (quyida).

---

## 2. Loyihani yuklash

```bash
cd "/mnt/e/kamol sayt/CURSOR"
git checkout main
git pull origin main
```

Oxirgi commit: `fd61dfa` (OCMS + barcha modullar)

---

## 3. To'liq ishga tushirish (bitta buyruq)

### Variant A — DEV (eng oson, TLS yo'q)

```bash
chmod +x scripts/start.sh
./scripts/start.sh dev
```

| Xizmat | Manzil |
|--------|--------|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |

### Variant B — STAGING (productionga yaqin, HTTPS)

```bash
chmod +x scripts/start.sh
./scripts/start.sh staging
```

Keyin `hosts` ga qo'shing:

**Windows (Admin PowerShell):**
```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "127.0.0.1 tamor.staging.local"
```

**WSL:**
```bash
echo "127.0.0.1 tamor.staging.local" | sudo tee -a /etc/hosts
```

Sayt: **https://tamor.staging.local**

### Variant C — Windows PowerShell (WSL da Docker yo'q bo'lsa)

```powershell
cd "E:\kamol sayt\CURSOR"
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\start.ps1 dev
# yoki
.\scripts\start.ps1 staging
```

---

## 4. Login ma'lumotlari

| Rol | Login | Parol | MFA |
|-----|-------|-------|-----|
| Menejer | `admin.aspect` | `CenterAdmin#26!` | Yo'q |
| Super Admin | `admin.tmb` | `Tmb#2026Admin!` | Ha |
| Direktor | `director.aspect` | `Direktor#2026!` | Ha |
| O'qituvchi | `teacher.dilnoza` | `Teach#Dil2026!` | Yo'q |

Parol o'zgartirish: **Xavfsizlik** sahifasi (`/dashboard/security`)

MFA QR kod:
```bash
./scripts/show-mfa-qr.sh
```

---

## 5. Tekshirish

```bash
# Dev
curl http://localhost:8000/health

# Staging
./scripts/test-login.sh
```

---

## 6. To'xtatish

```bash
# Dev
docker compose down

# Staging
docker compose -f docker-compose.staging.yml --env-file .env.staging down
```

Ma'lumotlarni ham o'chirish (ehtiyot!):
```bash
docker compose down -v
```

---

## 7. Muammolar

| Muammo | Yechim |
|--------|--------|
| `docker not found` | Docker Desktop + WSL Integration |
| Login 401 | `./scripts/start.sh dev` qayta ishga tushiring (seed avtomatik) |
| 502 nginx | `docker compose logs backend` — migration xatosi |
| Postgres unhealthy | `docker compose down -v` keyin qayta `start.sh` |
| Backend `exited (127)` | Windows CRLF — `git pull`, `docker compose build --no-cache backend`, qayta start |
| Brauzer sertifikat ogohlantirishi | Staging self-signed — "Advanced → Proceed" |

Diagnostika:
```bash
./scripts/diagnose-staging.sh
```
