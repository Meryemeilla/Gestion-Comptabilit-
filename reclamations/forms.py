from django import forms
from django.contrib.auth import get_user_model
from .models import Reclamation , Dossier 
from utilisateurs.models import Utilisateur , Client
User = get_user_model()

class ReclamationForm(forms.ModelForm):
    code = forms.CharField(label="Code", max_length=100, required=True)

    class Meta:
        model = Reclamation
        fields = [
            'code', 'dossier', 'type_reclamation', 'date_reception',
            'reponse', 'suivi', 'remarque', 'classement',
            'priorite', 'destinataire', 'document'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Gérer les dossiers selon le rôle
            if user.role == 'client':
                client = getattr(user, 'client_profile', None)
                if client:
                    self.fields['dossier'].queryset = Dossier.objects.filter(client=client)
                else:
                    self.fields['dossier'].queryset = Dossier.objects.none()

            elif user.role in ['comptable', 'administrateur']:
                self.fields['dossier'].queryset = Dossier.objects.all()

            else:
                self.fields['dossier'].queryset = Dossier.objects.none()

            # Gérer le champ destinataire
            if user.role == 'client':
                #  Supprimer complètement le champ destinataire pour le client
                self.fields.pop('destinataire', None)

            elif user.role in ['comptable', 'administrateur']:
                self.fields['dossier'].queryset = Dossier.objects.all()

            else:
                #  Afficher les clients comme destinataires pour les rôles autorisés
                self.fields['destinataire'].queryset = Utilisateur.objects.filter(role='client')
            
            if user.role != 'client':
                self.fields.pop('destinataire', None)




# forms.py
from django import forms

class ReclamationSearchForm(forms.Form):
    code = forms.CharField(required=False, label="Code")
    denomination = forms.CharField(required=False, label="Dénomination de dossier")
    classement = forms.ChoiceField(
        required=False,
        choices=[('', '---')] + Reclamation.CLASSEMENT_CHOICES,  # ou ta liste de choix
        label="Classement"
    )
