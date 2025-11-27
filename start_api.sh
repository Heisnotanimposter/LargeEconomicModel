#!/bin/bash

# Economic Data API Startup Script

echo "=========================================="
echo "  Economic Data API Startup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r api_requirements.txt
    touch venv/.installed
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "✓ Created .env file. Please edit it with your API keys."
    else
        echo "❌ .env.example not found. Please create a .env file."
    fi
fi

# Initialize database
echo "Initializing database..."
python3 -c "from api.core.database import init_db, engine, Base; Base.metadata.create_all(bind=engine); print('✓ Database initialized')" 2>/dev/null || echo "⚠️  Database initialization skipped"

echo ""
echo "=========================================="
echo "  Starting API Server"
echo "=========================================="
echo "  API will be available at:"
echo "  - Main: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

