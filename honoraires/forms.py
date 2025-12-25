"""
Formulaires Django et validation.

Fichier: honoraires/forms.py
"""

# ==================== Imports ====================
from django import forms
from django import forms
from .models import Honoraire, ReglementHonoraire, HonorairePV, ReglementHonorairePV


# ==================== Classes ====================
class HonoraireForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    class Meta:
        model = Honoraire
        fields = [
            'code',
            'dossier',
            'montant_mensuel',
            'montant_trimestriel',
            'montant_annuel',
            'statut_reglement',
            'date_echeance',
        ]
        widgets = {
            'date_echeance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'code': 'Code',
            'dossier': 'Dossier concerné',
            'montant_mensuel': 'Montant mensuel',
            'montant_trimestriel': 'Montant trimestriel',
            'montant_annuel': 'Montant annuel',
            'statut_reglement': 'Statut du règlement',
            'date_echeance': 'Date d\'échéance',
        }



class CombinedHonoraireChoiceField(forms.ChoiceField):
    pass

from django import forms
from .models import Honoraire, HonorairePV, ReglementHonoraire

class ReglementHonoraireForm(forms.ModelForm):
    combined_honoraire = CombinedHonoraireChoiceField(label="Honoraire / Honoraire PV concerné")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialisation des choix pour combined_honoraire
        honoraires = Honoraire.objects.all()
        honoraires_pv = HonorairePV.objects.all()
        choices = []
        for h in honoraires:
            dossier_denomination_h = h.dossier.denomination if h.dossier else 'N/A'
            choices.append((f"H_{h.pk}", f"Honoraire: {h.code} - {dossier_denomination_h}"))
        for hpv in honoraires_pv:
            dossier_denomination_hpv = hpv.dossier.denomination if hpv.dossier else 'N/A'
            choices.append((f"HPV_{hpv.pk}", f"Honoraire PV: {hpv.code} - {dossier_denomination_hpv}"))
        self.fields['combined_honoraire'].choices = choices

        # Définir la valeur initiale si instance existante
        if self.instance.pk:
            if self.instance.honoraire:
                self.initial['combined_honoraire'] = f"H_{self.instance.honoraire.pk}"
            elif self.instance.honoraire_pv:
                self.initial['combined_honoraire'] = f"HPV_{self.instance.honoraire_pv.pk}"

        # Récupérer la valeur du champ combined_honoraire venant de l'initial ou du POST
        combined_value = (
            self.initial.get('combined_honoraire') or
            (self.data.get('combined_honoraire') if self.data else None)
        )

        # Si c'est un honoraire PV, masquer ou rendre optionnel type_reglement
        if combined_value and combined_value.startswith('HPV_'):
            self.fields['type_reglement'].required = False
            self.fields['type_reglement'].widget = forms.HiddenInput()

    class Meta:
        model = ReglementHonoraire
        fields = [
            'date_reglement',
            'montant',
            'type_reglement',
            'mode_paiement',
            'numero_piece',
            'remarques',
            'combined_honoraire',
        ]
        widgets = {
            'date_reglement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'remarques': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'date_reglement': 'Date du règlement',
            'montant': 'Montant réglé (DH)',
            'type_reglement': 'Type de règlement',
            'mode_paiement': 'Mode de paiement',
            'numero_piece': 'Numéro de pièce',
            'remarques': 'Remarques',
        }

    def clean(self):
        cleaned_data = super().clean()
        combined_value = cleaned_data.get('combined_honoraire')
        type_reglement = cleaned_data.get('type_reglement')

        if combined_value and combined_value.startswith('H_'):
            # Pour Honoraire classique, type_reglement est obligatoire
            if not type_reglement:
                self.add_error('type_reglement', "Ce champ est obligatoire pour un honoraire classique.")
        else:
            # Pour Honoraire PV, on peut forcer type_reglement à None ou valeur par défaut si besoin
            cleaned_data['type_reglement'] = None

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        combined_value = self.cleaned_data['combined_honoraire']
        if combined_value.startswith('H_'):
            pk = combined_value.split('_')[1]
            instance.honoraire = Honoraire.objects.get(pk=pk)
            instance.honoraire_pv = None
        elif combined_value.startswith('HPV_'):
            pk = combined_value.split('_')[1]
            instance.honoraire_pv = HonorairePV.objects.get(pk=pk)
            instance.honoraire = None

        if commit:
            instance.save()
        return instance




class HonorairePVForm(forms.ModelForm):
    class Meta:
        model = HonorairePV
        fields = ['code', 'dossier', 'montant_total', 'description']
        widgets = {
            # ajoute ici les widgets si besoin, ex: 'date_creation': forms.DateInput(attrs={'type': 'date'})
        }
        labels = {
            'code': 'Code',
            'dossier': 'Dossier',
            'montant_total': 'Montant Total',
            'description': 'Description',
            
        }



class ReglementHonorairePVForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = ReglementHonorairePV
        fields = [
            'honoraire_pv',
            'date_reglement',
            'montant',
            'type_reglement',
            'reference',
        ]
        widgets = {
            'date_reglement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'honoraire_pv': 'Honoraire PV concerné',
            'date_reglement': 'Date du règlement',
            'montant': 'Montant réglé (DH)',
            'type_reglement': 'Type de règlement',
            'reference': 'Référence',
        }