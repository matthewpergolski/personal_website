#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")/.."

# Ensure cache directory exists
mkdir -p app/cache

# Set development environment
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start the development server
echo "Starting Flask development server..."
uv run python app.py 