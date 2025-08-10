from django.contrib import admin
from cabinet.models import Document
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['fichier', 'dossier']
    readonly_fields = ['texte_extrait']  # <-- affiche le champ extrait

