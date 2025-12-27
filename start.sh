#!/bin/bash
# start.sh
set -e

echo "--- Démarrage de start.sh ---"

# Appliquer les migrations
echo "Application des migrations..."
python manage.py migrate --settings=config.settings.prod

# Créer ou mettre à jour le superuser
echo "Vérification du superutilisateur..."
python manage.py ensure_superuser --username administrateur --password adminn123 --email admin@example.com --settings=config.settings.prod

# Lancer l'application
echo "Lancement de gunicorn..."
exec gunicorn config.wsgi:application --bind=0.0.0.0:$PORT
