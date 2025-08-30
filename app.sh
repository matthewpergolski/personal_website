#!/bin/bash
# FastHTML Portfolio App Launcher
# This script handles environment setup and starts the FastHTML application

set -e  # Exit on any error

echo "🚀 Starting FastHTML Portfolio Application"
echo "=========================================="

# Source environment variables
if [ -f "envs.sh" ]; then
    echo "📄 Loading environment variables from envs.sh"
    source envs.sh
else
    echo "⚠️  Warning: envs.sh not found. Using default configuration."
fi

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "❌ Error: src/main.py not found. Are you in the correct directory?"
    exit 1
fi

# Kill any existing processes on port 8000 and 8001
echo "🧹 Cleaning up any existing processes on ports 8000 and 8001"
pkill -f "uvicorn" 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Wait a moment for ports to be freed
sleep 2

# Check if UV is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: UV is not installed. Please install UV first."
    echo "   pip install uv"
    exit 1
fi

# Install/update dependencies
echo "📦 Ensuring dependencies are up to date"
uv sync

# Start the application
echo "🌟 Starting FastHTML server on http://localhost:8000"
echo "   Press Ctrl+C to stop the server"
echo ""

# Use UV to run the application with uvicorn directly (path‑agnostic)
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
cd "$SCRIPT_DIR"
PYTHONPATH="$SCRIPT_DIR" uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
