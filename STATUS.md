# Carpe Vitam - Implementation Status

**Last Updated**: 2026-03-20 (16:00 UTC)
**Phase**: MVP Phase 1 - Complete & Validated

---

## Completed Implementation (All 17 Tasks)

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

## Next Phase (Phase 2)

1. **Family Management**: Add `/api/v1/families` and `/api/v1/family-members` endpoints
2. **Lab-Specific Extractors**: Thyrocare, Redcliffe PDFs (date parsing, better table extraction)
3. **Expand Analyte Catalog**: Seed ~75 tests from `unique_analytes.json`
4. **Reference Ranges**: Visualization + out-of-range highlighting
5. **Related Tests Panel**: Show tests that typically go together

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
