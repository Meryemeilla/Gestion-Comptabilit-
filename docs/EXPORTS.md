# Exports (PDF & Excel)

## Export Excel
- Fichier: `cabinet/utils/export.py`.
- Rôle: générer des fichiers Excel pour différents domaines (clients, honoraires, fiscal…).

## Export PDF
- Fichier: `cabinet/utils/pdf_export.py`.
- Design:
  - Import WeasyPrint paresseux (`from weasyprint import HTML, CSS`) à l’intérieur de chaque méthode d’export.
  - CSS injectée via chaîne: `CSS(string=self.css_style_string)` instanciée localement.
  - Appels `write_pdf` protégés par `try/except` avec fallback `HttpResponse(status=503)` en cas d’échec.
- Vue:
  - `ExportPDFView` (dans `cabinet/views.py`) importe `ExportPDF` de manière paresseuse et route selon `type`.

## Dépendances Système (Windows)
- Installer MSYS2 et paquets:
  - `mingw-w64-x86_64-pango`, `mingw-w64-x86_64-cairo`, `mingw-w64-x86_64-glib2`, `mingw-w64-x86_64-libffi`.
- Ajouter `C:\msys64\mingw64\bin` au `PATH` système.
- WeasyPrint: version compatible Windows (ex: `pip install weasyprint==57.*`).

## Diagnostic
- En cas d’échec WeasyPrint/GTK, les endpoints d’export renvoient 503 sans faire planter le serveur.
- Consulter les logs du terminal pour les messages `OSError: cannot load library 'gobject-2.0-0'` si dépendances manquantes.

## URLs d’Export
- Voir `docs/ROUTES.md` (section export PDF).