#!/bin/bash
set -e

echo "🚀 Starting Django Backend..."

# Ensure data directory exists for SQLite
echo "📂 Ensuring data directory exists..."
mkdir -p /app/data

echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

echo "📦 Applying migrations..."
python manage.py migrate

echo "🔥 Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
