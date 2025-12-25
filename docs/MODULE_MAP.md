# Module Map (Carte des Fichiers)

## Répertoires Clés
- `config/`: `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`, `celery.py`.
- `cabinet/`: `views.py`, `urls.py`, `utils/email.py`, `utils/export.py`, `utils/pdf_export.py`, `templates/cabinet/`.
- `dossiers/`: `models.py`, `views.py`, `services.py`, `managers.py`, `urls.py`, `list.html`.
- `honoraires/`: `models.py`, `views.py`, `templates/honoraires/`, `urls.py`.
- `fiscal/`: `models.py`, `views.py`, `forms.py`, `templates/fiscal/`, `urls.py`.
- `juridique/`: `models.py`, `views.py`, `urls.py`, `templates/juridique/`.
- `reclamations/`: `models.py`, `views.py`, `forms.py`, `signals.py`, `tasks.py`, `urls.py`.
- `comptables/`: `models.py`, `views.py`, `tasks.py`, `urls.py`.
- `utilisateurs/`: `models.py`, `views.py`, `tasks.py`, `signals.py`, `urls.py`.
- `api/`: `viewsets.py`, `serializers.py`, `urls.py`.
- `templates/`: `base/base.html`, `partials/`, `pdf/`, `rapports/`, `registration/`, `dashboard.html`, `home.html`.

## Points d’Entrée Fréquents
- Accueil/Dashboard: `cabinet/views.py :: home_view` et `DashboardView`.
- Exports: `cabinet/views.py :: ExportPDFView`, utilitaires dans `cabinet/utils/`.
- Listes et détails: `views.py` dans chaque app + `urls.py`.

## Utilité
- Permet de retrouver rapidement un module/fichier en fonction du besoin (UI, services, exports, tâches, tests).