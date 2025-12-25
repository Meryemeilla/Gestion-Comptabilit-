# Organisation du Projet

Ce dossier `docs/` centralise l'organisation, les conventions et les cartes du projet afin de faciliter la maintenance et l'évolution.

## Sommaire
- ARCHITECTURE.md: structure des apps et responsabilités.
- CONVENTIONS.md: règles de séparation (views/services/utils/tasks/managers/tests).
- ROUTES.md: cartographie des endpoints (notamment exports PDF/Excel).
- EXPORTS.md: design des exports, dépendances systèmes (WeasyPrint/Windows).
- MODULE_MAP.md: carte des fichiers clés par app.

## Utilisation
- Lire ARCHITECTURE.md pour comprendre le découpage global.
- Lire CONVENTIONS.md pour respecter les responsabilités par fichier.
- Lire ROUTES.md pour retrouver rapidement les endpoints.
- Lire EXPORTS.md pour activer/diagnostiquer les exports.
- Lire MODULE_MAP.md pour localiser les modules importants.

## Principes
- N’implémente pas de changements de code ici; documentation seulement.
- Favorise les imports paresseux pour les dépendances lourdes (WeasyPrint) et des fallbacks HTTP contrôlés (503) en cas d’échec.
- Encourage la logique métier dans `services.py` pour testabilité et réutilisation.