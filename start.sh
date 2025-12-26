#!/bin/bash
# start.sh

# Appliquer les migrations
python manage.py migrate --settings=config.settings.prod

# Créer ou mettre à jour le superuser
python manage.py ensure_superuser --username admin --password Admin123! --email admin@example.com --settings=config.settings.prod

# Lancer l'application
exec gunicorn config.wsgi:application --bind=0.0.0.0:$PORT
