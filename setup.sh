#!/bin/bash

# Clone the repository
git clone -b update https://github.com/MurtadaAhmed/YPH-YourPhotoHost.git

# Change directory to the cloned repository
cd YPH-YourPhotoHost

# Update the system packages
sudo apt update

# Install pip for Python 3
sudo apt install python3-pip

# Install the Python dependencies
pip install -r requirements.txt

# Run Django management commands
python manage.py makemigrations
python manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@myproject.com', 'password')" | python manage.py shell

# Collect static files
python manage.py collectstatic --noinput

# Run the Uvicorn server
sudo uvicorn murtidjango.asgi:application --host 0.0.0.0 --port 80