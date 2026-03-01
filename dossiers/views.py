"""
Django views (gestion des requêtes HTTP).

Fichier: dossiers/views.py
"""

# ==================== Imports ====================
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.utils import timezone
from io import BytesIO
import tempfile
import os

from utilisateurs.models import RoleRequiredMixin, Client, Utilisateur
from comptables.models import Comptable
from honoraires.models import Honoraire
from reclamations.models import Reclamation
from reclamations.forms import ReclamationForm
from fiscal.models import Acompte, CMIR, DepotBilan, SuiviForfaitaire, SuiviTVA
from cabinet.models import Document
from cabinet.util import (
    extract_text_from_pdf, extract_date, parse_french_date, 
    extraire_periode_depuis_pdf, extraire_infos_identifiants,
    enregistrer_suivi_tva
)
from .services import get_stats_by_year_month, get_total_cards, get_sector_counts, get_branche_counts
from .models import Dossier
from .forms import DossierForm, BaseDossierForm, ClientDossierForm, ComptableDossierForm






# def dossier_create(request):
#     if request.method == 'POST':
#         form = DossierForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('cabinet:dossier_list')
#     else:
#         form = DossierForm()
#     return render(request, 'dossiers/form.html', {'form': form})



from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect

# ==================== Handlers ====================
def trashed_dossiers(request):
    dossiers = Dossier.all_objects.filter(is_deleted=True)

    if request.user.is_authenticated:
        if request.user.is_client():
            dossiers = dossiers.filter(client=request.user)
        elif request.user.is_comptable():
            try:
                comptable_profile = request.user.comptable_profile
                dossiers = dossiers.filter(comptable_traitant=comptable_profile)
            except Comptable.DoesNotExist:
                dossiers = Dossier.all_objects.none()
        # No need for an else here, as dossiers is already initialized with all non-deleted objects

    # 🔍 Recherche
    search = request.GET.get('search')
    if search:
        dossiers = dossiers.filter(
            Q(denomination__icontains=search) |
            Q(code__icontains=search) |
            Q(abreviation__icontains=search) |
            Q(ice__icontains=search) |
            Q(rc__icontains=search)
        )

    #  PAGINATION : 10 dossiers par page
    paginator = Paginator(dossiers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,  # Pour utiliser dans le template
        'search': search,
        'trashed_view': True, # Indicate that this is the trashed view
    }
    return render(request, 'dossiers/list.html', context)

# ==================== Dossier Management ====================

class DossierListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['administrateur', 'manager', 'comptable', 'client']
    model = Dossier
    template_name = 'dossiers/list.html'
    context_object_name = 'dossiers'
    paginate_by = 20

    def get_queryset(self):
        queryset = Dossier.objects.select_related('comptable_traitant').filter(actif=True, is_deleted=False)
        user = self.request.user

        if user.is_client():
            try:
                queryset = queryset.filter(client=user.client_profile)
            except Exception:
                queryset = Dossier.objects.none()
        elif user.is_comptable():
            try:
                queryset = queryset.filter(comptable_traitant=user.comptable_profile)
            except Exception:
                queryset = Dossier.objects.none()

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(denomination__icontains=search) |
                Q(abreviation__icontains=search) |
                Q(ice__icontains=search) |
                Q(rc__icontains=search)
            )

        forme_juridique = self.request.GET.get('forme_juridique')
        if forme_juridique:
            queryset = queryset.filter(forme_juridique=forme_juridique)

        declaration_tva = self.request.GET.get('declaration_tva')
        if declaration_tva:
            queryset = queryset.filter(declaration_tva=declaration_tva)

        return queryset.order_by('denomination')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['codes'] = Dossier.CODE_CHOICES
        context['formes_juridiques'] = Dossier.FORME_JURIDIQUE_CHOICES
        context['declarations_tva'] = Dossier.DECLARATION_TVA_CHOICES
        context['comptables'] = Comptable.objects.filter(actif=True)
        return context

