"""
Django views (gestion des requêtes HTTP).

Fichier: fiscal/views.py
"""

# ==================== Imports ====================
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import SuiviTVA, Acompte, CMIR, DepotBilan, SuiviForfaitaire
from django.db.models import Q
from .forms import AcompteForm
from cabinet.views import RoleRequiredMixin
from decimal import Decimal
from cabinet.models import Dossier
from django.http import JsonResponse
from .models import SuiviTVA

from .models import SuiviTVA
from django.http import JsonResponse




# ==================== Handlers ====================
def get_suivi_tva_data(request, dossier_id):
    try:
        suivi = SuiviTVA.objects.filter(dossier_id=dossier_id).latest('annee')  # récupère le dernier suivi
        data = {
            'annee': suivi.annee,
            'jan': suivi.jan,
            'fev': suivi.fev,
            'mars': suivi.mars,
            'avril': suivi.avril,
            'mai': suivi.mai,
            'juin': suivi.juin,
            'juillet': suivi.juillet,
            'aout': suivi.aout,
            'sep': suivi.sep,
            'oct': suivi.oct,
            'nov': suivi.nov,
            'dec': suivi.dec,
            't1': suivi.t1,
            't2': suivi.t2,
            't3': suivi.t3,
            't4': suivi.t4,
        }
        return JsonResponse(data)
    except SuiviTVA.DoesNotExist:
        return JsonResponse({'error': 'Aucun suivi TVA trouvé pour ce dossier'}, status=200)


import fitz  

# fiscal/utils.py
import re
from PyPDF2 import PdfReader

def extraire_annee_du_pdf(fichier_pdf):
    try:
        reader = PdfReader(fichier_pdf)
        texte = ""
        for page in reader.pages:
            texte += page.extract_text()
        match = re.search(r"(20\d{2})", texte)
        if match:
            return int(match.group(1))
    except Exception as e:
        print("Erreur extraction PDF :", e)
    return None




class SuiviFiscalListView(TemplateView):
    template_name = "fiscal/suivi_fiscal_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suivis_tva'] = SuiviTVA.objects.all()
        context['suivis_cmetir'] = CMIR.objects.all()
        context['suivis_acomptes'] = Acompte.objects.all()
        context['depots_bilan'] = DepotBilan.objects.all()
        context['suivis_forfaitaire'] = SuiviForfaitaire.objects.all()
        return context

# SuiviTVA Views
class SuiviTVAListView(RoleRequiredMixin, ListView):
    model = SuiviTVA
    template_name = 'fiscal/suivitva_list.html'
    context_object_name = 'suivitva_list'
    allowed_roles = ['administrateur', 'comptable']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(code__icontains=search_query) |
                Q(dossier__denomination__icontains=search_query) |
                Q(dossier__code__icontains=search_query)
            )
        return queryset

class SuiviTVADetailView(RoleRequiredMixin, DetailView):
    model = SuiviTVA
    template_name = 'fiscal/suivitva_detail.html'
    context_object_name = 'suivitva'
    allowed_roles = ['administrateur', 'comptable']

class SuiviTVACreateView(RoleRequiredMixin, CreateView):
    model = SuiviTVA
    template_name = 'fiscal/suivitva_form.html'
    fields = '__all__'
    success_url = reverse_lazy('fiscal:suivitva_list')
    allowed_roles = ['administrateur', 'comptable']

class SuiviTVAUpdateView(RoleRequiredMixin, UpdateView):
    model = SuiviTVA
    template_name = 'fiscal/suivitva_form.html'
    fields = '__all__'
    success_url = reverse_lazy('fiscal:suivitva_list')
    allowed_roles = ['administrateur', 'comptable']

class SuiviTVADeleteView(RoleRequiredMixin, DeleteView):
    model = SuiviTVA
    template_name = 'fiscal/suivitva_confirm_delete.html'
    success_url = reverse_lazy('fiscal:suivitva_list')
    allowed_roles = ['administrateur', 'comptable']

# Acompte Views
class AcompteListView(RoleRequiredMixin, ListView):
    model = Acompte
    template_name = 'fiscal/acompte_list.html'
    context_object_name = 'acomptes'
    allowed_roles = ['administrateur', 'comptable']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        
        if search_query:
            queryset = queryset.filter(
                Q(dossier__denomination__icontains=search_query) |
                Q(code__icontains=search_query)
            )
       
        return queryset

class AcompteDetailView(RoleRequiredMixin, DetailView):
    model = Acompte
    template_name = 'fiscal/acompte_detail.html'
    context_object_name = 'acompte'
    allowed_roles = ['administrateur', 'comptable']

