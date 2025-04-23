#!/usr/bin/env bash
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Configurar static files
python manage.py collectstatic --no-input --clear

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$ADMIN_EMAIL').exists():
    User.objects.create_superuser(
        email='$ADMIN_EMAIL',
        password='$ADMIN_PASSWORD',
        first_name='$ADMIN_FIRST_NAME',
        last_name='$ADMIN_LAST_NAME'
    )"