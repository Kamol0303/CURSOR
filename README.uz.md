# TMB — Ta'lim Monitoringi Boshqaruvi

**Tillar:** [English](README.md) · [O'zbek](README.uz.md) · [Русский](README.ru.md)

Samarqand viloyati, Toyloq tumani uchun davlat darajasidagi ta'lim monitoringi va boshqaruv platformasi.

---

## Yakuniy holat (2026-yil iyul)

| Soha | Tayyorlik | Izoh |
|------|-----------|------|
| **Ilova kodi** | **~100%** | 0–7 fazalar, OCMS, Hokimiyat paneli, AI, audit |
| **Xavfsizlik (avtomat)** | **12/12 o'tdi** | `python3 scripts/red_team_verify.py --offline` |
| **Go-live (infratuzilma)** | **~85%** | Vault, CA TLS, UZ server, tashqi pentest imzosi qoldi |

To'liq xavfsizlik hisoboti: [`docs/security-audit-report.md`](docs/security-audit-report.md)  
Go-live ro'yxati: [`docs/production-100-checklist-uz.md`](docs/production-100-checklist-uz.md)

---

## Asosiy imkoniyatlar

- **RBAC** — 10+ rol, PostgreSQL RLS, tenant izolyatsiyasi
- **Hokimiyat operatori** — faqat monitoring paneli (6 ta menyu)
- **Sertifikatlar** — QR tekshiruv, yaxlitlik xeshi, `/verify`
- **Sun'iy intellekt** — imtihon testlari + dars materiallari (prezentatsiya / sinf o'yini)
- **LLM zanjirlari** — BazaarLink → Gemini → Mistral (avtomatik zaxira)
- **Audit jurnali** — `/dashboard/audit` — kim, qachon, nima o'zgartirdi
- **Production** — `Dockerfile.prod`, `docker-compose.prod.yml`, Nginx TLS

---

## Xavfsizlik tekshiruvi

```bash
# Avtomatik red-team (server shart emas)
python3 scripts/red_team_verify.py --offline

# Staging / production
python3 scripts/red_team_verify.py --url https://tamor.toyloq.uz --production

# Integratsion testlar (PostgreSQL kerak)
cd backend && pytest tests/security/ -v
```

**So'nggi offline natija:** 12/12 avtomatik tekshiruv o'tdi.

**Production oldidan:** tashqi pentest imzosi (`docs/red-team-checklist.md`), CA TLS, Vault, demo ma'lumotlarni tozalash.

---

## Tez ishga tushirish (Docker)

```bash
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
```

- Frontend: http://localhost:3000  
- API: http://localhost:8000

### LLM sozlash (`.env` — kalitlarni gitga commit qilmang!)

```env
LLM_API_KEY=sk-bl-...              # BazaarLink (asosiy)
GEMINI_API_KEY=...                 # zaxira 1
MISTRAL_API_KEY=...                # zaxira 2
AI_ENABLED=true
```

Windows: `scripts\windows\setup-llm-env.cmd`

---

## Demo loginlar (faqat development)

| Rol | Login | Parol |
|-----|-------|-------|
| Super Admin | `admin.tmb` | `Tmb#2026Admin!` |
| Hokimiyat operatori | `operator.hokimiyat` | `Hokim#Op2026!` |
| Markaz admini | `admin.aspect` | `CenterAdmin#26!` |
| O'qituvchi | `teacher.dilnoza` | `Teach#Dil2026!` |
| O'quvchi | `student.sardor` | `Student#2026!` |

---

## Production go-live

```bash
cp .env.production.example .env.production
./scripts/go-live.sh
```

Windows: `scripts\windows\go-live-prep.cmd`  
Build tekshiruvi: `scripts\windows\verify-prod-build.cmd`

---

## Hujjatlar

| Hujjat | Maqsad |
|--------|--------|
| [`docs/threat-model.md`](docs/threat-model.md) | STRIDE tahdid modeli |
| [`docs/red-team-checklist.md`](docs/red-team-checklist.md) | 24A xavfsizlik ro'yxati |
| [`docs/go-live-runbook.md`](docs/go-live-runbook.md) | Production deploy |
| [`docs/security-audit-report.md`](docs/security-audit-report.md) | Audit natijalari |

---

## Litsenziya

Davlat loyihasi — Toyloq tumani hokimligi.
