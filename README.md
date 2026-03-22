# Carpe Vitam

Personal and family health tracker. Upload medical lab report PDFs — results are extracted, normalized, and visualized as time-series charts.

## Stack

- **Backend**: Python 3.12 + FastAPI + SQLAlchemy (async) + PostgreSQL
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Recharts
- **Infra**: Docker + Docker Compose

## Quick Start

```bash
cp .env.example .env
docker-compose up
```

- Frontend: http://localhost:3000
- API: http://localhost:8000/api/v1
- API Docs: http://localhost:8000/docs

> **Note**: Before uploading a PDF, create a family and add a member via the dashboard or API docs at `/docs`. The upload form includes family/member selection.

## Project Structure

```
carpe-vitam/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # API endpoint handlers
│   │   ├── services/        # Business logic
│   │   └── extraction/      # PDF extraction pipeline
│   ├── alembic/             # Database migrations
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── api/             # API client
│       ├── store/           # Zustand state
│       ├── pages/
│       └── components/
└── docker-compose.yml
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| GET | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/families` | Create a family |
| GET | `/api/v1/families` | List user's families |
| POST | `/api/v1/families/{id}/members` | Add a family member |
| GET | `/api/v1/families/{id}/members` | List family members |
| POST | `/api/v1/uploads` | Upload PDF (requires family_member_id) |
| GET | `/api/v1/results?family_member_id=` | List results |
| GET | `/api/v1/results/timeseries?family_member_id=` | Time-series data |

## Development

### Setup (First Time)

**Automated**:
```bash
bash scripts/setup.sh
```

Creates virtual environment, installs dependencies, seeds database (if PostgreSQL is running).

**Manual**: See `SETUP.md` for detailed steps and troubleshooting.

### Common Tasks

```bash
# Lint & format (requires ruff installed)
cd backend && ruff check . && ruff format .

# Tests (requires venv activated)
cd backend && source .venv/bin/activate && pytest -v

# New migration
cd backend && alembic revision --autogenerate -m "description"

# Seed analyte catalog
cd backend && source .venv/bin/activate && python -m scripts.seed_analytes

# After any backend Python change (no --reload in docker-compose)
docker restart carpe-vitam-api
```

## Roadmap

- **v0.1.0** ✅ — Core MVP: auth, upload, extraction, results API
- **v0.2.0** ✅ — Families API, lab-specific extractors, analyte catalog, dashboard redesign
- **v0.3.0** — Dashboard quality: report dates, trend indicators, analyte detail view
- **v0.4.0** — Async extraction (Celery + Redis), admin dashboard
