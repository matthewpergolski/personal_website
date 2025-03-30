#!/bin/bash

set -e  # Exit immediately if a command fails

# Navigate to the project directory (adapt for the new location)
cd "$(dirname "$0")"

# Clear any cache that might be causing issues
echo "Clearing cache..."
if [ -d "app/cache" ]; then
    rm -rf app/cache/*
    echo "Cache cleared successfully"
else
    echo "Cache directory not found - creating it"
    mkdir -p app/cache
fi

# Start Flask with uv
echo "Starting Flask application with uv..."
echo "The app should be available at http://0.0.0.0:5001 once started"
uv run python main.py

# If we get here, something went wrong
echo "Application exited unexpectedly. Check the error messages above."
