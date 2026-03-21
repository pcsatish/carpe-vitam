# Development Setup

## Quick Start (One Command)

```bash
bash scripts/setup.sh
```

This script:
- ✅ Checks Python 3.12 availability
- ✅ Creates virtual environment (`backend/.venv`)
- ✅ Installs all dependencies
- ✅ Seeds analyte catalog (if PostgreSQL is running)
- ✅ Prints next steps

## Manual Setup (If Preferred)

### 1. Create Virtual Environment
```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -e ".[dev]"
# OR (workaround if editable install fails):
pip install pytest pytest-asyncio httpx sqlalchemy[asyncio] asyncpg \
    pydantic pydantic-settings 'pydantic[email]' fastapi uvicorn \
    python-jose passlib bcrypt pdfplumber python-multipart alembic
```

### 3. Start Database
```bash
docker-compose up -d  # or: docker-compose up postgres
```

### 4. Seed Analyte Catalog
```bash
cd backend
source .venv/bin/activate
python -m scripts.seed_analytes
```

### 5. Run Tests
```bash
cd backend
pytest -v app/tests/
```

### 6. Start Full Stack
```bash
docker-compose up
```

## Access Points

- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Database**: localhost:5432 (postgres/postgres)

## Troubleshooting

### "Python 3.12 not found"
Install Python 3.12 or use `python3 -m venv` if you have Python 3.12 as default.

### "PostgreSQL not running"
```bash
docker-compose up -d postgres
```

### "pydantic[email] not installed"
This is handled by the script. If running manually:
```bash
pip install 'pydantic[email]'
```

### Tests fail with connection refused
Ensure `docker-compose up` has been run and the DB is initialized (wait ~5s).
