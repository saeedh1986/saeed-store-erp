#!/bin/bash
set -e

echo "🚀 Starting Django Backend..."

# Ensure data directory exists for SQLite
echo "📂 Ensuring data directory exists..."
mkdir -p /app/data

echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

echo "📦 Creating migrations..."
python manage.py makemigrations core inventory orders contacts --noinput

echo "📦 Applying migrations..."
python manage.py migrate

echo "👤 Creating admin user..."
python manage.py shell << EOF
from core.models import User
if not User.objects.filter(username='saeed').exists():
    user = User.objects.create_superuser(
        username='saeed',
        email='saeed@s3eed.ae',
        password='Nov@2020'
    )
    print('✅ Admin user created: saeed@s3eed.ae')
else:
    print('ℹ️ Admin user already exists')
EOF

echo "🔥 Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
