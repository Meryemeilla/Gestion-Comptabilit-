# Maintenance: Archivage et Vidage des Répertoires de Documents

Objectif: archiver ou vider les répertoires `documents_dossiers/` et `documents_juridiques/` lorsqu’ils ne sont plus utilisés, sans impacter l’application ni les données actives.

## Périmètre
- Répertoires ciblés:
  - `documents_dossiers/`
  - `documents_juridiques/`
- Non inclus: code source, templates, base de données.

## Politique de rétention (recommandée)
- Conservation 12 mois glissants des documents.
- Archivage mensuel dans `archives/<YYYY-MM>/` avec compression ZIP.
- Suppression définitive uniquement après validation métier.

## Détection des fichiers non utilisés
1. Vérifier les références en base aux pièces (modèles pouvant référencer ces fichiers):
   - `reclamations` (dossier de pièces jointes)
   - `dossiers` (documents de dossiers)
   - `juridique` (documents juridiques)
2. Exporter les chemins/réfs en base et comparer avec le contenu des répertoires.

Exemple (PowerShell) pour lister les fichiers présents:
```
$root = "c:\\Users\\lenovo\\Downloads\\Gestion-Comptabilité"
Get-ChildItem "$root\documents_dossiers" -Recurse -File | Select-Object FullName | Export-Csv "$root\docs\inventaire_documents_dossiers.csv" -NoTypeInformation
Get-ChildItem "$root\documents_juridiques" -Recurse -File | Select-Object FullName | Export-Csv "$root\docs\inventaire_documents_juridiques.csv" -NoTypeInformation
```

## Archivage (sécurisé)
1. Créer le dossier d’archives:
```
$root = "c:\\Users\\lenovo\\Downloads\\Gestion-Comptabilité"
$month = Get-Date -Format "yyyy-MM"
$newArchive = "$root\archives\$month"
New-Item -ItemType Directory -Force -Path $newArchive
```
2. Compresser et déplacer les fichiers non référencés (après validation):
```
Compress-Archive -Path "$root\documents_dossiers\*" -DestinationPath "$newArchive\documents_dossiers.zip"
Compress-Archive -Path "$root\documents_juridiques\*" -DestinationPath "$newArchive\documents_juridiques.zip"
```
3. Vidage des répertoires (optionnel, si validé):
```
Remove-Item -Recurse -Force "$root\documents_dossiers\*"
Remove-Item -Recurse -Force "$root\documents_juridiques\*"
```

## Étapes de sécurité
- Faire une sauvegarde avant toute suppression.
- Travailler en dehors des heures d’activité.
- Valider la liste des fichiers avec l’équipe métier.
- Conserver un journal des actions (date, contenu archivé, taille).

## Automatisation (optionnelle)
- Planifier un job mensuel d’archivage (Task Scheduler) basé sur ce guide.
- Générer un rapport CSV de l’archivage: taille, nombre de fichiers, emplacements.

## Intégration Git
- Les répertoires de documents sont hors VCS (voir `.gitignore`).
- Ne versionner que les scripts/documentation liés à la maintenance.

## Checklist rapide
- [ ] Exporter l’inventaire des fichiers présents.
- [ ] Compiler les références en base.
- [ ] Identifier les fichiers non référencés.
- [ ] Valider la liste avec le métier.
- [ ] Archiver (ZIP) vers `archives/<YYYY-MM>/`.
- [ ] Vider les répertoires si validé.
- [ ] Consigner les actions dans un journal.