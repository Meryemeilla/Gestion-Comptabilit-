#!/bin/bash
# start.sh
set -ex

echo "--- Démarrage de start.sh ---"

# Appliquer les migrations
echo "Application des migrations..."
python manage.py migrate --settings=config.settings.prod

# Créer ou mettre à jour le superuser
echo "Vérification du superutilisateur..."
python manage.py ensure_superuser --username admin --password Admin123! --email admin@example.com --settings=config.settings.prod


# Lancement des workers Celery en arrière-plan (Solution Gratuite)
echo "Lancement de Celery Worker..."
celery -A config worker --loglevel=info --concurrency=2 &

echo "Lancement de Celery Beat..."
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

# Lancer l'application (Processus principal)
echo "Lancement de gunicorn..."
exec gunicorn config.wsgi:application --bind=0.0.0.0:$PORT
