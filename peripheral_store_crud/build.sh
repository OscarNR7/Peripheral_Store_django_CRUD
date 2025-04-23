#!/usr/bin/env bash
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Configurar static files
python manage.py collectstatic --no-input

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$ADMIN_USER').exists():
    User.objects.create_superuser(
        username='$ADMIN_USER',
        email='$ADMIN_EMAIL',
        password='$ADMIN_PASSWORD'
    )"