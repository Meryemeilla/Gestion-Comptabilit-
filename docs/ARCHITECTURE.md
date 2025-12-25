# Architecture Globale

## Structure
- `config/`: configuration centralisée (settings, urls, wsgi, asgi, celery).
- Apps: `cabinet/`, `dossiers/`, `honoraires/`, `fiscal/`, `juridique/`, `reclamations/`, `comptables/`, `utilisateurs/`, `api/`.
- `templates/`: templates transversaux (base, pdf, rapports, partials, registration…).
- `cabinet/utils/`: services partagés (email, export Excel, export PDF).
- Stockage de documents: `documents_dossiers/`, `documents_juridiques/`.

## Rôles par App
- `cabinet`: dashboard, rapports, exports, vues transversales.
- `dossiers`: gestion des dossiers (modèles, vues, services, managers).
- `honoraires`: montants, recouvrements, règlements.
- `fiscal`: TVA, acomptes, CMIR, dépôt bilan, suivi forfaitaire.
- `juridique`: créations, documents, événements.
- `reclamations`: gestion des réclamations et notifications.
- `comptables`: gestion des comptables.
- `utilisateurs`: rôles, profils, authentification.
- `api`: endpoints REST (viewsets, serializers, urls).

## Flux Clés
- Export PDF/Excel initié depuis `cabinet/views.py` → `cabinet/utils/*.py`.
- Dashboard agrège des statistiques via ORM sur plusieurs apps.
- Pages de listes/détails par app avec `urls.py` dédiés et mixins d’accès.

## Découpage des Fichiers (recommandé)
- `views.py`: logique HTTP et orchestration.
- `services.py`: logique métier, agrégations, optimisation ORM.
- `utils/`: helpers techniques (email/export) transversaux.
- `tasks.py`: tâches asynchrones (Celery) par app.
- `managers.py`: QuerySets personnalisés.
- `forms.py`: formulaires et validation.
- `tests/`: par domaine (models/views/services).