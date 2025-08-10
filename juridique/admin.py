from django.contrib import admin
from django.contrib import admin
from .models import JuridiqueCreation, DocumentJuridique, EvenementJuridique


@admin.register(JuridiqueCreation)
class JuridiqueCreationAdmin(admin.ModelAdmin):
    list_display = [
       'dossier', 'statut_global', 'pourcentage_completion', 'date_creation'
    ]
    list_filter = ['statut_global']
    search_fields = ['dossier__denomination', 'ordre', 'forme']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('dossier', 'ordre', 'forme', 'statut_global')
        }),
        ('Documents', {
            'fields': (
                ('certificat_negatif', 'date_certificat_negatif'),
                ('statuts', 'date_statuts'),
                ('contrat_bail', 'date_contrat_bail')
            )
        }),
        ('Formalités administratives', {
            'fields': (
                ('tp', 'date_tp'),
                ('rc', 'date_rc', 'numero_rc'),
                ('cnss', 'date_cnss', 'numero_cnss'),
                ('al', 'date_al'),
                ('bo', 'date_bo'),
                ('rq', 'date_rq')
            )
        }),
        ('Remarques', {
            'fields': ('remarques',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentJuridique)
class DocumentJuridiqueAdmin(admin.ModelAdmin):
    list_display = [
        'code','nom_document', 'dossier', 'type_document', 'date_document', 'statut'
    ]
    list_filter = ['type_document', 'statut', 'dossier']
    search_fields = ['nom_document', 'description', 'dossier__denomination']
    date_hierarchy = 'date_document'

@admin.register(EvenementJuridique)
class EvenementJuridiqueAdmin(admin.ModelAdmin):
    list_display = [
        'code','type_evenement', 'dossier', 'date_evenement', 'statut'
    ]
    list_filter = ['code','type_evenement', 'statut', 'dossier']
    search_fields = ['code','type_evenement', 'description', 'dossier__denomination']
    date_hierarchy = 'date_evenement'
    readonly_fields = ['date_creation', 'date_modification']


