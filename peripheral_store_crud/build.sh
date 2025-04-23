#!/usr/bin/env bash
# Exit on error and print commands
set -o errexit -o xtrace

# Install dependencies
pip install -r requirements.txt

# Static files and migrations
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser securely (with environment variables)
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.exists():  # Better check than filtering by username
    User.objects.create_superuser(
        username=os.environ.get('ADMIN_USER', 'admin'),
        email=os.environ.get('ADMIN_EMAIL', 'admin@example.com'),
        password=os.environ.get('ADMIN_PASSWORD')
    )
"