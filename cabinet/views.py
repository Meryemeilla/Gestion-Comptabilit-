"""
Django views (gestion des requêtes HTTP).

Fichier: cabinet/views.py
"""

# ==================== Imports ====================
import os
import json
import logging
from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django import forms
from django.db.models import ProtectedError, Count, Q, Sum
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db.models.functions import ExtractYear, ExtractMonth
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group

from utilisateurs.models import Client, Utilisateur, RoleRequiredMixin
from comptables.models import Comptable
from dossiers.models import Dossier
from honoraires.models import Honoraire, ReglementHonoraire, HonorairePV, ReglementHonorairePV
from fiscal.models import Acompte, CMIR, DepotBilan, SuiviTVA, SuiviForfaitaire
from reclamations.models import Reclamation
from juridique.models import JuridiqueCreation, DocumentJuridique, EvenementJuridique

from .utils.export import ExportExcel
from .utils.email import EmailService
from .models import Notification
# ==================== Handlers ====================
class DashboardView(RoleRequiredMixin, LoginRequiredMixin, TemplateView):
    allowed_roles = ['administrateur', 'manager', 'comptable', 'client']
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_is_comptable'] = getattr(self.request.user, 'role', None) == 'comptable' or (hasattr(self.request.user, 'is_comptable') and self.request.user.is_comptable())
        
        # Statistiques générales
        context['total_comptables'] = Comptable.objects.filter(actif=True).count()
        context['total_dossiers'] = Dossier.objects.filter(actif=True).count()
        context['total_dossiers_pm'] = Dossier.objects.filter(actif=True, forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'EURL', 'SASU', 'SAS']).count()
        context['total_dossiers_pp'] = Dossier.objects.filter(actif=True, forme_juridique__in=['EI', 'EIRL', 'AUTO']).count()
        # Statistiques honoraires
        context['total_honoraires'] = Honoraire.objects.all().count()
        context['total_honoraires_en_attente'] = Honoraire.objects.filter(statut_reglement='EN_ATTENTE').count()
        context['total_honoraires_payes'] = Honoraire.objects.filter(statut_reglement='PAYE').count()
        # Statistiques acomptes
        from fiscal.models import Acompte, SuiviTVA, DepotBilan, SuiviForfaitaire, CMIR
        context['total_acomptes'] = Acompte.objects.all().count()
        context['total_acomptes_en_attente'] = Acompte.objects.filter(valide=False).count() if hasattr(Acompte, 'valide') else None
        # Statistiques TVA
        context['total_suivi_tva'] = SuiviTVA.objects.all().count()
        context['total_suivi_tva_mensuelle'] = SuiviTVA.objects.filter(dossier__declaration_tva='MENSUELLE').count()
        context['total_suivi_tva_trimestrielle'] = SuiviTVA.objects.filter(dossier__declaration_tva='TRIMESTRIELLE').count()
        # Statistiques Dépôt Bilan
        context['total_depot_bilan'] = DepotBilan.objects.all().count()
        # Statistiques Suivi Forfaitaire
        context['total_suivi_forfaitaire'] = SuiviForfaitaire.objects.all().count()
        # Réclamations urgentes
        user = self.request.user

        if user.role == 'administrateur':
            # L'administrateur voit le nombre total de réclamations destinées aux comptables
            context['reclamations_urgentes'] = Reclamation.objects.filter(
                destinataire__role='comptable'
            ).count()
        elif user.role == 'comptable':
            # Le comptable voit seulement celles qui lui sont destinées
            context['reclamations_urgentes'] = Reclamation.objects.filter(
                destinataire=user
            ).count()
        elif user.role == 'client':
            # Le client voit seulement celles qui lui sont destinées
            context['reclamations_urgentes'] = Reclamation.objects.filter(
                destinataire=user
            ).count()
        else:
            context['reclamations_urgentes'] = 0

        # Dossiers par comptable
        context['dossiers_par_comptable'] = Comptable.objects.filter(actif=True).annotate(
            nb_dossiers=Count('dossiers', filter=Q(dossiers__actif=True)),
            total_dossiers=Count('dossiers')
        ).order_by('-nb_dossiers')[:5]

        # Répartition par forme juridique
        context['repartition_forme_juridique'] = list(
            Dossier.objects.filter(actif=True)
            .values('forme_juridique')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        # Alertes honoraires et règlements
        context['alertes_honoraires'] = Honoraire.objects.filter(statut_reglement__in=['EN_ATTENTE', 'EN_RETARD'])
        context['alertes_reglements'] = ReglementHonoraire.objects.filter(statut_reglement__in=['EN_ATTENTE', 'EN_RETARD'])
        # Ajout du premier Honoraire pk pour le lien de règlement
        first_honoraire = Honoraire.objects.first()
        context['first_honoraire_pk'] = first_honoraire.pk if first_honoraire else None

        # Derniers documents juridiques
        if hasattr(user, 'client_profile'):
            client = user.client_profile
            dossiers = client.dossiers_client.all()
            context['documents_juridiques'] = (
                DocumentJuridique.objects
                .filter(dossier__in=dossiers)
                .order_by('-date_document')[:5]  # plusieurs documents pour le client
            )
            context['documents_is_list'] = True
        else:
            # Pour admin/comptable/manager : un seul document
            context['documents_juridiques'] = (
                DocumentJuridique.objects
                .all()
                .order_by('-date_document')
                .first()
            )
            context['documents_is_list'] = False


        


        # Documents récents liés au client connecté
        if hasattr(user, 'client_profile'):
            context['recent_documents'] = DocumentJuridique.objects.filter(
                dossier__client=user.client_profile
            ).order_by('-date_creation')[:5]

        else:
            context['recent_documents'] = []
            context['recent_activities'] = []

        # Prochains événements juridiques
        context['upcoming_events'] = EvenementJuridique.objects.filter(date_evenement__gte=timezone.now()).order_by('date_evenement')[:5]

        return context
class HonoraireDashboardView(RoleRequiredMixin, LoginRequiredMixin, TemplateView):
    allowed_roles = ['comptable', 'administrateur']
    template_name = 'honoraires/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Alertes : honoraires non payés ou en retard
        alertes_honoraires = Honoraire.objects.filter(
            statut_reglement__in=['EN_ATTENTE', 'EN_RETARD']
        )

        # Alertes : règlements non payés ou en retard
        alertes_reglements = ReglementHonoraire.objects.filter(
            statut_reglement__in=['EN_ATTENTE', 'EN_RETARD']
        )

        # Premier honoraire pour créer un règlement
        first_honoraire = Honoraire.objects.first()

        context.update({
            'alertes_honoraires': alertes_honoraires,
            'alertes_reglements': alertes_reglements,
            'first_honoraire_pk': first_honoraire.pk if first_honoraire else None
        })

        return context
# views.py
class DocumentsClientView(LoginRequiredMixin, TemplateView):
    template_name = "cabinet/documents_client.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_staff or user.is_superuser:
                context['documents'] = DocumentJuridique.objects.all().order_by('-date_document')
        else:
                # Si client : vérifier qu'il a un profil
            try:
                    client = user.client_profile
                    context['documents'] = DocumentJuridique.objects.filter(
                        dossier__client=client
                    ).order_by('-date_document')
            except AttributeError:
                    raise Http404("Aucun profil client associé à cet utilisateur.")

            return context
def est_admin(user):
    return user.is_authenticated and user.is_staff  # ou autre selon ta logique

from django.http import HttpResponse

from utilisateurs.tasks import envoyer_email_creation_client

# Les vues de gestion des clients (ajouter, supprimer, detail, liste, modifier)
# ont été déplacées vers utilisateurs/views.py




from utilisateurs.models import Client



from django.db.models import Count, Q

# Les vues de gestion des comptables (ListView, DetailView)
# ont été déplacées vers comptables/views.py

from utilisateurs.tasks import envoyer_email_creation_comptable

# Les statistiques admin de dossiers ont été déplacées vers dossiers/views.py


# Les vues de gestion des comptables (Create, Update, Delete)
# ont été déplacées vers comptables/views.py

# cabinet/views.py

from cabinet.util import extract_text_from_pdf

class DocumentCreateView(CreateView):
   

    def form_valid(self, form):
        response = super().form_valid(form)

        fichier = self.object.fichier
        if fichier:
            text = extract_text_from_pdf(fichier)
            print("Texte extrait :", text)  # Ou l’enregistrer dans un champ du modèle

        return response

class DossierListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['administrateur', 'manager', 'comptable', 'client']
    model = Dossier
    template_name = 'dossiers/list.html'
    context_object_name = 'dossiers'
    paginate_by = 20
    queryset = Dossier.objects.filter(is_deleted=False)
    
    def get_queryset(self):
        queryset = Dossier.objects.select_related('comptable_traitant').filter(actif=True)
        user = self.request.user


        if user.is_client():
            try:
                client_profile = user.client_profile
                queryset = queryset.filter(client=client_profile)
            except Client.DoesNotExist:
                queryset = Dossier.objects.none() # No client profile, no dossiers



        elif user.is_comptable():
            try:
                comptable_profile = user.comptable_profile
                queryset = queryset.filter(comptable_traitant=comptable_profile)

            except Comptable.DoesNotExist:
                queryset = Dossier.objects.none() # No comptable profile, no dossiers



        all_dossiers = Dossier.objects.all()
        print(f"Total dossiers in DB (Dossier.objects.all().count()): {all_dossiers.count()}")
        for dossier in all_dossiers:
            print(f"Dossier ID: {dossier.id}, Actif: {dossier.actif}")

        user_role = user.role
        print(f"User role: {user_role}")
        print(f"Initial queryset count (actif=True): {queryset.count()}")

        type_structure = self.request.GET.get('type')
        if type_structure == 'PP':  # Personne Physique
            queryset = queryset.filter(forme_juridique__in=['PP', 'EI', 'EIRL', 'EURL', 'Auto-entrepreneur'])
        elif type_structure == 'PM':  # Personne Morale
            queryset = queryset.filter(forme_juridique__in=['SARL', 'SA', 'SAS', 'SNC', 'SCS', 'SCA', 'SASU'])

        # Filtres
        search = self.request.GET.get('search')
        code = self.request.GET.get('code')
        forme_juridique = self.request.GET.get('forme_juridique')
        declaration_tva = self.request.GET.get('declaration_tva')

        # Only allow 'comptable' filter for superuser, administrateur, secretaire, manager
        if user.is_superuser or user.is_administrateur() or user.is_secretaire() or user.is_manager():
            comptable = self.request.GET.get('comptable')
            if comptable:
                queryset = queryset.filter(comptable_traitant__pk=comptable)
        if code:
            queryset = queryset.filter(code__iexact=code.strip())
        
        if search:
            queryset = queryset.filter(
                Q(denomination__icontains=search) |
                Q(abreviation__icontains=search) |
                Q(ice__icontains=search) |
                Q(rc__icontains=search)
            )


        # The 'comptable' filter was already handled above for specific roles.
        # This 'if comptable' block is redundant if the previous one is active and covers all cases.
        # I will remove this redundant check to avoid confusion and potential double filtering.
        # if comptable:
        #     queryset = queryset.filter(comptable_traitant_id=comptable)
        #     print(f"[DEBUG] Queryset after redundant comptable filter: {queryset.count()}")

        if code:
            queryset = queryset.filter(code=code)
            print(f"[DEBUG] Queryset after code filter: {queryset.count()}")
            
        if forme_juridique:
            queryset = queryset.filter(forme_juridique=forme_juridique)
            print(f"[DEBUG] Queryset after forme_juridique filter: {queryset.count()}")
            
        if declaration_tva:
            queryset = queryset.filter(declaration_tva=declaration_tva)
            print(f"[DEBUG] Queryset after declaration_tva filter: {queryset.count()}")
        
        print(f"Queryset after user role filtering: {queryset.count()}")
        print(f"Final queryset count: {queryset.count()}")
        print("Dossiers in final queryset:")
        for dossier in queryset:
            print(f"  ID: {dossier.id}, Code: {dossier.code}, Denomination: {dossier.denomination}")
        return queryset.order_by('denomination')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assign_to_comptable_pk = self.request.GET.get('assign_to_comptable')
        if assign_to_comptable_pk:
            context['assign_to_comptable_pk'] = assign_to_comptable_pk
            try:
                context['comptable_to_assign'] = Comptable.objects.get(pk=assign_to_comptable_pk)
            except Comptable.DoesNotExist:
                context['comptable_to_assign'] = None
        context['comptables'] = Comptable.objects.filter(actif=True)
        context['codes'] = Dossier.CODE_CHOICES
        context['formes_juridiques'] = Dossier.FORME_JURIDIQUE_CHOICES
        context['declarations_tva'] = Dossier.DECLARATION_TVA_CHOICES
        return context


class DossierDetailView(LoginRequiredMixin, DetailView):
    model = Dossier
    template_name = 'dossiers/detail.html'
    context_object_name = 'dossier'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_client():
            client = get_object_or_404(Client, user=user)
            queryset = queryset.filter(client=client)
        elif user.is_comptable():
            try:
                comptable_profile = user.comptable_profile
                queryset = queryset.filter(comptable_traitant=comptable_profile)
            except Comptable.DoesNotExist:
               queryset = Dossier.objects.none()
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dossier = self.get_object()
        
        # Réclamations liées au dossier
        context['reclamations'] = Reclamation.objects.filter(dossier=dossier).order_by('-date_creation')
        context['reclamation_form'] = ReclamationForm(initial={'dossier': dossier})

        # Honoraires liés au dossier
        context['honoraires'] = Honoraire.objects.filter(dossier=dossier).order_by('-date_creation')

        # Suivis fiscaux liés au dossier
        context['acomptes'] = Acompte.objects.filter(dossier=dossier).order_by('-date_creation')
        context['cmirs'] = CMIR.objects.filter(dossier=dossier).order_by('-date_creation')
        context['depots_bilan'] = DepotBilan.objects.filter(dossier=dossier).order_by('-date_creation')
        context['suivis_tva'] = SuiviTVA.objects.filter(dossier=dossier).order_by('-date_creation')
        context['suivis_forfaitaire'] = SuiviForfaitaire.objects.filter(dossier=dossier).order_by('-date_creation')

        # Documents juridiques liés au dossier
        context['documents_juridiques'] = DocumentJuridique.objects.filter(dossier=dossier).order_by('-date_document')
        context['evenements_juridiques'] = EvenementJuridique.objects.filter(dossier=dossier).order_by('-date_evenement')

        return context

from cabinet.models import Document
from cabinet.util import extract_text_from_pdf, extract_date, parse_french_date
from io import BytesIO
from cabinet.util import extract_text_from_pdf, enregistrer_suivi_tva  # Assure-toi que c’est bien importé
import tempfile
import os
from .util import extraire_periode_depuis_pdf , extraire_infos_identifiants
from fiscal.models import SuiviTVA
class DossierCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['administrateur', 'manager', 'comptable']
    model = Dossier
    template_name = 'dossiers/form.html'
    success_url = reverse_lazy('cabinet:dossier_list')

    def get_form_class(self):
        if self.request.user.is_authenticated and self.request.user.groups.filter(name='comptable').exists():
            class DossierForm(forms.ModelForm):
                class Meta:
                    model = Dossier
                    exclude = ['comptable_traitant', 'statut']
            return DossierForm
        else:
            class DossierForm(forms.ModelForm):
                class Meta:
                    model = Dossier
                    exclude = ['statut']
            return DossierForm
    
    def form_valid(self, form):
        dossier = form.save(commit=False)

        # Attribution utilisateur
        if not dossier.cree_par:
            dossier.cree_par = self.request.user

        if hasattr(self.request.user, 'comptable_profile'):
            dossier.comptable_traitant = self.request.user.comptable_profile

        # Vérification de doublon
        if Dossier.objects.filter(
            denomination=dossier.denomination,
            comptable_traitant=dossier.comptable_traitant
        ).exclude(pk=dossier.pk).exists():
            form.add_error('denomination', "Un dossier avec cette dénomination et ce comptable existe déjà.")
            return self.form_invalid(form)

        # Sauvegarder ici AVANT de créer les documents
        dossier.save()

        tva_traitee = False
        documents = self.request.FILES.getlist('documents')

        for file in documents:
            try:
                document = Document.objects.create(dossier=dossier, fichier=file)

                with document.fichier.open('rb') as f:
                    file_content = f.read()

                document.texte_extrait = extract_text_from_pdf(BytesIO(file_content))
                document.save()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(file_content)
                    tmp_path = tmp_file.name

                infos = extraire_infos_identifiants(tmp_path)

                if infos.get('if_identifiant') and not dossier.if_identifiant:
                    dossier.if_identifiant = infos['if_identifiant']
                if infos.get('ice') and not dossier.ice:
                    dossier.ice = infos['ice']
                if infos.get('tp') and not dossier.tp:
                    dossier.tp = infos['tp']
                if infos.get('rc') and not dossier.rc:
                    dossier.rc = infos['rc']
                if infos.get('cnss') and not dossier.cnss:
                    dossier.cnss = infos['cnss']

                # Extraire et parser la date AVANT form.save()
                if not dossier.date_creation:
                    date_extraite = extract_date(document.texte_extrait)
                    print(" Date extraite brute :", date_extraite)
                    date_creation = parse_french_date(str(date_extraite)) if date_extraite else None
                    print(" Date après parsing :", date_creation)
                    if date_creation:
                        dossier.date_creation = date_creation
                    else:
                        print(" Aucune date valide extraite pour le champ date_creation.")

                if not tva_traitee:
                    annee, champs = extraire_periode_depuis_pdf(tmp_path)
                    if annee and champs:
                        SuiviTVA.objects.update_or_create(
                            dossier=dossier,
                            annee=annee,
                            defaults=champs
                        )
                        tva_traitee = True

                os.remove(tmp_path)

            except Exception as e:
                print(f" Erreur traitement fichier {file.name} : {e}")

        #  Enregistrer les modifications de dossier après enrichissement
        dossier.save()
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.groups.filter(name='comptable').exists():
            context['comptables'] = Comptable.objects.filter(actif=True)
        return context

    def form_invalid(self, form):
        print("ERREURS DU FORMULAIRE :", form.errors)
        messages.error(self.request, "Échec de la création du dossier. Vérifiez les champs.")
        return super().form_invalid(form)


from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')
# La vue delete_document a été déplacée vers dossiers/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .util import extraire_infos_identifiants
import tempfile
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
@require_http_methods(["GET", "POST"])
def custom_logout(request):
    logout(request)
    return redirect('/accounts/login/')
@csrf_exempt
@require_POST
def preview_identifiants_ajax(request):
    fichiers = request.FILES.getlist('documents')  #  plusieurs fichiers supportés

    if not fichiers:
        return JsonResponse({'error': 'Aucun fichier fourni'}, status=400)

    aggregated_data = {
        'if_identifiant': '',
        'ice': '',
        'tp': '',
        'rc': '',
        'cnss': '',
        'denomination': '',
        'forme_juridique': '',
        'gerant': '',
        'cin': '',
        'adresse': '',
        'numero_certificat': '',
        'date_certificat': '',
        'date_creation':'',
        'branche': '',
        'secteur': '',
        'telephone_fixe':'',
        'telephone_mobile':'',
        'email':'',
        'tva': '',
        'telephone':''

    }

    try:
        for fichier in fichiers:
            # Vérifier le type
            if not fichier.name.lower().endswith('.pdf'):
                continue  # Ignorer les fichiers non-PDF

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                for chunk in fichier.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name

            try:
                infos = extraire_infos_identifiants(tmp_path)

                #  On garde la première valeur trouvée pour chaque champ manquant
                for key in aggregated_data:
                    if not aggregated_data[key] and infos.get(key):
                        aggregated_data[key] = infos[key]

            except Exception as e:
                print(f" Erreur extraction {fichier.name} :", e)

            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        return JsonResponse({
            **aggregated_data,
            'status': 'success'
        })

    except Exception as e:
        print(" Erreur globale :", e)
        return JsonResponse({
            'error': 'Erreur globale lors du traitement',
            'details': str(e),
            'status': 'error'
        }, status=500)


import logging

logger = logging.getLogger(__name__)
# La vue DossierUpdateView a été déplacée vers dossiers/views.py
# Les vues de gestion des dossiers ont été déplacées



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

# La vue assign_dossier_to_comptable a été déplacée vers dossiers/views.py

# Les vues DossierDeleteView et DossierTrashListView ont été déplacées
# Les vues de suppression et corbeille ont été déplacées





# La vue corbeille et restauration de dossiers ont été déplacées


# Les vues Honoraire ont été déplacées vers honoraires/views.py


class ReglementCreateView(LoginRequiredMixin, CreateView):
    model = ReglementHonoraire
    template_name = 'honoraires/reglement_form.html'
    fields = ['date_reglement', 'montant', 'type_reglement', 'mode_paiement', 'numero_piece', 'remarques']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['honoraire'] = get_object_or_404(Honoraire, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        form.instance.honoraire = get_object_or_404(Honoraire, pk=self.kwargs['pk'])
        messages.success(self.request, 'Règlement enregistré avec succès.')
        return super().form_valid(form)


# Les vues Fiscal ont été déplacées vers fiscal/views.py


# Les vues Reclamation ont été déplacées vers reclamations/views.py



    






# Les vues ReclamationCreateView et update ont été déplacées


# La vue ReclamationUpdateView a été déplacée



# Les vues ReclamationDetailView et add_suivi ont été déplacées

    
# Les vues Juridique ont été déplacées vers juridique/views.py


# Les vues ReclamationDeleteView et TrashListView ont été déplacées


# La vue ReclamationTrashListView a été déplacée


# La vue reclamation_restore a été déplacée



class RapportsView(LoginRequiredMixin, TemplateView):
    template_name = 'rapports/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques pour les rapports
        context['stats'] = {
            'total_dossiers': Dossier.objects.filter(actif=True).count(),
            'total_comptables': Comptable.objects.filter(actif=True).count(),
            'reclamations_en_cours': Reclamation.objects.filter(classement='EN_COURS').count(),
        }
        
        return context


class ExportExcelView(LoginRequiredMixin, View):
    def get(self, request, type):
        exporter = ExportExcel()
        
        if type == 'comptables':
            response = exporter.export_comptables()
        elif type == 'dossiers':
            response = exporter.export_dossiers()
        elif type == 'honoraires':
            response = exporter.export_honoraires()
        elif type == 'honoraires_pv':
            response = exporter.export_honoraires_pv()
        elif type == 'suivi_tva':
            response = exporter.export_suivi_tva()
        elif type == 'acomptes':
            response = exporter.export_acompte()
        elif type == 'cmir':
            response = exporter.export_cmir()
        elif type == 'depotbilan':
            response = exporter.export_depotbilan()
        elif type == 'suivi_forfaitaire':
            response = exporter.export_suiviforfaitaire()
        elif type == 'juridique_creation':
            response = exporter.export_juridique_creation()
        elif type == 'document_juridique':
            response = exporter.export_document_juridique()
        elif type == 'evenement_juridique':
            response = exporter.export_evenement_juridique()
        elif type == 'reclamations':
            response = exporter.export_reclamations()
        elif type == 'clients':
            response = exporter.export_clients()
        else:
            return HttpResponse('Type d\'export non supporté', status=400)
        
        return response

@login_required
def export_clients(request):
    exporter = ExportExcel()
    return exporter.export_clients
@login_required
def export_honoraires(request):
    exporter = ExportExcel()
    return exporter.export_honoraires()

@login_required
def export_honoraires_pv(request):
    exporter = ExportExcel()
    return exporter.export_honoraires_pv()

@login_required
def export_acomptes(request):
    exporter = ExportExcel()
    return exporter.export_acompte()

@login_required
def export_cmir(request):
    exporter = ExportExcel()
    return exporter.export_cmir()

@login_required
def export_depotbilan(request):
    exporter = ExportExcel()
    return exporter.export_depotbilan()

@login_required
def export_suiviforfaitaire(request):
    exporter = ExportExcel()
    return exporter.export_suiviforfaitaire()

@login_required
def export_juridique_creation(request):
    exporter = ExportExcel()
    return exporter.export_juridique_creation()

@login_required
def export_document_juridique(request):
    exporter = ExportExcel()
    return exporter.export_document_juridique()

@login_required
def export_evenement_juridique(request):
    exporter = ExportExcel()
    return exporter.export_evenement_juridique()

@login_required
def export_reclamations(request):
    exporter = ExportExcel()
    return exporter.export_reclamations()




class ExportPDFView(LoginRequiredMixin, View):
    def get(self, request, type):
        try:
            from .utils.pdf_export import ExportPDF
        except Exception as e:
            return HttpResponse(
                "Export PDF indisponible: dépendances WeasyPrint manquantes ou non chargées.",
                status=503
            )

        exporter = ExportPDF()
        if type == 'rapport-comptables':
            return exporter.export_rapport_comptables()
        elif type == 'rapport-dossiers':
            return exporter.export_rapport_dossiers()
        elif type == 'rapport-honoraires':
            return exporter.export_rapport_honoraires()
        elif type == 'suivi-tva':
            return exporter.export_suivi_tva_pdf()
        else:
            return HttpResponse("Type d'export non supporté", status=400)


class SendEmailView(LoginRequiredMixin, View):
     def post(self, request):
        try:
            data = json.loads(request.body)

            # Récupération des données du corps de la requête
            to_emails = data.get('to_emails', [])
            subject = data.get('subject', '')
            message = data.get('message', '')
            html_message = data.get('html_message', None)  # optionnel
            attachments = data.get('attachments', None)    # gérés s'ils sont passés en base64, etc.

            if not to_emails or not subject or not message:
                return JsonResponse({'status': 'error', 'message': 'Champs requis manquants'}, status=400)

            # Appel au service d'envoi
            email_service = EmailService()
            success = email_service.send_email(
                to_emails=to_emails,
                subject=subject,
                message=message,
                html_message=html_message,
                attachments=attachments
            )

            if success:
                Notification.objects.create(
                    user=request.user,
                    title="Email envoyé",
                    message=f"Email envoyé à {', '.join(to_emails)} avec le sujet : {subject}"
                )
                return JsonResponse({'status': 'success', 'message': 'Email envoyé avec succès'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Échec de l’envoi de l’email'}, status=500)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# Les vues Fiscal et Honoraires restantes ont été déplacées

# La vue client_register a été déplacée vers utilisateurs/views.py






from django.http import JsonResponse
from reclamations.tasks import send_rappel_tva_task, send_reclamation_email_task
def lancer_tache_rappel_tva(request):
    send_rappel_tva_task.delay()
    return JsonResponse({'status': 'Tâche rappel TVA lancée'})

# La vue lancer_tache_reclamation a été déplacée
