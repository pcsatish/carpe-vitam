#!/bin/bash
set -e

echo "🚀 Carpe Vitam Development Setup"
echo "=================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$BACKEND_DIR/.venv"

# Check Python version
echo "✓ Checking Python version..."
if ! command -v python3.12 &> /dev/null; then
    echo "✗ Python 3.12 not found. Please install Python 3.12."
    exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "✓ Creating virtual environment..."
    python3.12 -m venv "$VENV_DIR"
else
    echo "✓ Virtual environment already exists"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Install dependencies (workaround for hatchling issue)
echo "✓ Installing dependencies..."
pip install -q \
    pytest pytest-asyncio httpx \
    sqlalchemy[asyncio] asyncpg \
    pydantic pydantic-settings 'pydantic[email]' \
    fastapi uvicorn \
    python-jose passlib bcrypt \
    pdfplumber python-multipart \
    alembic 2>&1 | grep -v "already satisfied" || true

echo "✓ Dependencies installed"

# Verify database exists
echo "✓ Checking PostgreSQL connection..."
if ! psql -U postgres -h localhost -d carpe_vitam -c "SELECT 1" &>/dev/null 2>&1; then
    echo "⚠ PostgreSQL not running or carpe_vitam DB not found"
    echo "  Start with: docker-compose up -d postgres"
    echo "  (Or provide DATABASE_URL environment variable)"
fi

# Seed analytes if DB is available
if psql -U postgres -h localhost -d carpe_vitam -c "SELECT 1" &>/dev/null 2>&1; then
    echo "✓ Seeding analyte catalog..."
    cd "$BACKEND_DIR"
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/carpe_vitam"
    python scripts/seed_analytes.py || echo "  (Seed skipped - DB may not be initialized yet)"
    cd "$PROJECT_ROOT"
else
    echo "⚠ Skipping seed (database not available)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Start the database:"
echo "     docker-compose up -d"
echo ""
echo "  2. Activate venv (if not already active):"
echo "     source backend/.venv/bin/activate"
echo ""
echo "  3. Run tests:"
echo "     cd backend && pytest -v app/tests/"
echo ""
echo "  4. Start the full stack:"
echo "     docker-compose up"
echo ""
echo "  5. Access the app:"
echo "     API: http://localhost:8000/docs"
echo "     Frontend: http://localhost:3000"
echo ""
