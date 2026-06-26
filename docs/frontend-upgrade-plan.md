# Frontend upgrade plan — ESLint 9 and Next.js 15

Current stack (2026-06): **Next.js 14.2.35**, **ESLint 8**, **React 18**, `next-intl` 3.x.

## Goals

- Close security advisory window for Next.js 14 when Next 15 is stable in CI.
- Migrate to ESLint 9 flat config before ESLint 8 EOL.
- Avoid production regression during go-live.

## Phase A — Preparation (no version bump)

- [ ] Run `npx @next/codemod@latest upgrade` in a throwaway branch.
- [ ] Document breaking changes from Next 15 release notes.
- [ ] Verify `next-intl` compatibility (v3 vs v4).
- [ ] Add smoke E2E checklist: login, MFA, dashboard, i18n routes, parent portal, student cabinet.

## Phase B — Next.js 15

1. Bump `next` and `eslint-config-next` to 15.x in `frontend/package.json`.
2. Update `.github/workflows/ci.yml` version gate from `14.2.` to `15.`.
3. Fix async `params` / `searchParams` in App Router pages if required.
4. Re-test `next.config.mjs` rewrites and `next-intl` plugin.
5. Run full `npm run build && npm run lint`.

## Phase C — ESLint 9

1. Install `eslint@9`.
2. Replace `frontend/.eslintrc.json` with `eslint.config.mjs` using `eslint-config-next` flat export.
3. Update `npm run lint` script if Next CLI changes.
4. Fix any new lint violations (prefer minimal diffs).

## Phase D — React 19 (if required by Next 15)

- Coordinate with `react` / `react-dom` peer dependency requirements.
- Test client components: `AuthContext`, forms, modals.

## Phase E — Validation

- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] Backend pytest green
- [ ] Lighthouse CI thresholds reviewed
- [ ] Staging smoke test with Docker stack

## Risk assessment

| Risk | Mitigation |
|------|------------|
| i18n routing breaks | Test all locales on `/`, `/dashboard`, `/parent` |
| Middleware edge runtime | Re-test `middleware.ts` after upgrade |
| Dependency peer conflicts | Pin versions in lockfile, one bump per PR |

## Recommendation

Execute **after** Stage 4 low remediation and production go-live, unless a critical Next.js CVE forces early upgrade.
