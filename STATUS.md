# Carpe Vitam - Implementation Status

**Last Updated**: 2026-03-21
**Phase**: Phase 2 - Complete & Ready for v0.2.0

---

## Phase 2 - Complete (2026-03-20)

### ✅ All 4 Phase 2 Items Delivered

1. **Families API** — `/api/v1/families` and `/api/v1/families/{id}/members`
   - 4 endpoints (POST/GET families, POST/GET members)
   - Authorization: membership required, ADMIN role for adding
   - Creator auto-added as ADMIN
   - 9 integration tests (CRUD, auth, edge cases)
   - Files: `routers/families.py`, `schemas/families.py`, `tests/test_families.py`

2. **Upload UI Enhancement** — Family/member selection
   - Family dropdown (auto-fetched on load)
   - Member dropdown (auto-fetched when family changes)
   - Inline "create family" form for first-time users
   - File: `frontend/src/pages/UploadPage.tsx`

3. **Extended Analyte Catalog** — 44 analytes across 12 categories
   - Categories: Lipid, Liver, Renal, Thyroid, Glucose, Electrolyte, Hematology, Minerals, Pancreas, Hormones, Cardiac, Metabolic
   - All aliases mapped from `unique_analytes.json` with method-suffix normalization
   - Standard adult reference ranges seeded (sex-stratified)
   - File: `backend/scripts/seed_analytes.py`

4. **Lab-Specific Extractors**
   - Thyrocare: Detects "THYROCARE"/"AAROGYAM", priority 100
   - Redcliffe: Detects "REDCLIFFE", priority 200
   - Files: `extractors/thyrocare_pdf.py`, `extractors/redcliffe_pdf.py`

5. **Dashboard Charts** — Live time-series visualization
   - Family + member selectors (auto-populate)
   - Recharts time-series with reference ranges
   - File: `frontend/src/pages/DashboardPage.tsx`

### Infrastructure Added
- `scripts/setup.sh` — One-command development setup (venv + deps + seed)
- `SETUP.md` — Detailed setup instructions and troubleshooting
- `frontend/src/api/families.ts` — Typed families API client

### Testing & Validation
- ✅ All code imports successfully
- ✅ All TypeScript/TSX structure verified
- ✅ Setup script functional
- ✅ Integration tests ready (await DB)

---

## Completed Implementation (Phase 1 - All 17 Tasks)

### Backend (Python/FastAPI)
- Project structure with pyproject.toml
- SQLAlchemy ORM models (8 tables: users, families, family_members, analyte_catalog, analyte_aliases, reference_ranges, lab_reports, test_results)
- Alembic migrations (001_initial_schema.py)
- JWT authentication (register, login, refresh, me endpoints)
- PDF extraction pipeline:
  - BaseExtractor ABC + Registry pattern
  - GenericPDFExtractor (table-first, regex fallback)
  - Canonicalizer (test name normalization with method-suffix stripping)
  - UnitConverter (mg/dL <-> mmol/L conversions)
- Upload service + endpoint (triggers extraction synchronously)
- Extraction service (orchestrates pipeline + canonicalization + persistence)
- Results API (GET /results, GET /results/timeseries)

### Frontend (React/TypeScript/Vite)
- Project structure with package.json, vite.config.ts, tsconfig.json
- Zustand auth store (persisted to localStorage)
- API client with axios + automatic token injection
- Auth pages (LoginPage, RegisterPage)
- Protected routes (ProtectedRoute wrapper)
- Dashboard page (upload + chart sections)
- Upload page (file picker + progress)
- TimeSeriesChart component (Recharts-based)

### Infrastructure
- Dockerfile for backend (bcrypt<4.0.0 pinned for passlib compat)
- Dockerfile for frontend (dev mode)
- docker-compose.yml (PostgreSQL + FastAPI + React)
- .env.example with configuration
- .gitignore
- README.md with setup instructions
- CLAUDE.md with workflow guidelines

---

## All Bugs Found & Fixed (2026-03-20)

### Issue 1: Async Lifespan Initialization
**Status**: Fixed
**File**: `backend/app/main.py`

### Issue 2: Missing ForeignKey Import
**Status**: Fixed
**File**: `backend/app/models/analyte.py`

### Issue 3: Invalid Family->LabReport Relationship
**Status**: Fixed
**File**: `backend/app/models/family.py`

### Issue 4: Auth Header Parsing
**Status**: Fixed
**File**: `backend/app/dependencies.py`

### Issue 5: Missing Pydantic Email Validator
**Status**: Fixed
**File**: `backend/Dockerfile`

### Issue 6: Frontend Port Conflict
**Status**: Fixed
**Solution**: Use `--force-recreate` when restarting frontend container

### Issue 7: bcrypt/passlib Version Incompatibility
**Status**: Fixed
**Was**: `passlib==1.7.4` incompatible with `bcrypt>=4.0.0` — registration crashed with "password cannot be longer than 72 bytes"
**Fixed**: Pinned `bcrypt<4.0.0` in `backend/Dockerfile` and `backend/pyproject.toml`

### Issue 8: UserSchema.created_at Type Mismatch
**Status**: Fixed
**Was**: `created_at: str` in schema but model returns `datetime` — `GET /auth/me` returned 500
**Fixed**: Changed to `created_at: datetime` in `backend/app/schemas/auth.py`

