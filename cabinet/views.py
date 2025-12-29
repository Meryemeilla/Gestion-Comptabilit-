"""
Django views (gestion des requêtes HTTP).

Fichier: cabinet/views.py
"""

# ==================== Imports ====================
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django import forms
from django.db.models import ProtectedError
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.db.models import Count, Q, Sum
from django.db.models.functions import ExtractYear, ExtractMonth
from django.utils import timezone
from django.urls import reverse_lazy
from datetime import datetime, timedelta
import json
from django.http import Http404
from reclamations.forms import ReclamationSearchForm
from utilisateurs.models import Client
from django.contrib.auth.decorators import login_required
from comptables.models import Comptable
from dossiers.models import Dossier
from dossiers.services import get_stats_by_year_month, get_total_cards, get_sector_counts, get_branche_counts
from honoraires.models import Honoraire, ReglementHonoraire, HonorairePV, ReglementHonorairePV
from fiscal.models import Acompte, CMIR, DepotBilan, SuiviTVA, SuiviForfaitaire
from reclamations.models import Reclamation
from juridique.models import JuridiqueCreation, DocumentJuridique, EvenementJuridique
from .utils.export import ExportExcel
from .utils.email import EmailService
from django.contrib import messages
from django.http import HttpResponseForbidden
from utilisateurs.models import RoleRequiredMixin, Utilisateur
from django.views import View
from django.urls import reverse
from honoraires.views import HonoraireCreateView
from reclamations.forms import ReclamationForm
from django.contrib.auth.models import Group
from .forms import ComptableForm
from django.shortcuts import redirect
from cabinet.forms import ClientCreationForm, ClientRegisterForm
from django.contrib.auth.decorators import user_passes_test
from cabinet.forms import ClientUpdateForm
from django.contrib.auth.decorators import login_required
from utilisateurs.models import Utilisateur
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

@user_passes_test(est_admin)
def ajouter_client_par_admin(request):
    if request.method == 'POST':
        form = ClientCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Crée un nouvel utilisateur

            if Client.objects.filter(user=user).exists():
                messages.error(request, "Ce compte utilisateur est déjà associé à un client.")
                return redirect('cabinet:liste_clients')

            client = Client.objects.create(
                user=user,
                nom_entreprise=request.POST.get('nom_entreprise', ''),
                contact_personne=f"{user.first_name} {user.last_name}",
                email=user.email,
                telephone=user.telephone,
                adresse=request.POST.get('adresse', ''),
            )

            # Appelle explicitement la tâche Celery ici
            raw_password = form.cleaned_data.get('password1')  # Récupère le mot de passe défini dans le formulaire

            envoyer_email_creation_client.delay(
                to_email=client.email,
                password=raw_password,
                nom_client=client.nom_entreprise,
                prenom=user.first_name,
                username=user.username,
                login_url='https://gestion-comptabilite.onrender.com/accounts/login/'
            )

            messages.success(request, "Client ajouté avec succès.")
            return redirect('cabinet:liste_clients')
        else:
            print(form.errors)
    else:
        form = ClientCreationForm()

    return render(request, 'cabinet/ajouter_client_admin.html', {
        'form': form,
        'admin_creation': True,
    })



@login_required
@user_passes_test(est_admin)
def supprimer_client(request, client_id):
    print("suppression_client VUE APPELÉE")
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        print(f"Client avec ID {client_id} non trouvé.")
        raise Http404("Client non trouvé")

    print(f"Suppression demandée pour client ID: {client_id}")

    if request.method == "POST":
        try:
            client.delete()
            if client.user:
                client.user.delete()
            messages.success(request, "Le client a été supprimé avec succès.")
        except ProtectedError:
            messages.error(request, "Impossible de supprimer ce client car il est lié à d'autres données.")
        return redirect('cabinet:liste_clients')
    else:
        return redirect('cabinet:liste_clients')

@login_required
@user_passes_test(est_admin)
def detail_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    dossier = client.dossiers_client.order_by('-id').first()
    return render(request, 'cabinet/detail_clients.html', {'client': client,'dossier': dossier,}) 


from django.db.models import Q


