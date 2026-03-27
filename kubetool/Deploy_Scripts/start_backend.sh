#!/bin/bash

# Navigate to the kubetool directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate virtual environment (if exists)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the FastAPI backend server
echo "Starting SREAgent API server on port 3001..."
python src/api/api_server.py