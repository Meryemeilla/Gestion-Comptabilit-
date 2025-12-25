"""
Formulaires Django et validation.

Fichier: fiscal/forms.py
"""

# ==================== Imports ====================
from django import forms
from .models import Acompte

# ==================== Classes ====================
class AcompteForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = Acompte
        exclude = ['montant']
        labels = {
            'is_montant': 'Montant IS',
            # autres labels si besoin
        }