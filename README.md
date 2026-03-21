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

> **Note**: Uploading PDFs requires a `family_member_id`. Until the families API is built (v0.2.0), create one directly in the database or via the API docs at `/docs`.

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
| POST | `/api/v1/uploads?family_member_id=` | Upload PDF |
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
```

## Roadmap

- **v0.2.0** — Family & member management API
- **v0.3.0** — Lab-specific extractors (Thyrocare, Redcliffe), expanded analyte catalog
- **v0.4.0** — Reference ranges, out-of-range highlighting
- Later — Async extraction (Celery), CSV/HL7 support, cloud deployment