### Issue 9: Extraction Never Triggered After Upload
**Status**: Fixed
**Was**: Upload router only saved file to disk and created PENDING record — never called ResultService
**Fixed**: Added `ResultService.extract_and_persist()` call in `backend/app/routers/uploads.py` after file save

### Issue 10: Canonicalizer Regex Too Aggressive
**Status**: Fixed
**Was**: `re.sub(r"(\w)\s+(\w)", r"\1\2", name)` collapsed ALL spaces between word chars — `SERUM COPPER` -> `SERUMCOPPER`
**Fixed**: Replaced with token-based logic that only collapses consecutive single-character tokens (e.g. `C M I A` -> `CMIA`)
**File**: `backend/app/extraction/canonicalizer.py`

### Issue 11: CLIA Not in METHOD_SUFFIXES
**Status**: Fixed
**Was**: `TESTOSTERONE C.L.I.A` normalized to `TESTOSTERONE CLIA` instead of `TESTOSTERONE`
**Fixed**: Added `CLIA` to `METHOD_SUFFIXES` list in canonicalizer
**File**: `backend/app/extraction/canonicalizer.py`

### Issue 12: analyte_catalog and analyte_aliases Empty
**Status**: Fixed
**Was**: No analyte data seeded — all extracted tests skipped, every report marked FAILED
**Fixed**: Seeded 22 analytes from `normalization_map.json` with canonical names, categories, units, and aliases

### Issue 13: Timeseries Endpoint Lazy-Load in Async Context
**Status**: Fixed
**Was**: `test_result.analyte` accessed as lazy relationship in async handler — `MissingGreenlet` 500 error
**Fixed**: Added `selectinload(TestResult.analyte)` to the timeseries query
**File**: `backend/app/routers/results.py`

---

## Verification Checklist

- [x] Backend starts without crashes
- [x] GET /health returns `{"status": "ok"}`
- [x] Docker images rebuild correctly
- [x] POST /auth/register creates user and returns JWT
- [x] POST /auth/login returns JWT token
- [x] GET /auth/me returns user info
- [x] POST /uploads accepts PDF, triggers extraction, returns lab_report_id
- [x] GET /results returns extracted test results
- [x] GET /results/timeseries returns time-series data
- [x] Frontend loads at localhost:3000

---

## Known Gaps (Not Blocking MVP)

- **No families API**: `family_member_id` for uploads must be inserted directly into DB. Phase 2 adds `/api/v1/families` endpoints.
- **report_date is null**: GenericPDFExtractor doesn't parse dates from this PDF format — timeseries `date` field is empty. Needs extractor improvement or lab-specific extractor.
- **Low canonicalization coverage**: Only analytes in `normalization_map.json` (22 entries) are recognized. Most specialized tests (Apolipoprotein, LP-PLA2, etc.) are silently skipped. Expand aliases table to improve coverage.

---

## Lessons from Phase 2

**What Worked Well**:
- Virtual environment + setup automation (`scripts/setup.sh`) — eliminated dev friction
- Seed scripts with idempotent inserts (UPSERT) — safe to re-run multiple times
- Helper functions for authorization (`_require_admin`, `_require_membership`) — DRY + prevents info leak bugs
- Frontend re-fetching server data on state change — simple, fresh data, no sync bugs
- Extractor registry pattern — easy to add new labs without modifying core pipeline

**For Phase 3**:
- Report dates must be fixed first — x-axis is meaningless without real dates
- Seed scripts should eventually become Alembic data migrations (track state in DB)
- Consider TanStack Query for caching if chart re-renders become expensive

## Next Phase (Phase 3 — Dashboard Quality)

1. **Fix report dates** — x-axis is currently null for most extractors; date parsing must work before trend features are useful
2. **Trend indicators** — improving / stable / worsening arrow per analyte based on last 2+ readings
3. **Expanded analyte detail view** — click a card to see full history table + larger chart
4. **% deviation from optimal** — show "12% above upper limit" alongside Low/High badge
5. **Category summary row** — "3 of 7 Lipid markers out of range" at the top of each group
6. **Lab report linkage** — tooltip on each chart data point shows which report it came from

---

## Key Files Reference

### Backend Entry Points
- `backend/app/main.py` - FastAPI app setup
- `backend/app/config.py` - Environment config
- `backend/app/database.py` - SQLAlchemy setup
- `backend/alembic/versions/001_initial_schema.py` - Full schema

### Frontend Entry Points
- `frontend/src/main.tsx` - React entry
- `frontend/src/App.tsx` - Router setup
- `frontend/src/store/authStore.ts` - State management
- `frontend/src/api/client.ts` - HTTP client

### Critical Logic
- `backend/app/extraction/canonicalizer.py` - Name normalization
- `backend/app/extraction/extractors/generic_pdf.py` - PDF extraction
- `backend/app/services/result_service.py` - Extraction orchestration
- `backend/app/routers/uploads.py` - Upload + extraction trigger
- `backend/app/dependencies.py` - Auth token handling

## Running

```bash
# Full stack
cd /home/chris/carpe-vitam
docker-compose up

# If frontend port doesn't bind
docker-compose up -d --force-recreate frontend

# Database (direct access for seeding families until Phase 2 API exists)
# Host: localhost:5432, User: postgres, Password: postgres, DB: carpe_vitam
```

**API Docs**: http://localhost:8000/docs
