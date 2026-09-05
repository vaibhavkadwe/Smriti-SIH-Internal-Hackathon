#!/bin/bash
set -e

echo "=== ElderCare Platform — Local Dev Setup ==="

# 1. Check Python
python3 --version || { echo "Python 3 is required"; exit 1; }

# 2. Virtual environment
cd "/Users/priyanujgoswami/SIH 26/backend"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating venv and installing dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

# 3. Run tests
echo "Running test suite..."
python run_tests.py

# 4. Start Docker stack (if docker available)
if command -v docker &> /dev/null; then
    echo "Starting PostgreSQL + Redis via Docker Compose..."
    cd "/Users/priyanujgoswami/SIH 26"
    docker compose up -d db redis
    echo "Waiting for PostgreSQL to be ready..."
    sleep 3

    # 5. Run Alembic migrations
    echo "Running migrations..."
    cd "/Users/priyanujgoswami/SIH 26/backend"
    alembic upgrade head 2>/dev/null || echo "Alembic: No migrations yet (initial schema in models)"
fi

echo ""
echo "=== Phase 1 Scaffold Ready ==="
echo "Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "Mobile:  cd mobile && flutter pub get && flutter run"
echo "Web:     cd dashboard && flutter pub get && flutter run -d chrome"
