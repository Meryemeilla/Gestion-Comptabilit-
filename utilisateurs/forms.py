"""
Formulaires Django et validation.

Fichier: utilisateurs/forms.py
"""

# ==================== Imports ====================
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur, Client
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
            user.save()
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

class ClientRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    telephone = forms.CharField(max_length=20, required=False)
    nom_entreprise = forms.CharField(max_length=200, required=False)

    class Meta:
        model = Utilisateur
        fields = ('username', 'first_name', 'last_name', 'email', 'telephone', 'nom_entreprise')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                contact_personne=f"{user.first_name} {user.last_name}",
                email=user.email,
                telephone=user.telephone,
                nom_entreprise=self.cleaned_data.get('nom_entreprise')
            )
        return user

class ClientCreationForm(forms.ModelForm):
    # User fields
    username = forms.CharField(max_length=150, required=True, label="Nom d'utilisateur")
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, label="Mot de passe")
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirmation")
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")

    class Meta:
        model = Client
        fields = ['nom_entreprise', 'email', 'telephone', 'adresse']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Utilisateur.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        # Create User
        user = Utilisateur.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role='client'
        )
        
        # Create Client profile
        client = super().save(commit=False)
        client.user = user
        client.contact_personne = f"{user.first_name} {user.last_name}"
        if commit:
            client.save()
        return client

class ClientUpdateForm(forms.ModelForm):
    # User fields to edit
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True)
    # Use password1 and password2 for consistency with template
    password1 = forms.CharField(widget=forms.PasswordInput, required=False, label="Nouveau mot de passe")
    password2 = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirmation")

    class Meta:
        model = Client
        fields = ['nom_entreprise', 'telephone', 'adresse']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        client = super().save(commit=False)
        user = client.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        new_password = self.cleaned_data.get('password1')
        if new_password:
            user.set_password(new_password)
            
        if commit:
            user.save()
            client.contact_personne = f"{user.first_name} {user.last_name}"
            client.email = user.email
            client.save()
        return client