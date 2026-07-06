# TMB — Role × Page Access Matrix (Stage 6)

> Generated as part of tenant RBAC isolation (stages 0–6).  
> **Legend:** ✅ allowed · — denied · 🔀 separate portal

## Admin dashboard (`/dashboard/*`)

| Page | super_admin | hokimiyat | director | center_admin | accountant | auditor |
|------|:-----------:|:---------:|:--------:|:------------:|:----------:|:-------:|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Centers | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| Students | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Teachers | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| Groups | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| Courses | ✅ | ✅ | ✅ | ✅ | — | — |
| Messages | ✅ | — | ✅ | — | — | — |
| Attendance | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| Payments | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Exams | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| Grades | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| Ratings | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| Certificates | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| Analytics | ✅ | ✅ | ✅ | — | — | ✅ |
| Security | ✅ | — | ✅ | — | — | — |

### `hokimiyat_operator` — monitoring-only (2026-07)

District operator uses a **restricted** sidebar and API surface (read + analytics only):

| Page | hokimiyat_operator | API |
|------|:------------------:|-----|
| Operator dashboard (`/dashboard`) | ✅ | `GET /api/v1/dashboard/operator-summary` |
| Centers | ✅ read | `centers.read` — no `centers.create` |
| Teachers | ✅ read | `teachers.read` |
| Students | ✅ read | `students.read` |
| Certificates | ✅ read | `certificates.read` |
| Analytics | ✅ | `analytics.view` |
| Groups, courses, subjects, messages, attendance, payments, exams, grades, ratings, security | — | Denied at API + `OPERATOR_NAV_ROUTES` in `route-guards.ts` |

Source: `backend/app/core/permissions.py` (`hokimiyat_operator`), `frontend/src/lib/route-guards.ts` (`OPERATOR_NAV_ROUTES`).

Portal-only roles (`teacher`, `student`, `parent`) are **denied** all `/dashboard/*` routes (middleware + API).

## Teacher portal (`/teacher/*`)

| Page | teacher | staff roles |
|------|:-------:|:-----------:|
| Dashboard | ✅ | — |
| Groups | ✅ | — |
| Group students | ✅ | — |
| Attendance | ✅ | — |
| Grades | ✅ | — |
| Schedule | ✅ | — |
| Profile | ✅ | — |

API: `/api/v1/teacher/*` — role must be `teacher`.

## Parent portal (`/parent/*`)

| Page | parent | other roles |
|------|:------:|:-----------:|
| Dashboard (children) | ✅ | — |
| Certificates | ✅ | — |

API: `/api/v1/parent/*` — role must be `parent`.

## Student portal (`/student/*`)

| Page | student | other roles |
|------|:-------:|:-----------:|
| Dashboard | ✅ | — |
| Grades / exams / attendance | ✅ | — |

API: `/api/v1/student/*` — role must be `student`.

## Super Admin regression (confirmed)

| Check | Status |
|-------|--------|
| Global center list (all tenants) | ✅ `test_super_admin_lists_all_centers` |
| Cross-center student list | ✅ `test_super_admin_lists_cross_center_students` |
| Dashboard KPIs (unfiltered) | ✅ `test_super_admin_dashboard_kpis_global` |
| PINFL reveal | ✅ `test_super_admin_can_reveal_pinfl` |
| Blocked from teacher portal | ✅ `test_super_admin_cannot_access_teacher_portal` |

## Enforcement layers

| Layer | Mechanism |
|-------|-----------|
| Backend API | `requires_permission()` + tenant scope in services |
| PostgreSQL RLS | `app.center_id`, `app.teacher_id`, `app.role` session vars |
| Next.js middleware | JWT role portal routing + per-route permission checks |
| Client UI | `DashboardRouteGuard`, `PermissionGate`, filtered sidebar |

## Test coverage

| Suite | Type | Purpose |
|-------|------|---------|
| `tests/test_rbac_matrix.py` | Unit | Permission matrix consistency |
| `tests/test_nav_permissions.py` | Unit | Nav ↔ role alignment |
| `tests/security/test_rbac_regression.py` | Integration | Per-role API access + Super Admin regression |
| `tests/security/test_idor.py` | Integration | Cross-tenant isolation |
| `tests/security/test_teacher_portal.py` | Integration | Teacher scope |

Run integration tests (requires PostgreSQL):

```bash
cd backend && pytest tests/security/test_rbac_regression.py -m integration -v
```

## Source of truth

- Permissions: `backend/app/core/permissions.py`
- Page definitions: `backend/app/core/rbac_pages.py`
- Frontend routes: `frontend/src/lib/route-guards.ts`
