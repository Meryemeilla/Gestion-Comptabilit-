"""
Module applicatif.

Fichier: tools/add_headers.py
"""

# ==================== Imports ====================
import os
import sys
from pathlib import Path

# ==================== Constantes ====================
EXCLUDED_DIRS = {
    'envGestion', 'docs', 'templates', 'documents_dossiers', 'documents_juridiques', '__pycache__'
}

DESCRIPTIONS = {
    'views.py': 'Django views (gestion des requêtes HTTP).',
    'urls.py': 'Définition des routes URL et namespaces.',
    'models.py': 'Modèles Django et logique d’accès aux données.',
    'forms.py': 'Formulaires Django et validation.',
    'services.py': 'Services métier réutilisables et testables.',
    'managers.py': 'Managers ORM personnalisés pour les QuerySets.',
    'tasks.py': 'Tâches asynchrones (Celery, planifications).',
    'signals.py': 'Signaux et hooks (post_save, etc.).',
    'admin.py': 'Enregistrements et personnalisation Admin Django.',
    'apps.py': 'Configuration d’application Django.',
    'serializers.py': 'Sérialiseurs API (DRF).',
    'viewsets.py': 'ViewSets API (DRF).',
    'wsgi.py': 'Point d’entrée WSGI.',
    'asgi.py': 'Point d’entrée ASGI.',
    'settings.py': 'Paramétrage du projet Django.',
    '__init__.py': 'Initialisation du module Python.',
}

HEADER_TEMPLATE = '"""\n{desc}\n\nFichier: {rel}\n"""\n\n'

# ==================== Fonctions ====================
def has_module_docstring(text: str) -> bool:
    # Détecter une docstring en tête: première instruction triple quotes
    stripped = text.lstrip()
    return stripped.startswith('"""') or stripped.startswith("'''")


def insert_header(text: str, header: str) -> str:
    # Respect d’un éventuel shebang ou ligne d’encodage
    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines:
        if lines[0].startswith('#!'):
            insert_at = 1
        elif lines[0].lower().startswith('# -*- coding:') or ('coding:' in lines[0].lower()):
            insert_at = 1
    return ''.join(lines[:insert_at]) + header + ''.join(lines[insert_at:])


def guess_desc(file_name: str, parent: str) -> str:
    base = os.path.basename(file_name)
    if base in DESCRIPTIONS:
        return DESCRIPTIONS[base]
    # Heuristique pour utils
    if 'utils' in parent:
        return 'Fonctions utilitaires et helpers techniques.'
    return 'Module applicatif.'


def should_skip(path: Path) -> bool:
    parts = set(p.name for p in path.parents)
    if any(d in parts for d in EXCLUDED_DIRS):
        return True
    # Ignorer site-packages du venv
    if 'site-packages' in path.as_posix():
        return True
    return False


def main(root_dir: Path) -> int:
    changed = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filtrer les dirs exclus
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for fname in filenames:
            if not fname.endswith('.py'):
                continue
            fpath = Path(dirpath) / fname
            if should_skip(fpath):
                continue
            try:
                text = fpath.read_text(encoding='utf-8')
            except Exception:
                continue
            if has_module_docstring(text):
                continue  # Ne pas dupliquer
            rel = fpath.relative_to(root_dir).as_posix()
            desc = guess_desc(fname, Path(dirpath).name)
            header = HEADER_TEMPLATE.format(desc=desc, rel=rel)
            new_text = insert_header(text, header)
            try:
                fpath.write_text(new_text, encoding='utf-8')
                changed += 1
            except Exception:
                continue
    print(f"Headers ajoutés dans {changed} fichiers.")
    return 0


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    sys.exit(main(root))