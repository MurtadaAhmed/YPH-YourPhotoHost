#!/bin/bash

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser if it doesn't exist
python << END
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@myproject.com', 'password')
END

# Collect static files
python manage.py collectstatic --noinput

# Start Uvicorn server
exec uvicorn murtidjango.asgi:application --host 0.0.0.0 --port 80
