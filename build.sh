#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser automatically if environment variables are present
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
username = '$DJANGO_SUPERUSER_USERNAME';
email = '$DJANGO_SUPERUSER_EMAIL';
password = '$DJANGO_SUPERUSER_PASSWORD';
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password);
    print('Superuser created successfully.');
else:
    print('Superuser already exists.');
"
fi