class DossierDetailView(LoginRequiredMixin, DetailView):
    model = Dossier
    template_name = 'dossiers/detail.html'
    context_object_name = 'dossier'

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_deleted=False)
        user = self.request.user
        if user.is_client():
            queryset = queryset.filter(client=user.client_profile)
        elif user.is_comptable():
            queryset = queryset.filter(comptable_traitant=user.comptable_profile)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dossier = self.get_object()
        context['reclamations'] = Reclamation.objects.filter(dossier=dossier).order_by('-date_creation')
        context['reclamation_form'] = ReclamationForm(initial={'dossier': dossier})
        context['honoraires'] = Honoraire.objects.filter(dossier=dossier).order_by('-date_creation')
        context['acomptes'] = Acompte.objects.filter(dossier=dossier).order_by('-date_creation')
        context['suivis_tva'] = SuiviTVA.objects.filter(dossier=dossier).order_by('-date_creation')
        from juridique.models import DocumentJuridique, EvenementJuridique
        context['documents_juridiques'] = DocumentJuridique.objects.filter(dossier=dossier).order_by('-date_document')
        context['evenements_juridiques'] = EvenementJuridique.objects.filter(dossier=dossier).order_by('-date_evenement')
        return context

class DossierCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['administrateur', 'manager', 'comptable']
    model = Dossier
    form_class = DossierForm
    template_name = 'dossiers/form.html'
    success_url = reverse_lazy('dossiers:dossier_list')

    def form_valid(self, form):
        dossier = form.save(commit=False)
        dossier.cree_par = self.request.user
        if hasattr(self.request.user, 'comptable_profile'):
            dossier.comptable_traitant = self.request.user.comptable_profile
        
        dossier.save()
        
        # Handle file uploads
        files = self.request.FILES.getlist('documents')
        for f in files:
            doc = Document.objects.create(dossier=dossier, fichier=f)
            try:
                text = extract_text_from_pdf(doc.fichier)
                doc.texte_extrait = text
                doc.save()
            except Exception as e:
                print(f"Error extracting text from {f.name}: {e}")
                
        messages.success(self.request, "Dossier créé avec succès.")
        return super().form_valid(form)

class DossierUpdateView(LoginRequiredMixin, UpdateView):
    model = Dossier
    template_name = 'dossiers/form.html'
    
    def get_form_class(self):
        user = self.request.user
        if user.is_client():
            return ClientDossierForm
        elif user.is_comptable():
            return ComptableDossierForm
        return BaseDossierForm

    def get_success_url(self):
        return reverse('dossiers:dossier_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Dossier mis à jour avec succès.")
        return super().form_valid(form)

class DossierDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Dossier
    template_name = 'dossiers/delete.html'
    success_url = reverse_lazy('dossiers:dossier_list')

    def test_func(self):
        return self.request.user.role in ['administrateur', 'manager']

    def post(self, request, *args, **kwargs):
        dossier = self.get_object()
        dossier.is_deleted = True
        dossier.save()
        messages.success(request, "Dossier déplacé vers la corbeille.")
        return redirect(self.success_url)

class AdminDossierStatsView(RoleRequiredMixin, LoginRequiredMixin, TemplateView):
    allowed_roles = ['administrateur']
    template_name = 'cabinet/admin_dossier_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats_data = get_stats_by_year_month()
        month_names = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
            7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
        for stat in stats_data:
            stat['month'] = month_names.get(stat['month'], stat['month'])
        
        context['stats'] = list(stats_data)
        cards = get_total_cards()
        context.update(cards)
        context['stats_par_secteur'] = list(get_sector_counts())
        context['stats_par_branche'] = list(get_branche_counts())
        return context

# ==================== Utilities ====================

def delete_document(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    dossier_pk = doc.dossier.pk
    doc.delete()
    messages.success(request, "Document supprimé.")
    return redirect('dossiers:dossier_edit', pk=dossier_pk)

def assign_dossier_to_comptable(request, comptable_pk, dossier_pk):
    comptable = get_object_or_404(Comptable, pk=comptable_pk)
    dossier = get_object_or_404(Dossier, pk=dossier_pk)
    dossier.comptable_traitant = comptable
    dossier.save()
    messages.success(request, f"Dossier {dossier.denomination} assigné à {comptable.nom_complet}.")
    return redirect('comptables:comptable_detail', pk=comptable_pk)

def restore_dossier(request, pk):
    dossier = get_object_or_404(Dossier.all_objects, pk=pk)
    dossier.is_deleted = False
    dossier.save()
    messages.success(request, "Dossier restauré.")
    return redirect('dossiers:dossier_list')

