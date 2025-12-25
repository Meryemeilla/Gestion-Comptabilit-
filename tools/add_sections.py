import os
import re
from pathlib import Path

EXCLUDED_DIRS = {
    'envGestion', 'docs', 'templates', 'documents_dossiers', 'documents_juridiques', '__pycache__'
}
SECTION_MARKERS = {
    'imports': '# ==================== Imports ====================\n',
    'constantes': '# ==================== Constantes ====================\n',
    'classes': '# ==================== Classes ====================\n',
    'fonctions': '# ==================== Fonctions ====================\n',
    'handlers': '# ==================== Handlers ====================\n',
}

IMPORT_RE = re.compile(r'^(?:from\s+\S+\s+import\s+|import\s+\S+)')
CONST_RE = re.compile(r'^[A-Z_][A-Z0-9_]*\s*=')
CLASS_RE = re.compile(r'^class\s+\w')
DEF_RE = re.compile(r'^def\s+\w')

MARKER_PRESENT_RE = re.compile(r'#\s*=+\s*(Imports|Constantes|Classes|Fonctions|Handlers)\s*=+')


def should_skip(path: Path) -> bool:
    parts = set(p.name for p in path.parents)
    if any(d in parts for d in EXCLUDED_DIRS):
        return True
    if 'site-packages' in path.as_posix():
        return True
    return False


def find_first_indices(lines):
    first_import = first_const = first_class = first_def = None
    for i, line in enumerate(lines):
        # Ignorer lignes indentées (non top-niveau)
        if line.startswith((' ', '\t')):
            continue
        if first_import is None and IMPORT_RE.match(line):
            first_import = i
            continue
        if first_const is None and CONST_RE.match(line):
            first_const = i
            continue
        if first_class is None and CLASS_RE.match(line):
            first_class = i
            continue
        if first_def is None and DEF_RE.match(line):
            first_def = i
            continue
    return first_import, first_const, first_class, first_def


def marker_already_present(lines):
    return any(MARKER_PRESENT_RE.search(l) for l in lines)


def insert_markers(file_path: Path) -> bool:
    try:
        text = file_path.read_text(encoding='utf-8')
    except Exception:
        return False
    lines = text.splitlines(keepends=True)

    # Ne pas dupliquer si des marqueurs existent déjà
    if marker_already_present(lines):
        return False

    first_import, first_const, first_class, first_def = find_first_indices(lines)

    inserts = []
    base = file_path.name

    # Insérer Imports si présents
    if first_import is not None:
        inserts.append((first_import, SECTION_MARKERS['imports']))

    # Déterminer si fichier de vues
    is_views = base == 'views.py' or base == 'views_api.py'

    if is_views:
        # Pour les vues, insérer Handlers avant le premier handler (def ou class)
        handler_pos_candidates = [p for p in [first_class, first_def] if p is not None]
        if handler_pos_candidates:
            inserts.append((min(handler_pos_candidates), SECTION_MARKERS['handlers']))
    else:
        # Constantes, Classes, Fonctions
        if first_const is not None:
            inserts.append((first_const, SECTION_MARKERS['constantes']))
        if first_class is not None:
            inserts.append((first_class, SECTION_MARKERS['classes']))
        if first_def is not None:
            inserts.append((first_def, SECTION_MARKERS['fonctions']))

    if not inserts:
        return False

    # Appliquer les insertions en ordre croissant d’index, avec offset
    inserts.sort(key=lambda x: x[0])
    offset = 0
    for pos, marker in inserts:
        idx = pos + offset
        lines.insert(idx, marker)
        offset += 1

    new_text = ''.join(lines)
    try:
        file_path.write_text(new_text, encoding='utf-8')
        return True
    except Exception:
        return False


def main(root_dir: Path) -> int:
    changed = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for fname in filenames:
            if not fname.endswith('.py'):
                continue
            fpath = Path(dirpath) / fname
            if should_skip(fpath):
                continue
            if insert_markers(fpath):
                changed += 1
    print(f"Séparateurs de sections ajoutés dans {changed} fichiers.")
    return 0


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    raise SystemExit(main(root))