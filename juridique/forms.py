"""
Formulaires Django et validation.

Fichier: juridique/forms.py
"""

# ==================== Imports ====================
from django import forms
from .models import DocumentJuridique
from django import forms
from .models import JuridiqueCreation

# ==================== Classes ====================
class JuridiqueCreationForm(forms.ModelForm):
    class Meta:
        model = JuridiqueCreation
        fields = '__all__'
        widgets = {
            # Documents obligatoires
            'certificat_negatif': forms.CheckboxInput(attrs={
                'id': 'id_certificat_negatif'
            }),
            'date_certificat_negatif': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'sf-form-control sf-date-input',
                'id': 'id_date_certificat_negatif'
            }),
            'statuts': forms.CheckboxInput(attrs={
                'id': 'id_statuts'
            }),
            'date_statuts': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'sf-form-control sf-date-input',
                'id': 'id_date_statuts'
            }),
            'contrat_bail': forms.CheckboxInput(attrs={
                'id': 'id_contrat_bail'
            }),
            'date_contrat_bail': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'sf-form-control sf-date-input',
                'id': 'id_date_contrat_bail'
            }),

            # Formalités administratives
            'tp': forms.CheckboxInput(attrs={
                'id': 'id_tp'
            }),
            'date_tp': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'sf-form-control sf-date-input',
                'id': 'id_date_tp'
            }),
            'rc': forms.CheckboxInput(attrs={
                'id': 'id_rc'
            }),
            'date_rc': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'sf-form-control sf-date-input',
                'id': 'id_date_rc'
            }),
            'numero_rc': forms.TextInput(attrs={
                'id': 'id_numero_rc'
            }),
            'cnss': forms.CheckboxInput(attrs={
                'id': 'id_cnss'
            }),
            'date_cnss': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'sf-form-control sf-date-input',
                'id': 'id_date_cnss'
            }),
            'numero_cnss': forms.TextInput(attrs={
                'id': 'id_numero_cnss'
            }),
            'al': forms.CheckboxInput(attrs={
                'id': 'id_al'
            }),
            'date_al': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'sf-form-control sf-date-input',
                'id': 'id_date_al'
            }),
            'bo': forms.CheckboxInput(attrs={
                'id': 'id_bo'
            }),
            'date_bo': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'sf-form-control sf-date-input',
                'id': 'id_date_bo'
            }),
            'rq': forms.CheckboxInput(attrs={
                'id': 'id_rq'
            }),
            'date_rq': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'sf-form-control sf-date-input',
                'id': 'id_date_rq'
            }),

            # Champs divers
            'remarques': forms.Textarea(attrs={
                'id': 'id_remarques',
                'class': 'sf-form-control'
            }),
            'ordre': forms.TextInput(attrs={
                'id': 'id_ordre',
                'class': 'sf-form-control'
            }),
            'forme': forms.TextInput(attrs={
                'id': 'id_forme',
                'class': 'sf-form-control'
            }),
            'statut_global': forms.Select(attrs={
                'id': 'id_statut_global',
                'class': 'sf-form-control'
            }),
            'dossier': forms.Select(attrs={
                'id': 'id_dossier',
                'class': 'sf-form-control'
            }),
        }

class DocumentJuridiqueForm(forms.ModelForm):
    class Meta:
        model = DocumentJuridique
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'sf-form-control', 'placeholder': 'Entrer le nom du document'}),
        }
