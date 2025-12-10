#!/bin/bash

# Exit on error
set -e

# Navigate to backend directory if not already there
if [ -d "backend" ]; then
    cd backend
fi

# Run migrations (Optional: if we add Alembic later, this is where it goes)
# echo "Running migrations..."
# alembic upgrade head

# Start the application
echo "Starting Uvicorn Server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
