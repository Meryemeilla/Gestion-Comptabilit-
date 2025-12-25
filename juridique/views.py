"""
Django views (gestion des requêtes HTTP).

Fichier: juridique/views.py
"""

# ==================== Imports ====================
from django.shortcuts import render
from .forms import DocumentJuridiqueForm
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from cabinet.views import RoleRequiredMixin
from .models import JuridiqueCreation, DocumentJuridique, EvenementJuridique
from cabinet.util import extract_text_from_pdf, extract_date, extract_rc_number, extract_cnss_number
from django.shortcuts import get_object_or_404
from dossiers.models import Dossier
# ==================== Handlers ====================
class JuridiqueCreationListView(LoginRequiredMixin, ListView):
    model = JuridiqueCreation
    template_name = 'juridique/juridique_creation_list.html'
    context_object_name = 'juridique_creations'
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        
        if search_query:
            queryset = queryset.filter(
                Q(dossier__denomination__icontains=search_query) |
                Q(code__icontains=search_query)
            )
       
        return queryset

# views.py


from django.http import JsonResponse
from cabinet.util import (
    extract_text_from_pdf, extract_date_finale, extract_dates_from_text,
    extract_rc_number, extract_cnss_number,
)

import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def dossier_infos_api(request):
    dossier_id = request.GET.get('dossier_id')
    if not dossier_id:
        return JsonResponse({'error': 'ID manquant'}, status=400)

    try:
        dossier = Dossier.objects.get(pk=dossier_id)
    except Dossier.DoesNotExist:
        return JsonResponse({'error': 'Dossier introuvable'}, status=404)

    infos = {}
    infos['al'] = False  # Ou supprime cette clé à chaque appel

    for doc in dossier.documents.all():
        nom_fichier = doc.fichier.name.lower()
        nom_fichier_normalized = remove_accents(nom_fichier)  # <-- Normalisation ici

        with doc.fichier.open('rb') as f:
            texte = extract_text_from_pdf(f)
        print(f"---\nTexte extrait de {nom_fichier} :\n{texte}\n---")

        dates_extraites = extract_date(texte)
        date_finale = extract_date_finale(texte)
        print(f"Date finale extraite: {date_finale}")

        if 'rc' in nom_fichier or 'RC' in nom_fichier:
            infos['rc'] = True
            infos['date_rc'] = date_finale or ""
            infos['numero_rc'] = extract_rc_number(texte) or ""

        if 'cnss' in nom_fichier:
            infos['cnss'] = True
            infos['date_cnss'] = date_finale or ""
            infos['numero_cnss'] = extract_cnss_number(texte) or ""

        if 'contrat' in nom_fichier and 'bail' in nom_fichier:
            print(f"Fichier détecté comme contrat de bail: {nom_fichier}")
            infos['contrat_bail'] = True
            infos['date_contrat_bail'] = date_finale or ""

        if 'statut' in nom_fichier or 'statuts' in nom_fichier:
            infos['statuts'] = True
            infos['date_statuts'] = date_finale or ""

        # Ici on utilise nom_fichier_normalized pour bien détecter malgré les accents
        if 'certificat_negatif' in nom_fichier_normalized or ('certificat' in nom_fichier_normalized and 'negatif' in nom_fichier_normalized):
            infos['certificat_negatif'] = True
            infos['date_certificat_negatif'] = date_finale or ""

        if 'taxe' in nom_fichier or 'professionnelle' in nom_fichier or 'taxe_professionnelle' in nom_fichier:
            infos['date_tp'] = date_finale or ""

        if 'autorisation_location' in nom_fichier or 'autorisation_de_location' in nom_fichier or 'location' in nom_fichier:
            infos['al'] = True
            infos['date_al'] = date_finale or ""

        if 'bulletin_officiel' in nom_fichier or 'bulletin' in nom_fichier or 'officiel' in nom_fichier:
            infos['bo'] = True
            infos['date_bo'] = date_finale or ""

        if 'registre_qualite' in nom_fichier_normalized or 'registre' in nom_fichier_normalized or 'qualite' in nom_fichier_normalized:
            infos['rq'] = True
            infos['date_rq'] = date_finale or ""


    rc_number = None
    for doc in dossier.documents.all():
        with doc.fichier.open('rb') as f:
            texte = extract_text_from_pdf(f)
        if not rc_number:
            rc_number = extract_rc_number(texte)

    if rc_number:
        infos['numero_rc'] = rc_number

    return JsonResponse(infos)









