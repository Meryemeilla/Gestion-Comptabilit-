"""
Formulaires Django et validation.

Fichier: utilisateurs/forms.py
"""

# ==================== Imports ====================
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur
from comptables.models import Comptable



# ==================== Classes ====================
class ComptableRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telephone = forms.CharField(required=False)
    tel_personnel = forms.CharField(required=False, label="Téléphone personnel")

    class Meta:
        model = Utilisateur
        fields = ('username', 'email', 'telephone', 'tel_personnel', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'comptable'
        user.is_active = True  # User is active but comptable profile needs approval
        user.tel_personnel = self.cleaned_data.get('tel_personnel')
        if commit:
            print(f"DEBUG: Before save - User role: {user.role}")
            user.save()
            print(f"DEBUG: After save - User role: {user.role}")
            # Create the associated Comptable profile
            comptable_profile, created = Comptable.objects.get_or_create(
                user=user,
                defaults={
                    'nom': user.last_name if user.last_name else 'Nom',
                    'prenom': user.first_name if user.first_name else 'Prénom',
                    'email': user.email,
                    'tel': user.telephone,
                    'tel_personnel': user.tel_personnel,
                    'is_approved': False
                }
            )
            if not created:
                comptable_profile.is_approved = False
                comptable_profile.save()
        return user