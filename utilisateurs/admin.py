"""
Enregistrements et personnalisation Admin Django.

Fichier: utilisateurs/admin.py
"""

# ==================== Imports ====================
from django.contrib import admin
from .models import Utilisateur, Client
from dossiers.models import Dossier
from django import forms
from dossiers.admin import DossierAdmin

# ==================== Classes ====================
class UtilisateurAdminForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = '__all__'

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            raise forms.ValidationError('Le champ rôle est obligatoire.')
        return role

class UtilisateurAdmin(admin.ModelAdmin):
    form = UtilisateurAdminForm
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'telephone', 'tel_personnel')}),
        ('Rôle', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(Utilisateur, UtilisateurAdmin)
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom_entreprise', 'contact_personne', 'email', 'user')
    search_fields = ('nom_entreprise', 'email', 'user__username')
    list_filter = ('user__is_active',)



# Register your models here.