@login_required
@user_passes_test(est_admin)
def liste_clients(request):
    search = request.GET.get('search', '')
    clients = Client.objects.all()
    
    # Debug détaillé
    print(f"[DEBUG] Nombre total de clients: {clients.count()}")
    for client in clients:
        print(f"[DEBUG] Client: {client.id} - User: {client.user.username} - Entreprise: '{client.nom_entreprise}' - Email: {client.email}")
        print(f"[DEBUG] - Nom: {client.user.first_name} - Prénom: {client.user.last_name}")
        print(f"[DEBUG] - Adresse: '{client.adresse}' - Téléphone: {client.telephone}")
        print("---")

    if search:
        clients = clients.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(email__icontains=search) |
            Q(telephone__icontains=search)
        )
        print(f"[DEBUG] Après recherche '{search}': {clients.count()} clients")

    return render(request, 'cabinet/liste_clients.html', {
        'clients': clients,
    })

@user_passes_test(est_admin)
def modifier_client_par_admin(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    user = client.user

    if request.method == 'POST':
        form = ClientUpdateForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save()

            # Mise à jour des données du modèle Client
            client.nom_entreprise = request.POST.get('nom_entreprise', client.nom_entreprise)
            client.contact_personne = f"{user.first_name} {user.last_name}"
            client.email = user.email
            client.telephone = user.telephone
            client.adresse = request.POST.get('adresse', client.adresse)
            client.save()

            messages.success(request, "Client modifié avec succès.")
            return redirect('cabinet:liste_clients')
        else:
            print(form.errors)
    else:
        initial_data = {
            'nom_entreprise': client.nom_entreprise,
            'adresse': client.adresse,
        }
        form = ClientUpdateForm(instance=user, initial=initial_data)

    return render(request, 'cabinet/ajouter_client_admin.html', {
        'form': form,
        'client': client,
        'modification': True,
    })




from utilisateurs.models import Client



from django.db.models import Count, Q

class ComptableListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['administrateur', 'manager']
    model = Comptable
    template_name = 'comptables/list.html'
    context_object_name = 'comptables'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_comptable():
            return redirect('cabinet:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Comptable.objects.filter(actif=True)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(prenom__icontains=search) |
                Q(matricule__icontains=search) |
                Q(email__icontains=search)
            )

        queryset = queryset.annotate(
            nbre_pm_count=Count(
                'dossiers',
                filter=Q(dossiers__forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'SASU', 'SAS'])
            ),
            nbre_et_count=Count(
                'dossiers',
                filter=Q(dossiers__forme_juridique__in=['EI', 'EIRL', 'EURL', 'AUTO'])
            )
        )

        return queryset.order_by('nom', 'prenom')



class ComptableDetailView(RoleRequiredMixin, LoginRequiredMixin, DetailView):
    allowed_roles = ['administrateur', 'manager']
    model = Comptable
    template_name = 'comptables/detail.html'
    context_object_name = 'comptable'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user

        if user.is_comptable() and obj.user != user:
            # If the user is an accountant, they can only view their own details
            raise Http404("Vous n'êtes pas autorisé à voir ce détail de comptable.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comptable = self.get_object()

        # Tous les dossiers du comptable (qu'ils soient actifs ou non)
        all_dossiers = comptable.dossiers.all()

        # Seulement les dossiers actifs
        actifs = all_dossiers.filter(actif=True)

        context['dossiers'] = all_dossiers

        # Statistiques sur les dossiers actifs uniquement
        context['stats'] = {
            'total_dossiers': all_dossiers.count(),  # Total réel
            'dossiers_actifs': actifs.count(),       # Total actif
            'dossiers_pm': actifs.filter(forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'EURL', 'SASU', 'SAS']).count(),
            'dossiers_pp': actifs.filter(forme_juridique__in=['EI', 'EIRL', 'AUTO']).count(),
            'dossiers_forfaitaires': actifs.filter(code__in=['F', 'FS']).count(),
            'dossiers_avec_tva': actifs.filter(declaration_tva__in=['MENSUELLE', 'TRIMESTRIELLE']).count(),
            'dossiers_tva_mensuelle': actifs.filter(declaration_tva='MENSUELLE').count(),
            'dossiers_tva_trimestrielle': actifs.filter(declaration_tva='TRIMESTRIELLE').count(),
            'total_dossiers_pm': all_dossiers.filter(forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'EURL', 'SASU', 'SAS']).count(),
            'total_dossiers_pp': all_dossiers.filter(forme_juridique__in=['EI', 'EIRL', 'AUTO']).count(),
        }

        context['comptable'] = comptable

        return context

