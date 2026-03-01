"""
Formulaires Django et validation.

Fichier: cabinet/forms.py
"""

# ==================== Imports ====================
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from comptables.models import Comptable
from dossiers.models import Dossier
from utilisateurs.models import Client, Utilisateur
from django.core.exceptions import ValidationError

User = get_user_model()


# ==================== Classes ====================
# Les formulaires Dossier ont été déplacés vers dossiers/forms.py

# Les formulaires ComptableUserCreationForm et ComptableForm ont été déplacés vers comptables/forms.py
from django.forms import DateField
from cabinet.util import parse_french_date
from django.forms import Textarea 
from django import forms
from .models import Dossier
from django.forms import DateField

# Le formulaire DossierForm a été déplacé vers dossiers/forms.py



# Les formulaires Client ont été déplacés vers utilisateurs/forms.py




