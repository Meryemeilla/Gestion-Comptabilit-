# Routes Principales

## Inclusion Globale (config/urls.py)
- `path('', include(('cabinet.urls', 'cabinet'), namespace='cabinet'))`
- Autres apps: `dossiers/`, `reclamations/`, `juridique/`, `fiscal/`, `honoraires/`, `comptables/`, `api/`.

## Export PDF (cabinet/urls.py)
- Endpoint: `export/pdf/<str:type>/` → `ExportPDFView`.
- Types supportés:
  - `rapport-comptables` → Rapport des comptables.
  - `rapport-dossiers` → Rapport des dossiers.
  - `rapport-honoraires` → Rapport des honoraires.
  - `suivi-tva` → Rapport suivi TVA (année courante par défaut).

## Exemples d’URL
- `http://localhost:8000/export/pdf/rapport-comptables/`
- `http://localhost:8000/export/pdf/rapport-dossiers/`
- `http://localhost:8000/export/pdf/rapport-honoraires/`
- `http://localhost:8000/export/pdf/suivi-tva/`

## Authentification
- Login: `http://localhost:8000/accounts/login/`
- Accueil/Dashboard: `http://localhost:8000/`

## Remarque
- Pas de préfixe `/cabinet/` dans l’URL car `cabinet.urls` est inclus à la racine.