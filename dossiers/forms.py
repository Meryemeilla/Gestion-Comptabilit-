from django import forms
from django.forms import DateField, Textarea
from .models import Dossier
from cabinet.util import parse_french_date

class BaseDossierForm(forms.ModelForm):
    class Meta:
        model = Dossier
        exclude = ['statut']

class ClientDossierForm(BaseDossierForm):
    class Meta(BaseDossierForm.Meta):
        exclude = BaseDossierForm.Meta.exclude + ['client', 'comptable_traitant']

class ComptableDossierForm(BaseDossierForm):
    class Meta(BaseDossierForm.Meta):
        exclude = BaseDossierForm.Meta.exclude + ['comptable_traitant']

class DossierForm(forms.ModelForm):
    date_creation = DateField(
        required=False,
        input_formats=['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d %B %Y', '%d %b %Y']
    )

    branche_activite = forms.CharField(
        label="Branche d'activité",
        widget=forms.Textarea(attrs={
            'rows': 4,
            'cols': 60,
            'class': 'form-control',
            'placeholder': 'Ex: Vente de matériel, développement de logiciels, etc.'
        })
    )

    class Meta:
        model = Dossier
        exclude = ['cree_par']

    def clean_date_creation(self):
        raw = self.cleaned_data.get('date_creation')
        if not raw:
            return None

        parsed = parse_french_date(raw)
        if parsed:
            return parsed
        raise forms.ValidationError("Format de date non reconnu. Exemple : 14 mars 2025 ou 14/03/2025")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_creation'].required = False
        self.fields['client'].label_from_instance = lambda obj: f"{obj.nom} {obj.prenom}"
        self.fields['statut_fiscal'].label = "Statut fiscal"
        self.fields['statut_fiscal'].required = False
        self.fields['documents'] = forms.FileField(required=False)
