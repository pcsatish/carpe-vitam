# Carpe Vitam - Status

**Last Updated**: 2026-03-22
**Phase**: Phase 3 — Dashboard Quality (in progress)
**Tag**: v0.2.1
**CLAUDE.md**: Hard gates added (#21) — branch check before commit, test plan before PR

---

## Phase 3 — In Progress

| Issue | Feature | Status |
|-------|---------|--------|
| #7 | UI consistency: dark theme across all pages | ✅ Done |
| #8 | Fix report dates | ✅ Done |
| #10 | Analyte detail view (history table + larger chart) | ✅ Done |
| #20 | Fix duplicate analytes per report | ✅ Done |
| #24 | Family member management: add users by email, empty-state for new users | ✅ Done |
| #9 | Trend indicators per analyte | ⬜ Pending |
| #11 | % deviation from optimal range | ⬜ Pending |
| #12 | Category summary row | ⬜ Pending |
| #13 | Lab report linkage on chart tooltips | ⬜ Pending |
| #15 | Fix misleading FAILED status (bug) | ⬜ Pending |
| #16 | Store unrecognized analytes for catalog review queue | ⬜ Pending |

## Completed Phases

- **Phase 1** (v0.1.0) — Backend + frontend scaffolding, auth, PDF extraction pipeline, results API
- **Phase 2** (v0.2.0) — Families API, lab-specific extractors (Thyrocare/Redcliffe), 44-analyte catalog, dashboard charts, upload UI

---

## Key Files

| Area | File |
|------|------|
| FastAPI app | `backend/app/main.py` |
| DB session | `backend/app/database.py` |
| Auth | `backend/app/routers/auth.py`, `backend/app/dependencies.py` |
| Upload + extraction trigger | `backend/app/routers/uploads.py` |
| Extraction pipeline | `backend/app/services/result_service.py` |
| Canonicalizer | `backend/app/extraction/canonicalizer.py` |
| Extractors | `backend/app/extraction/extractors/` |
| Results API | `backend/app/routers/results.py` |
| Families API | `backend/app/routers/families.py` |
| Frontend router | `frontend/src/App.tsx` |
| Auth store | `frontend/src/store/authStore.ts` |
| Dashboard | `frontend/src/pages/DashboardPage.tsx` |
| Analyte card | `frontend/src/components/dashboard/AnalyteCard.tsx` |
| Analyte detail modal | `frontend/src/components/dashboard/AnalyteDetailModal.tsx` |
| Upload page | `frontend/src/pages/UploadPage.tsx` |

---

## Running

```bash
# Full stack
docker-compose up

# After backend Python changes (no --reload in docker-compose)
docker restart carpe-vitam-api

# Database
docker exec carpe-vitam-db psql -U postgres -d carpe_vitam

# Re-seed analyte catalog (idempotent)
docker exec carpe-vitam-api python scripts/seed_analytes.py
```

**API docs**: http://localhost:8000/docs
**Frontend**: http://localhost:3000

---

## Known Constraints

- WSL2/Docker: Tailwind JIT does not scan new `.tsx` files — use inline styles for all new components
- `gh pr edit` broken due to GitHub classic projects deprecation — update PR titles/bodies on GitHub manually
- Seed scripts are not yet Alembic data migrations (safe to re-run, but not tracked in DB)
