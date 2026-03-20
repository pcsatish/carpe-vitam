# Carpe Vitam - Development Guidelines

## Code Quality & Standards

### Backend (Python)
- **Format & Lint**: Use `ruff check .` and `ruff format .` before committing
- **Type hints**: All functions require type hints (SQLAlchemy models, FastAPI handlers, services)
- **Async first**: Database operations must be async (SQLAlchemy asyncio)
- **Error handling**: Raise `HTTPException` with appropriate status codes in routers; let services raise `ValueError` for business logic errors
- **No over-engineering**: One-line fixes stay one-line. Don't refactor surrounding code unless explicitly asked
- **Tests**: Write integration tests using real database (not mocks). See `backend/app/tests/`

### Frontend (React/TypeScript)
- **Strict mode**: Always use TypeScript strict mode, no `any` types
- **Component structure**: Keep components focused; extract logic to hooks and API clients
- **State management**:
  - Use Zustand for client state (auth, UI preferences)
  - Use TanStack Query for server state (results, uploads)
  - Never duplicate server state in local state
- **Styling**: Tailwind only; no inline styles or CSS-in-JS
- **No over-engineering**: Simple forms are fine as inline components. Avoid premature abstraction

### Database
- **Migrations**: Use Alembic for all schema changes (`alembic revision --autogenerate -m "..."`)
- **Indexes**: Add indexes on foreign keys and frequently filtered columns
- **Soft deletes**: Use `is_deleted` flag for auditable soft deletes (lab_reports, not test_results)
- **Denormalization**: Only for performance (report_date in test_results for time-series queries)

## Architectural Patterns

### SQLAlchemy Async — Always Eager Load
All `relationship()` definitions use `lazy="raise"` to prevent accidental lazy loads in async handlers (which cause a cryptic `MissingGreenlet` 500). Any handler that needs related data must explicitly declare it with `selectinload` or `joinedload` on the query:

```python
# In the model
analyte = relationship("AnalyteCatalog", back_populates="test_results", lazy="raise")

# In the router query
result = await db.execute(
    select(TestResult).options(selectinload(TestResult.analyte))
)
```

### Extraction Pipeline (Strategy + Registry)
Add new lab extractors by:
1. Create `backend/app/extraction/extractors/my_lab_pdf.py`
2. Extend `BaseExtractor`
3. Decorate with `@ExtractorRegistry.register`
4. Set `priority` lower than GenericPDFExtractor (999) for priority order

**Example**:
```python
@ExtractorRegistry.register
class ThyrocarePDFExtractor(BaseExtractor):
    name = "ThyrocarePDFExtractor"
    priority = 100  # Higher priority than generic (lower number = tried first)
```

### Canonicalization (Name Normalization)
Test name pipeline: raw → normalize → lookup alias → get canonical → convert units

- Strip method suffixes in `Canonicalizer.normalize_name()`
- Add raw name mappings to `analyte_aliases` table
- Never hardcode mappings in code; use database

## Git & Commits

### Branch Strategy
- `main` is the stable branch — always deployable
- All work happens on feature branches: `feature/<name>` or `fix/<name>`
  - Examples: `feature/families-api`, `fix/canonicalizer-regex`
- Merge to main via PR only — no direct commits to main
- Tag releases as `v<major>.<minor>.<revision>` — no label suffixes
  - `revision` bumps for bug fixes within a phase
  - `minor` bumps at phase completions (Phase 1 → v0.1.0, Phase 2 → v0.2.0, etc.)
  - `major` stays 0 until a significant milestone (production-ready, public release, architectural overhaul) — suggest the bump, don't assume it

### Commit Hygiene
- **Commit frequency**: Small, focused commits (one feature/fix per commit)
- **Commit messages**: Imperative mood, reference what changed and why
  - Good: `Fix method suffix stripping in canonicalizer for PHOTOMETRY variants`
  - Bad: `updated canonicalizer`
- **No force-push** to main
- **Destructive operations**: Confirm first (git reset --hard, branch -D, etc.)

### What Never to Commit
- `.env` — use `.env.example` for templates; real secrets stay local only
- `uploads/` — user-uploaded PDFs are runtime data, not source
- `__pycache__/`, `.pytest_cache/`, `node_modules/` — covered by .gitignore
- Any file containing credentials, API keys, or passwords

## Testing & Validation

- **Before submitting work**: Run `docker-compose up` and test the full workflow
  - Register → Upload PDF → Check extraction
- **Backend tests**: `pytest -v` from backend/
- **Frontend tests**: Not yet required for MVP, but plan for Phase 2
- **Database**: Always test migrations on a fresh database

## Phase-Based Development

### Phase 1 (MVP - COMPLETE)
- Core: auth, upload, extraction, results API
- Focus: end-to-end working workflow
- No: family management, multiple extractors, reference ranges

### Phase 2 (Next)
- Family & member management (add router: `/api/v1/families`)
- Lab-specific extractors (Thyrocare, Redcliffe)
- Reference range visualization
- Extended analyte catalog (~75 tests)

### Phase 3 (Future)
- Async extraction (Celery + Redis)
- CSV/Excel/HL7 support
- Admin dashboard
- Cloud deployment (S3, AWS)

## Reference Files from Legacy Project

- `/mnt/d/Code/Codex/med_reports/process_labs.py` - port extraction logic from here
- `/mnt/d/Code/Codex/med_reports/normalization_map.json` - seed analyte_catalog
- `/mnt/d/Code/Codex/med_reports/unique_analytes.json` - reveals method-suffix normalization issue
- `/mnt/d/Code/Codex/med_reports/lab_results_canonical.csv` - validation data

## Running & Debugging

```bash
# Full stack
cd /home/chris/carpe-vitam
docker-compose up

# Backend only
cd backend
uvicorn app.main:app --reload

# Frontend only
cd frontend
npm run dev

# Database
# Host: localhost:5432, User: postgres, Password: postgres, DB: carpe_vitam
```

**API Docs**: http://localhost:8000/docs (auto-generated Swagger UI)

## When to Escalate

- Architecture changes (new tables, major refactor)
- Phase transitions (moving to Phase 2)
- Production deployment decisions
- Security/privacy considerations
