from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from comptables.models import Comptable
from dossiers.models import Dossier
from utilisateurs.models import Client, Utilisateur
from django.core.exceptions import ValidationError

User = get_user_model()


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

class ComptableUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class ComptableForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.")
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm Password")

    class Meta:
        model = Comptable
        fields = ['matricule', 'nom', 'prenom', 'cnss', 'tel', 'tel_personnel', 'email', 'email_personnel', 'adresse']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords don't match")
        return cleaned_data
from django.forms import DateField
from cabinet.util import parse_french_date
from django.forms import Textarea 
from django import forms
from .models import Dossier
from django.forms import DateField

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



class ClientCreationForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telephone'].required = True

    def clean_password2(self):
        # Valide uniquement que les deux mots de passe correspondent, sans appliquer les règles strictes
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return password2

    def _post_clean(self):
        """
        Override la méthode `_post_clean` pour **ne pas** appeler `validate_password`
        (qui applique les règles de sécurité Django sur le mot de passe).
        """
        super(forms.ModelForm, self)._post_clean()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'
        if commit:
            user.save()
        return user


    
class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone'] 
from utilisateurs.tasks import envoyer_email_nouveau_client
class ClientRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    telephone = forms.CharField(max_length=20, required=False)
    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'password1', 'password2']

    def save(self, commit=True):
        print("[DEBUG] Appel de save() dans ClientRegisterForm")
        user = super().save(commit=False)
        user.role = 'client'

        print(f"[DEBUG] Données utilisateur : {user.username}, {user.first_name}, {user.last_name}, {user.email}, {self.cleaned_data.get('telephone')}")
        if commit:
            user.save()
            if not Client.objects.filter(user=user).exists():
                client=Client.objects.create(
                    user=user,
                    contact_personne=f"{user.first_name} {user.last_name}".strip(),
                    email=user.email,
                    telephone=self.cleaned_data.get('telephone'),
                )
                print(f" Client créé : {client}")
            else:
                print(f" Client déjà existant : {user.username}")
            
            envoyer_email_nouveau_client.delay(user.id)
        return user