class AcompteCreateView(RoleRequiredMixin, CreateView):
    model = Acompte
    template_name = 'fiscal/acompte_form.html'
    form_class = AcompteForm 
    success_url = reverse_lazy('fiscal:acompte_list')
    allowed_roles = ['administrateur', 'comptable']

    def get_form_kwargs(self):
        """Ajoutez des arguments supplémentaires au formulaire si nécessaire"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs

    def form_invalid(self, form):
        print(form.errors)  # DEBUG
        return super().form_invalid(form)
    
    def form_valid(self, form):
       form.instance.montant = form.cleaned_data.get('is_montant', Decimal('0.00'))
       return super().form_valid(form)

class AcompteUpdateView(RoleRequiredMixin, UpdateView):
    model = Acompte
    template_name = 'fiscal/acompte_form.html'
    fields = '__all__'
    success_url = reverse_lazy('fiscal:acompte_list')
    allowed_roles = ['administrateur', 'comptable']

class AcompteDeleteView(RoleRequiredMixin, DeleteView):
    model = Acompte
    template_name = 'fiscal/acompte_confirm_delete.html'
    success_url = reverse_lazy('fiscal:acompte_list')
    allowed_roles = ['administrateur', 'comptable']

# CMIR Views
class CMIRListView(RoleRequiredMixin, ListView):
    model = CMIR
    template_name = 'fiscal/cmir_list.html'
    context_object_name = 'cmir_list'
    allowed_roles = ['administrateur', 'comptable']
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        
        if search_query:
            queryset = queryset.filter(
                Q(dossier__denomination__icontains=search_query) |
                Q(code__icontains=search_query)
            )
       
        return queryset

class CMIRDetailView(RoleRequiredMixin, DetailView):
    model = CMIR
    template_name = 'fiscal/cmir_detail.html'
    context_object_name = 'cmir'
    allowed_roles = ['administrateur', 'comptable']

class CMIRCreateView(RoleRequiredMixin, CreateView):
    model = CMIR
    template_name = 'fiscal/cmir_form.html'
    fields = '__all__'
    success_url = reverse_lazy('fiscal:cmir_list')
    allowed_roles = ['administrateur', 'comptable']

class CMIRUpdateView(RoleRequiredMixin, UpdateView):
    model = CMIR
    template_name = 'fiscal/cmir_form.html'
    fields = '__all__'
    success_url = reverse_lazy('fiscal:cmir_list')
    allowed_roles = ['administrateur', 'comptable']

class CMIRDeleteView(RoleRequiredMixin, DeleteView):
    model = CMIR
    template_name = 'fiscal/cmir_confirm_delete.html'
    success_url = reverse_lazy('fiscal:cmir_list')
    allowed_roles = ['administrateur', 'comptable']

# DepotBilan Views
class DepotBilanListView(RoleRequiredMixin, ListView):
    model = DepotBilan
    template_name = 'fiscal/depotbilan_list.html'
    context_object_name = 'depotbilan_list'
    allowed_roles = ['administrateur', 'comptable']
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        
        if search_query:
            queryset = queryset.filter(
                Q(dossier__denomination__icontains=search_query) |
                Q(code__icontains=search_query)
            )
       
        return queryset

class DepotBilanDetailView(RoleRequiredMixin, DetailView):
    model = DepotBilan
    template_name = 'fiscal/depotbilan_detail.html'
    context_object_name = 'depotbilan'
    allowed_roles = ['administrateur', 'comptable']

class DepotBilanCreateView(RoleRequiredMixin, CreateView):
    model = DepotBilan
    template_name = 'fiscal/depotbilan_form.html'
    fields = '__all__'
    success_url = reverse_lazy('fiscal:depotbilan_list')
    allowed_roles = ['administrateur', 'comptable']

class DepotBilanUpdateView(RoleRequiredMixin, UpdateView):
    model = DepotBilan
    template_name = 'fiscal/depotbilan_form.html'
    fields = '__all__'
    success_url = reverse_lazy('fiscal:depotbilan_list')
    allowed_roles = ['administrateur', 'comptable']

class DepotBilanDeleteView(RoleRequiredMixin, DeleteView):
    model = DepotBilan
    template_name = 'fiscal/depotbilan_confirm_delete.html'
    success_url = reverse_lazy('fiscal:depotbilan_list')
    allowed_roles = ['administrateur', 'comptable']

# SuiviForfaitaire Views
class SuiviForfaitaireListView(RoleRequiredMixin, ListView):
    model = SuiviForfaitaire
    template_name = 'fiscal/suiviforfaitaire_list.html'
    context_object_name = 'suiviforfaitaire_list'
    allowed_roles = ['administrateur', 'comptable']
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        
        if search_query:
            queryset = queryset.filter(
                Q(code__icontains=search_query) |
                Q(pp__icontains=search_query)
            )
       
        return queryset

class SuiviForfaitaireDetailView(RoleRequiredMixin, DetailView):
    model = SuiviForfaitaire
    template_name = 'fiscal/suiviforfaitaire_detail.html'
    context_object_name = 'suiviforfaitaire'
    allowed_roles = ['administrateur', 'comptable']

class SuiviForfaitaireCreateView(RoleRequiredMixin, CreateView):
    model = SuiviForfaitaire
    template_name = 'fiscal/suiviforfaitaire_form.html'
    fields = '__all__'
    success_url = reverse_lazy('fiscal:suiviforfaitaire_list')
    allowed_roles = ['administrateur', 'comptable']

class SuiviForfaitaireUpdateView(RoleRequiredMixin, UpdateView):
    model = SuiviForfaitaire
    template_name = 'fiscal/suiviforfaitaire_form.html'
    fields = '__all__'
    success_url = reverse_lazy('fiscal:suiviforfaitaire_list')
    allowed_roles = ['administrateur', 'comptable']

class SuiviForfaitaireDeleteView(RoleRequiredMixin, DeleteView):
    model = SuiviForfaitaire
    template_name = 'fiscal/suiviforfaitaire_confirm_delete.html'
    success_url = reverse_lazy('fiscal:suiviforfaitaire_list')
    allowed_roles = ['administrateur', 'comptable']