from utilisateurs.tasks import envoyer_email_creation_comptable

class AdminDossierStatsView(RoleRequiredMixin, LoginRequiredMixin, TemplateView):
    allowed_roles = ['administrateur']
    template_name = 'cabinet/admin_dossier_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistiques par année et par mois via service
        stats_data = get_stats_by_year_month()

        # Convertir les mois numériques en noms de mois pour l'affichage
        month_names = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
            7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
        for stat in stats_data:
            stat['month'] = month_names.get(stat['month'], stat['month'])

        context['stats'] = list(stats_data)

        # Totaux des cartes via service
        cards = get_total_cards()
        context.update({
            'total_dossiers': cards.get('total_dossiers', 0),
            'total_pp': cards.get('total_pp', 0),
            'total_pm': cards.get('total_pm', 0),
            'tva_mensuelle': cards.get('tva_mensuelle', 0),
            'tva_trimestrielle': cards.get('tva_trimestrielle', 0),
            'tva_exoneree': cards.get('tva_exoneree', 0),
            'total_radie': cards.get('total_radie', 0),
            'total_livre': cards.get('total_livre', 0),
            'total_delaisse': cards.get('total_delaisse', 0),
        })

        # Statistiques par secteur et par branche via services
        context['stats_par_secteur'] = list(get_sector_counts())
        context['stats_par_branche'] = list(get_branche_counts())

        return context


class ComptableCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['administrateur', 'manager']
    model = Comptable
    form_class = ComptableForm
    template_name = 'comptables/form.html'
    success_url = reverse_lazy('cabinet:comptable_list')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']

        try:
            user = Utilisateur.objects.create_user(username=username, email=email, password=password)
            user.first_name = form.cleaned_data['prenom']
            user.role = 'comptable'
            user.save()
            comptable = form.save(commit=False)
            comptable.user = user
            comptable.is_approved = True  # Automatically approve the accountant
            comptable.save()

            # Add user to 'Comptables' group
            comptable_group, created = Group.objects.get_or_create(name='Comptables')
            user.groups.add(comptable_group)

            envoyer_email_creation_comptable.delay(
                user_id=user.id,
                password_plain=password  # Le mot de passe saisi par l'admin
            )

            messages.success(self.request, 'Comptable créé avec succès et compte utilisateur associé.')
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Erreur lors de la création du comptable: {e}')
            return self.form_invalid(form)


class ComptableUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    allowed_roles = ['administrateur', 'manager']
    model = Comptable
    form_class = ComptableForm
    template_name = 'comptables/form.html'
    success_url = reverse_lazy('cabinet:comptable_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object.user:
            kwargs['initial'] = {
                'username': self.object.user.username,
                'email': self.object.user.email,
            }
        return kwargs

    def form_valid(self, form):
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data.get('password')

        comptable = form.save(commit=False)
        user = comptable.user

        if user:
            user.username = username
            user.email = email
            if password:
                user.set_password(password)
            user.save()
        else:
            # This case should ideally not happen if a Comptable always has a user
            # but as a fallback, create a user if somehow missing
            user = Utilisateur.objects.create_user(username=username, email=email, password=password)
            comptable.user = user

        comptable.is_approved = True  # Ensure approval on update as well
        comptable.save()

        messages.success(self.request, 'Comptable modifié avec succès.')
        return super().form_valid(form)


class ComptableDeleteView(RoleRequiredMixin, LoginRequiredMixin, DeleteView):
    allowed_roles = ['administrateur', 'manager']
    model = Comptable
    template_name = 'comptables/confirm_delete.html'
    success_url = reverse_lazy('cabinet:comptable_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Comptable supprimé avec succès.')
        return super().delete(request, *args, **kwargs)
        comptable = self.get_object()
        user = comptable.user
        if user:
            user.delete()
        messages.success(request, 'Comptable et utilisateur associé supprimés avec succès.')
        return super().delete(request, *args, **kwargs)

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
def delete_document(request, pk):
    try:
        document = get_object_or_404(Document, pk=pk)
        dossier_id = document.dossier.id  # Adaptez selon votre modèle
        document.delete()
        messages.success(request, "Document supprimé avec succès.")
        return redirect('cabinet:dossier_edit', pk=dossier_id)
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
        return redirect('cabinet:dossier_list')
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


from .forms import ClientDossierForm, ComptableDossierForm, BaseDossierForm
import logging

logger = logging.getLogger(__name__)
class DossierUpdateView(LoginRequiredMixin, UpdateView):
    model = Dossier
    template_name = 'dossiers/form.html'
    success_url = reverse_lazy('cabinet:dossier_list')

    def get_form_class(self):
        if self.request.user.is_client():
            return ClientDossierForm
        elif self.request.user.is_comptable():
            return ComptableDossierForm
        return BaseDossierForm


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comptables'] = Comptable.objects.filter(actif=True)
        return context

    def post(self, request, *args, **kwargs):
        print("POST request reçu")
        print("Données POST:", request.POST)
        print("Fichiers reçus:", request.FILES)

        self.object = self.get_object()  #  nécessaire !

        form = self.get_form()
        

        if form.is_valid():
            return self.form_valid(form)
        else:
            print(form.errors)
            return self.form_invalid(form)
            

        

    def form_valid(self, form):
        # Sauvegarde initiale en préservant le créateur original
        if not form.instance.pk:  # Si c'est une création
            form.instance.cree_par = self.request.user
        else:  # Si c'est une modification
            original_dossier = Dossier.objects.get(pk=form.instance.pk)
            form.instance.cree_par = original_dossier.cree_par
        
        response = super().form_valid(form)
        
        try:
            # Traitement des documents à supprimer
            delete_documents = self.request.POST.get('delete_documents', '')
            if delete_documents:
                document_ids = [int(id) for id in delete_documents.split(',') if id.isdigit()]
                Document.objects.filter(
                    pk__in=document_ids,
                    dossier=self.object
                ).delete()
            
            # Traitement des nouveaux documents
            for uploaded_file in self.request.FILES.getlist('documents'):
                try:
                    document_data = {
                        'dossier': self.object,
                        'fichier': uploaded_file
                    }
                    
                    if hasattr(Document, 'cree_par'):
                        document_data['cree_par'] = self.request.user
                    
                    document = Document.objects.create(**document_data)
                    
                    if uploaded_file.name.lower().endswith('.pdf'):
                        extracted_text = extract_text_from_pdf(document.fichier)
                        document.texte_extrait = extracted_text
                        document.save()
                        enregistrer_suivi_tva(self.object, extracted_text)
                        
                except Exception as e:
                    print(f"Erreur traitement du fichier {uploaded_file.name}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Erreur globale dans form_valid: {str(e)}")
            # Vous pourriez aussi logger l'erreur pour le suivi
            # logger.error(f"Erreur dans DossierUpdateView: {str(e)}")

        return response


    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            }, status=400)
        return response

    def get_success_url(self):
        return reverse('cabinet:dossier_detail', kwargs={'pk': self.object.pk})

        
        

        




from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def assign_dossier_to_comptable(request, comptable_pk, dossier_pk):
    comptable = get_object_or_404(Comptable, pk=comptable_pk)
    dossier = get_object_or_404(Dossier, pk=dossier_pk)

    if request.method == 'GET': # Or 'POST' depending on how you want to handle the assignment
        dossier.comptable_traitant = comptable
        dossier.save()
        messages.success(request, f"Le dossier {dossier.denomination} a été assigné à {comptable.nom_complet}.")
    return redirect('cabinet:comptable_detail', pk=comptable_pk)

class DossierDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Dossier
    template_name = 'dossiers/delete.html'
    success_url = reverse_lazy('cabinet:dossier_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_deleted = True
        self.object.save()
        messages.success(request, "Le dossier a été déplacé vers la corbeille.")
        return HttpResponseRedirect(self.get_success_url())

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff





class DossierTrashListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Dossier
    template_name = 'dossiers/trash_list.html'
    context_object_name = 'dossiers'
    paginate_by = 10

    def get_queryset(self):
        queryset = Dossier.objects.filter(is_deleted=True)
        
        if self.request.user.is_comptable():
            try:
                comptable_profile = self.request.user.comptable_profile
                queryset = queryset.filter(comptable_traitant=comptable_profile)
            except Comptable.DoesNotExist:
                queryset = Dossier.objects.none()
        elif self.request.user.is_client():
            queryset = queryset.filter(client=self.request.user.client_profile)
        
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(denomination__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(abreviation__icontains=search_query) |
                Q(ice__icontains=search_query) |
                Q(rc__icontains=search_query)
            )
        return queryset

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff or self.request.user.is_comptable() or self.request.user.is_client()

@login_required
def dossier_restore(request, pk):
    dossier = get_object_or_404(Dossier, pk=pk, is_deleted=True)
    if request.method == 'POST':
        dossier.is_deleted = False
        dossier.save()
        messages.success(request, "Le dossier a été restauré avec succès.")
        return redirect('cabinet:dossier_trash_list')
    return redirect('cabinet:dossier_trash_list')


class HonoraireCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['comptable', 'administrateur']
    model = Honoraire
    template_name = 'honoraires/honoraire_form.html'
    fields = ['dossier', 'montant_mensuel', 'montant_trimestriel', 'montant_annuel']
    success_url = reverse_lazy('cabinet:honoraire_list')

    def form_valid(self, form):
        messages.success(self.request, "Honoraire créé avec succès.")
        return super().form_valid(form)

    def form_invalid(self, form):
        print(" Formulaire invalide :", form.errors)
        messages.error(self.request, "Erreur lors de la création de l'honoraire.")
        return super().form_invalid(form)







class HonoraireUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    allowed_roles = ['comptable', 'administrateur']
    model = Honoraire
    template_name = 'honoraires/honoraire_form.html'

    fields = ['dossier', 'montant_mensuel', 'montant_trimestriel', 'montant_annuel']
    success_url = reverse_lazy('cabinet:honoraire_list')

    def form_valid(self, form):
        messages.success(self.request, "Honoraire modifié avec succès.")
        return super().form_valid(form)


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


class SuiviTVAListView(LoginRequiredMixin, ListView):
    model = SuiviTVA
    template_name = 'fiscal/list.html'
    context_object_name = 'suivis'
    paginate_by = 20
    
    def get_queryset(self):
        code= self.request.GET.get('code')
        annee = self.request.GET.get('annee')
        queryset = SuiviTVA.objects.select_related('dossier').all()
        if annee and annee.isdigit():
            queryset = queryset.filter(annee=annee)
        type_selected = self.request.GET.get('type')
        if type_selected:
            queryset = queryset.filter(dossier__declaration_tva=type_selected)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['annee_courante'] = timezone.now().year
        context['annees'] = range(2020, timezone.now().year + 2)
        return context


class SuiviTVADetailView(LoginRequiredMixin, DetailView):
    model = SuiviTVA
    template_name = 'fiscal/detail.html'
    context_object_name = 'suivi'


class SuiviTVAUpdateView(LoginRequiredMixin, UpdateView):
    model = SuiviTVA
    template_name = 'fiscal/form.html'
    fields = ['jan', 'fev', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout', 'sep', 'oct', 'nov', 'dec', 't1', 't2', 't3', 't4']
    
    def form_valid(self, form):
        messages.success(self.request, 'Suivi TVA mis à jour avec succès.')
        return super().form_valid(form)


class SuiviTVACreateView(LoginRequiredMixin, CreateView):
    model = SuiviTVA
    template_name = 'fiscal/form.html'
    fields = ['dossier', 'annee', 'jan', 'fev', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout', 'sep', 'oct', 'nov', 'dec', 't1', 't2', 't3', 't4']
    success_url = reverse_lazy('cabinet:suivi_tva_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = None
        context['form_type'] = 'tva'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Suivi TVA créé avec succès.')
        return super().form_valid(form)


from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

class SuiviForfaitaireCreateView(LoginRequiredMixin, CreateView):
    model = SuiviForfaitaire
    template_name = 'fiscal/form.html'
    fields = [
        'code',
        'dossier',
        'annee',
        'pp',
        'declaration_annuelle',
        'paiement_annuel',
        'acompte_1',
        'acompte_2',
        'acompte_3',
        'acompte_4',
        'reclamation_code',
        'type_reclamation',
        'date_reception'
    ]
    success_url = reverse_lazy('cabinet:suivi_tva_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Configuration des champs optionnels
        form.fields['reclamation_code'].required = False
        form.fields['type_reclamation'].required = False
        form.fields['date_reception'].required = False
        
        # Ajout de classes CSS et placeholders
        form.fields['declaration_annuelle'].widget.attrs.update({
            'class': 'montant-input',
            'placeholder': '0.00 €'
        })
        for field in ['acompte_1', 'acompte_2', 'acompte_3', 'acompte_4']:
            form.fields[field].widget.attrs.update({
                'class': 'acompte-input',
                'placeholder': '0.00 €'
            })
        
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(
            self.request,
            f"Suivi forfaitaire {form.instance.annee} créé avec succès pour le dossier {form.instance.dossier}."
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Créer un nouveau suivi forfaitaire',
            'form_type': 'forfaitaire',
            'submit_text': 'Enregistrer',
            'cancel_url': self.success_url,
            'help_text': {
                'code': 'Code identifiant le forfaitaire',
                'pp': 'Référence administrative',
                'declaration_annuelle': 'Montant annuel déclaré'
            }
        })
        return context


class ReclamationListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['client', 'comptable', 'manager', 'administrateur']
    model = Reclamation
    template_name = 'reclamations/list.html'
    context_object_name = 'reclamations'

    def get_queryset(self):
        user = self.request.user
        queryset = Reclamation.objects.filter(is_deleted=False)

        if user.is_superuser or user.role == 'administrateur':
            pass  # Superusers and admins see all non-deleted reclamations
        elif user.role == 'comptable':
            queryset = queryset.filter(Q(dossier__comptable=user) | Q(created_by=user) | Q(destinataire=user))
        elif user.role == 'client':
            client = getattr(user, 'client_profile', None)
            if client:
                queryset = queryset.filter(dossier__client=client)
            else:
                queryset = Reclamation.objects.none()
        elif user.role == 'manager':
            pass  # Managers see all non-deleted reclamations
        else:
            queryset = Reclamation.objects.none()

        filtre = self.request.GET.get('filter')
        if filtre == 'envoyees':
            queryset = queryset.filter(created_by=user)
        elif filtre == 'recues':
            queryset = queryset.filter(destinataire=user)

        # Filtres supplémentaires
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(dossier__denomination__icontains=search)
            )

        classement = self.request.GET.get('classement')
        if classement:
            queryset = queryset.filter(classement=classement)

        return queryset.order_by('-date_creation')



    






class ReclamationCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['client', 'comptable', 'administrateur', 'manager']
    model = Reclamation
    template_name = 'reclamations/form.html'
    form_class = ReclamationForm
    success_url = reverse_lazy('cabinet:reclamation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user

        # Si tu veux vraiment déboguer les champs sans risque
        form_class = self.get_form_class()
        dummy_form = form_class(**kwargs)
        print('DEBUG champs du formulaire:', list(dummy_form.fields.keys()))

        return kwargs

    def form_valid(self, form):
        user = self.request.user
        form.instance.created_by = user

        dossier = form.cleaned_data['dossier']

        if user.role == 'client':
            # Destinataire = utilisateur lié au comptable_traitant du dossier
            form.instance.destinataire = dossier.comptable_traitant.user

        elif user.role == 'comptable':
            # Destinataire = utilisateur lié au client du dossier
            form.instance.destinataire = dossier.client.user

        if form.instance.destinataire is None:
            messages.error(self.request, "Impossible de déterminer le destinataire automatiquement.")
            return self.form_invalid(form)

        return super().form_valid(form)


    def get_success_url(self):
        return reverse('cabinet:reclamation_list')


class ReclamationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reclamation
    template_name = 'reclamations/form.html'
    fields = ['dossier', 'type_reclamation', 'date_reception', 'reponse', 'suivi', 'remarque', 'classement', 'priorite']
    success_url = reverse_lazy('cabinet:reclamation_list')

    def form_valid(self, form):
        messages.success(self.request, "Réclamation modifiée avec succès.")
        return super().form_valid(form)

    def test_func(self):
        reclamation = self.get_object()
        return self.request.user == reclamation.created_by

    def dispatch(self, request, *args, **kwargs):
        reclamation = self.get_object()

        # Ne pas autoriser la modification/suppression si créée par un administrateur
        if reclamation.created_by.role == 'administrateur':
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)



class ReclamationDetailView(LoginRequiredMixin, DetailView):
    model = Reclamation
    template_name = 'reclamations/detail.html'
    context_object_name = 'reclamation'

def reclamation_add_suivi(request, pk):
        reclamation = get_object_or_404(Reclamation, pk=pk)
        if request.method == 'POST':
            type_suivi = request.POST.get('type')
            commentaire = request.POST.get('commentaire')
            piece_jointe = request.FILES.get('piece_jointe')
            if type_suivi and commentaire:
                Suivi.objects.create(
                    reclamation=reclamation,
                    type=type_suivi,
                    commentaire=commentaire,
                    piece_jointe=piece_jointe
                )
                messages.success(request, "Suivi ajouté avec succès.")
                return redirect('cabinet:reclamation_detail', pk=reclamation.pk)

    
class JuridiqueListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['administrateur', 'manager', 'comptable']
    model = JuridiqueCreation
    template_name = 'juridique/list.html'
    context_object_name = 'juridiques'
    paginate_by = 20


class JuridiqueDetailView(RoleRequiredMixin, LoginRequiredMixin, DetailView):
    allowed_roles = ['administrateur', 'manager', 'comptable']
    model = JuridiqueCreation
    template_name = 'juridique/detail.html'
    context_object_name = 'juridique'


class JuridiqueCreateView(LoginRequiredMixin, CreateView):
    model = JuridiqueCreation
    template_name = 'juridique/form.html'
    fields = [
        'dossier', 'ordre', 'forme', 'certificat_negatif', 'date_certificat_negatif',
        'statuts', 'date_statuts', 'contrat_bail', 'date_contrat_bail',
        'tp', 'date_tp', 'rc', 'date_rc', 'numero_rc',
        'cnss', 'date_cnss', 'numero_cnss', 'al', 'date_al',
        'bo', 'date_bo', 'rq', 'date_rq', 'statut_global', 'remarques'
    ]

    paginate_by = 20

    def get_initial(self):
        initial = super().get_initial()
        dossier_id = self.kwargs.get('dossier_id')

        if not dossier_id:
            return initial

        dossier = get_object_or_404(Dossier, pk=dossier_id)
        initial['dossier'] = dossier

        for doc in dossier.document_set.all():
            nom = doc.fichier.name.lower()
            texte = extract_text_from_pdf(doc.fichier)

            if 'statut' in nom:
                initial['date_statuts'] = extract_date(texte)
                initial['statuts'] = True
            elif 'bail' in nom or 'contrat' in nom:
                initial['date_contrat_bail'] = extract_date(texte)
                initial['contrat_bail'] = True
            elif 'rc' in nom:
                initial['date_rc'] = extract_date(texte)
                initial['numero_rc'] = extract_rc_number(texte)
                initial['rc'] = True
            elif 'cnss' in nom:
                initial['date_cnss'] = extract_date(texte)
                initial['numero_cnss'] = extract_cnss_number(texte)
                initial['cnss'] = True
            elif 'tp' in nom:
                initial['date_tp'] = extract_date(texte)
                initial['tp'] = True
            elif 'bo' in nom:
                initial['date_bo'] = extract_date(texte)
                initial['bo'] = True
            elif 'al' in nom:
                initial['date_al'] = extract_date(texte)
                initial['al'] = True
            elif 'rq' in nom:
                initial['date_rq'] = extract_date(texte)
                initial['rq'] = True
            elif 'certificat' in nom:
                initial['date_certificat_negatif'] = extract_date(texte)
                initial['certificat_negatif'] = True

        return initial

    def form_valid(self, form):
        messages.success(self.request, 'Document juridique créé avec succès.')
        return super().form_valid(form)
    
    def get_queryset(self):
        queryset = Reclamation.objects.select_related('dossier').all()
        
        classement = self.request.GET.get('classement')
        priorite = self.request.GET.get('priorite')
        
        if classement:
            queryset = queryset.filter(classement=classement)
        
        if priorite:
            queryset = queryset.filter(priorite=priorite)
        
        return queryset.order_by('-date_reception')


class ReclamationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reclamation
    template_name = "reclamations/confirm_delete.html"
    success_url = reverse_lazy("cabinet:reclamation_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()  # Call the custom delete method for soft deletion
        messages.success(request, 'Réclamation supprimée avec succès.')
        return HttpResponseRedirect(self.get_success_url())
    
    def dispatch(self, request, *args, **kwargs):
        reclamation = self.get_object()

        # Ne pas autoriser la modificatio)/suppression si créée par un administrateur


class ReclamationTrashListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['superuser', 'administrateur', 'comptable', 'client']
    model = Reclamation
    template_name = 'reclamations/list.html'
    context_object_name = 'reclamations'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Reclamation.objects.filter(is_deleted=True)
        elif user.role == 'administrateur':
            return Reclamation.objects.filter(is_deleted=True)
        elif user.role == 'comptable':
            return Reclamation.objects.filter(is_deleted=True)
        elif user.role == 'client':
            return Reclamation.objects.filter(client=user.client, is_deleted=True)
        return Reclamation.objects.none()


@login_required
def reclamation_restore(request, pk):
    reclamation = get_object_or_404(Reclamation, pk=pk, is_deleted=True)
    reclamation.restore()
    messages.success(request, 'Réclamation restaurée avec succès.')
    return redirect('cabinet:reclamation_trash_list')



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


class FiscalDocumentRedirectView(View):
    def post(self, request, *args, **kwargs):
        type_doc = request.POST.get('type_doc')
        if type_doc == 'acomptes':
            return redirect('cabinet:acompte_create')
        elif type_doc == 'cmir':
            return redirect('cabinet:cmir_create')
        elif type_doc == 'depotbilan':
            return redirect('cabinet:depotbilan_create')
        elif type_doc == 'tva':
            return redirect('cabinet:fiscal_create')
        else:
            messages.error(request, "Type de document inconnu.")
            return redirect(request.META.get('HTTP_REFERER', 'cabinet:suivi_tva_list'))


class AcompteCreateView(LoginRequiredMixin, CreateView):
    model = Acompte
    template_name = 'fiscal/form.html'
    fields = ['dossier', 'annee', 'montant', 'regularisation', 'a1', 'a2', 'a3', 'a4', 'is_montant']
    success_url = reverse_lazy('cabinet:suivi_tva_list')

    def form_valid(self, form):
        messages.success(self.request, 'Acompte créé avec succès.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = None
        context['form_type'] = 'acompte'
        return context


class CMIRCreateView(LoginRequiredMixin, CreateView):
    model = CMIR
    template_name = 'fiscal/form.html'
    fields = ['dossier', 'annee', 'montant_ir', 'montant_cm', 'complement_ir']
    success_url = reverse_lazy('cabinet:suivi_tva_list')

    def form_valid(self, form):
        messages.success(self.request, 'CM et IR créé avec succès.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = None
        context['form_type'] = 'cmir'
        return context


class DepotBilanCreateView(LoginRequiredMixin, CreateView):
    model = DepotBilan
    template_name = 'fiscal/form.html'
    fields = ['dossier', 'annee_exercice', 'date_depot', 'remarque', 'statut']
    success_url = reverse_lazy('cabinet:suivi_tva_list')

    def form_valid(self, form):
        messages.success(self.request, 'Dépôt de bilan créé avec succès.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = None
        context['form_type'] = 'depotbilan'
        return context


class HonoraireDeleteView(RoleRequiredMixin, LoginRequiredMixin, DeleteView):
    allowed_roles = ['comptable']
    model = Honoraire
    template_name = 'honoraires/confirm_delete.html'
    success_url = reverse_lazy('cabinet:honoraire_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Honoraire supprimé avec succès.')
        return super().delete(request, *args, **kwargs)

def client_register(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Compte client créé avec succès.")
            return redirect('cabinet:dashboard')
    else:
        form = ClientRegisterForm()

    return render(request, 'registration/client_register.html', {'form': form})






from django.http import JsonResponse
from reclamations.tasks import send_rappel_tva_task, send_reclamation_email_task
def lancer_tache_rappel_tva(request):
    send_rappel_tva_task.delay()
    return JsonResponse({'status': 'Tâche rappel TVA lancée'})

def lancer_tache_reclamation(request, reclamation_id):
    send_reclamation_email_task.delay(reclamation_id)
    return JsonResponse({'status': f'Tâche reclamation {reclamation_id} lancée'})
