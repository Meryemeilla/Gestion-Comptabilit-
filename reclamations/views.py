"""
Django views (gestion des requêtes HTTP).

Fichier: reclamations/views.py
"""

# ==================== Imports ====================
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect

from utilisateurs.models import RoleRequiredMixin
from .models import Reclamation
from .forms import ReclamationForm, ReclamationSearchForm
from dossiers.models import Dossier

# ==================== Handlers ====================

class ReclamationListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['administrateur', 'manager', 'comptable', 'client']
    model = Reclamation
    template_name = 'reclamations/list.html'
    context_object_name = 'reclamations'
    paginate_by = 20

    def get_queryset(self):
        queryset = Reclamation.objects.filter(is_deleted=False)
        user = self.request.user

        if user.is_client():
            queryset = queryset.filter(Q(dossier__client=user.client_profile) | Q(destinataire=user))
        elif user.is_comptable():
            queryset = queryset.filter(Q(destinataire=user) | Q(dossier__comptable_traitant=user.comptable_profile))

        # Filtre de recherche
        search_code = self.request.GET.get('code')
        search_denom = self.request.GET.get('denomination')
        search_class = self.request.GET.get('classement')

        if search_code:
            queryset = queryset.filter(code__icontains=search_code)
        if search_denom:
            queryset = queryset.filter(dossier__denomination__icontains=search_denom)
        if search_class:
            queryset = queryset.filter(classement=search_class)

        return queryset.order_by('-date_reception')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ReclamationSearchForm(self.request.GET)
        return context

class ReclamationDetailView(LoginRequiredMixin, DetailView):
    model = Reclamation
    template_name = 'reclamations/detail.html'
    context_object_name = 'reclamation'

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class ReclamationCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['administrateur', 'manager', 'comptable', 'client']
    model = Reclamation
    form_class = ReclamationForm
    template_name = 'reclamations/form.html'
    success_url = reverse_lazy('reclamations:reclamation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        messages.success(self.request, "Réclamation créée avec succès.")
        return super().form_valid(form)

class ReclamationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reclamation
    form_class = ReclamationForm
    template_name = 'reclamations/form.html'
    success_url = reverse_lazy('reclamations:reclamation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Réclamation mise à jour.")
        return super().form_valid(form)

class ReclamationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reclamation
    template_name = 'reclamations/delete.html'
    success_url = reverse_lazy('reclamations:reclamation_list')

    def post(self, request, *args, **kwargs):
        reclamation = self.get_object()
        reclamation.is_deleted = True
        reclamation.save()
        messages.success(request, "Réclamation mise à la corbeille.")
        return redirect(self.success_url)

class ReclamationTrashListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['administrateur', 'manager']
    model = Reclamation
    template_name = 'reclamations/trash_list.html'
    context_object_name = 'reclamations'
    paginate_by = 20

    def get_queryset(self):
        return Reclamation.objects.filter(is_deleted=True)

@login_required
def reclamation_restore(request, pk):
    reclamation = get_object_or_404(Reclamation, pk=pk, is_deleted=True)
    reclamation.is_deleted = False
    reclamation.save()
    messages.success(request, "Réclamation restaurée.")
    return redirect('reclamations:reclamation_list')


@login_required
def lancer_tache_reclamation(request, reclamation_id):
    # Logique pour déclencher une tâche Celery par exemple
    messages.info(request, f"Tâche lancée pour la réclamation {reclamation_id}.")
    return redirect('reclamations:reclamation_detail', pk=reclamation_id)