class JuridiqueCreationDetailView(LoginRequiredMixin, DetailView):
    model = JuridiqueCreation
    template_name = 'juridique/juridique_creation_detail.html'
    context_object_name = 'juridique_creation'

from .forms import JuridiqueCreationForm
class JuridiqueCreationCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = JuridiqueCreation
    template_name = 'juridique/juridique_creation_form.html'
    form_class = JuridiqueCreationForm
    
    success_url = reverse_lazy('juridique:juridique_creation_list')

    def form_valid(self, form):
        # Nettoyage des dates avant sauvegarde
        date_fields = [
            'date_rc', 'date_cnss', 'date_contrat_bail', 
            'date_statuts', 'date_certificat_negatif',
            'date_tp', 'date_bo', 'date_al', 'date_rq'
        ]
        
        for field in date_fields:
            date_str = form.cleaned_data.get(field)
            if not date_str:  # Si la date est vide ou None
                setattr(form.instance, field, None)
        
        # Gestion du dossier
        dossier_id = self.kwargs.get('dossier_id')
        if dossier_id:
            form.instance.dossier = get_object_or_404(Dossier, pk=dossier_id)
        
        return super().form_valid(form)

    allowed_roles = ['administrateur', 'comptable']
    def get_initial(self):
        initial = super().get_initial()
        dossier_id = self.kwargs.get('dossier_id')
        if not dossier_id:
            return initial

        dossier = get_object_or_404(Dossier, pk=dossier_id)
        initial['dossier'] = dossier

        documents = dossier.document_set.all()

        def format_date(d):
            return d.strftime('%Y-%m-%d') if d else None

        for doc in documents:
            nom_fichier = doc.fichier.name.lower()
            with doc.fichier.open('rb') as f:
                texte = extract_text_from_pdf(f)

            if 'rc' in nom_fichier:
                date_rc = extract_date(texte)
                numero_rc = extract_rc_number(texte)
                initial['rc'] = True
                if date_rc:
                    initial['date_rc'] = format_date(date_rc)
                if numero_rc:
                    initial['numero_rc'] = numero_rc

            elif 'cnss' in nom_fichier:
                date_cnss = extract_date(texte)
                numero_cnss = extract_cnss_number(texte)
                initial['cnss'] = True
                if date_cnss:
                    initial['date_cnss'] = format_date(date_cnss)
                if numero_cnss:
                    initial['numero_cnss'] = numero_cnss

            elif 'contrat' in nom_fichier or 'bail' in nom_fichier:
                date_bail = extract_date(texte)
                initial['contrat_bail'] = True
                if date_bail:
                    initial['date_contrat_bail'] = format_date(date_bail)

            elif 'statut' in nom_fichier:
                date_statut = extract_date(texte)
                initial['statuts'] = True
                if date_statut:
                    initial['date_statuts'] = format_date(date_statut)

            elif 'certificat negatif' in nom_fichier or 'certificat' in nom_fichier:
                date_cert = extract_date(texte)
                initial['certificat_negatif'] = True
                if date_cert:
                    initial['date_certificat_negatif'] = format_date(date_cert)

            elif 'tp' in nom_fichier:
                date_tp = extract_date(texte)
                initial['tp'] = True
                if date_tp:
                    initial['date_tp'] = format_date(date_tp)

            elif 'bo' in nom_fichier:
                date_bo = extract_date(texte)
                initial['bo'] = True
                if date_bo:
                    initial['date_bo'] = format_date(date_bo)

            elif 'al' in nom_fichier:
                date_al = extract_date(texte)
                initial['al'] = True
                if date_al:
                    initial['date_al'] = format_date(date_al)

            elif 'rq' in nom_fichier:
                date_rq = extract_date(texte)
                initial['rq'] = True
                if date_rq:
                    initial['date_rq'] = format_date(date_rq)

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['initial'] = self.get_initial()
        return context
    def form_invalid(self, form):
        print("Form is invalid. Errors:")
        print(form.errors)
        return super().form_invalid(form)






