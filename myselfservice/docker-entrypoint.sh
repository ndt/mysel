#!/bin/bash
set -e

# Warten auf Postgres
sleep 5


# Migrationen ausführen
python manage.py migrate

# Superuser erstellen (nur wenn noch keiner existiert)
if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(User.objects.filter(is_superuser=True).exists())"; then
    python manage.py createsuperuser --noinput
fi

python manage.py create_dovecot_users_view

exec "$@"