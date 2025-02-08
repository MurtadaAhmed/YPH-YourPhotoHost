
FROM python:3.9-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apt-get update \
    && apt-get install -y sudo git dos2unix \
    && apt-get clean


WORKDIR /app


COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt


COPY . /app/


EXPOSE 80


CMD ["sh", "-c", " \
    export DJANGO_SETTINGS_MODULE=murtidjango.settings && \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python -c 'import os, django; os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"murtidjango.settings\"); \
    django.setup(); \
    from django.contrib.auth import get_user_model; User = get_user_model(); \
    User.objects.create_superuser(\"admin\", \"admin@myproject.com\", \"password\") if not User.objects.filter(username=\"admin\").exists() else None' && \
    python manage.py collectstatic --noinput && \
    exec uvicorn murtidjango.asgi:application --host 0.0.0.0 --port 80 \
"]
