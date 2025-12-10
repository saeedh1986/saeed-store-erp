#!/bin/bash
set -e

echo "🚀 Starting Django Backend..."

# Wait for DB (simple sleep, or we could use wait-for-it)
# echo "Waiting for database..."
# sleep 5

echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

echo "📦 Applying migrations..."
python manage.py migrate

echo "🔥 Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
