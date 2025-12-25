# Conventions du Projet

## Séparation des Responsabilités
- `views.py`: logique HTTP minimale; délègue aux services.
- `services.py`: logique métier testable, agrégations (utiliser `select_related`/`prefetch_related`).
- `utils/`: helpers techniques (email, export PDF/Excel), réutilisables.
- `tasks.py`: traitement asynchrone (envoi email, rappels, batchs).
- `managers.py`: QuerySets personnalisés pour les modèles.
- `forms.py`: validation et saisies.
- `tests/`: tests organisés par domaine et par type (models/views/services).

## Routes et Namespaces
- Inclusion par app avec namespace: `include(("app.urls", "app"), namespace="app")`.
- Préfixes cohérents:
  - `export/pdf/<type>/` pour les PDF.
  - `export/excel/<type>/` pour les Excel.

## Templates
- Par app: `templates/<app>/*.html`.
- Partials réutilisables: `templates/partials/`.
- Modèles PDF transversaux: `templates/pdf/`.

## Imports et Dépendances Lourdes
- Import paresseux pour `weasyprint` à l’intérieur des méthodes d’export.
- Gestion d’erreurs contrôlée (HTTP 503) en cas d’échec d’import/`write_pdf`.

## Qualité et Performance
- Logique lourde dans `services.py` pour lisibilité et tests.
- Minimiser les requêtes N+1 via optimisation ORM.
- Favoriser la centralisation des helpers transversaux (`cabinet/utils/`).

## Sections internes des modules
- Utiliser des séparateurs de commentaires pour structurer les fichiers:
  - `# ==================== Imports ====================`
  - `# ==================== Constantes ====================`
  - `# ==================== Classes ====================`
  - `# ==================== Fonctions ====================`
  - `# ==================== Handlers ====================` (uniquement pour `views.py`/`views_api.py`)
- Placement:
  - Insérer chaque séparateur avant la première occurrence top-niveau correspondante (import/constante/class/def).
  - Ne pas dupliquer si des séparateurs existent déjà.
- Automatisation:
  - Scripts disponibles: `tools/add_headers.py` (docstrings de module) et `tools/add_sections.py` (séparateurs de sections).
  - Les scripts n’altèrent pas la logique ni l’ordre du code.