class DocumentJuridiqueListView(LoginRequiredMixin, ListView):
    model = DocumentJuridique
    template_name = 'juridique/document_juridique_list.html'
    context_object_name = 'document_juridiques'
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        
        if search_query:
            queryset = queryset.filter(
                Q(dossier__denomination__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query)
            )
       
        return queryset


class DocumentJuridiqueDetailView(LoginRequiredMixin, DetailView):
    model = DocumentJuridique
    template_name = 'juridique/document_juridique_detail.html'
    context_object_name = 'document_juridique'


class DocumentJuridiqueCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = DocumentJuridique
    template_name = 'juridique/document_juridique_form.html'
    form_class = DocumentJuridiqueForm
    success_url = reverse_lazy('juridique:documentjuridique_list')
    allowed_roles = ['administrateur', 'comptable']
    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        print("Form is valid. Saving object...")
        return super().form_valid(form)

class DocumentJuridiqueUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = DocumentJuridique
    template_name = 'juridique/document_juridique_form.html'
    fields = '__all__'
    success_url = reverse_lazy('juridique:documentjuridique_list')
    allowed_roles = ['administrateur', 'comptable']


class DocumentJuridiqueDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = DocumentJuridique
    template_name = 'juridique/document_juridique_confirm_delete.html'
    success_url = reverse_lazy('juridique:documentjuridique_list')
    allowed_roles = ['administrateur', 'comptable']


class EvenementJuridiqueListView(LoginRequiredMixin, ListView):
    model = EvenementJuridique
    template_name = 'juridique/evenement_juridique_list.html'
    context_object_name = 'evenement_juridiques'
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        
        if search_query:
            queryset = queryset.filter(
                Q(dossier__denomination__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query)
            )
       
        return queryset


class EvenementJuridiqueDetailView(LoginRequiredMixin, DetailView):
    model = EvenementJuridique
    template_name = 'juridique/evenement_juridique_detail.html'
    context_object_name = 'evenement_juridique'


class EvenementJuridiqueCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = EvenementJuridique
    template_name = 'juridique/evenement_juridique_form.html'
    fields = '__all__'
    success_url = reverse_lazy('juridique:evenementjuridique_list')
    allowed_roles = ['administrateur', 'comptable']


class EvenementJuridiqueUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = EvenementJuridique
    template_name = 'juridique/evenement_juridique_form.html'
    fields = '__all__'
    success_url = reverse_lazy('juridique:evenementjuridique_list')
    allowed_roles = ['administrateur', 'comptable']


class EvenementJuridiqueDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = EvenementJuridique
    template_name = 'juridique/evenement_juridique_confirm_delete.html'
    success_url = reverse_lazy('juridique:evenementjuridique_list')
    allowed_roles = ['administrateur', 'comptable']


class JuridiqueCreationDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = JuridiqueCreation
    template_name = 'juridique/juridique_creation_confirm_delete.html'
    success_url = reverse_lazy('juridique:juridique_creation_list')
    allowed_roles = ['administrateur', 'comptable']


class JuridiqueCreationUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = JuridiqueCreation
    template_name = 'juridique/juridique_creation_form.html'
    fields = '__all__'
    success_url = reverse_lazy('juridique:juridique_creation_list')
    allowed_roles = ['administrateur', 'comptable']
