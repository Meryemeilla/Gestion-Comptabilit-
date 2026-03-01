from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Comptable

User = get_user_model()

class ComptableUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class ComptableForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, help_text="Requis. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ uniquement.")
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirmer le mot de passe")

    class Meta:
        model = Comptable
        fields = ['matricule', 'nom', 'prenom', 'cnss', 'tel', 'tel_personnel', 'email', 'email_personnel', 'adresse']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Les mots de passe ne correspondent pas")
        return cleaned_data
