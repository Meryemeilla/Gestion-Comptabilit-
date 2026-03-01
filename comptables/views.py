"""
Django views (gestion des requêtes HTTP).

Fichier: comptables/views.py
"""

# ==================== Imports ====================
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from utilisateurs.models import RoleRequiredMixin
from .models import Comptable
from .forms import ComptableForm

# ==================== Handlers ====================

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
            nbre_pm_count=Count('dossiers', filter=Q(dossiers__forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'EURL', 'SASU', 'SAS'], dossiers__actif=True)),
            nbre_pp_count=Count('dossiers', filter=Q(dossiers__forme_juridique__in=['EI', 'EIRL', 'AUTO'], dossiers__actif=True))
        )
        return queryset

class ComptableDetailView(RoleRequiredMixin, LoginRequiredMixin, DetailView):
    allowed_roles = ['administrateur', 'manager']
    model = Comptable
    template_name = 'comptables/detail.html'
    context_object_name = 'comptable'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Comptable, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comptable = self.get_object()
        context['dossiers'] = comptable.dossiers.filter(actif=True)
        return context

class ComptableCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['administrateur', 'manager']
    model = Comptable
    form_class = ComptableForm
    template_name = 'comptables/form.html'
    success_url = reverse_lazy('comptables:comptable_list')

    def form_valid(self, form):
        from utilisateurs.models import Utilisateur
        from utilisateurs.tasks import envoyer_email_creation_comptable
        
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']
        
        user = Utilisateur.objects.create_user(
            username=username,
            password=password,
            email=email,
            role='comptable'
        )
        
        form.instance.user = user
        response = super().form_valid(form)
        
        login_url = self.request.build_absolute_uri('/accounts/login/')
        try:
            envoyer_email_creation_comptable.delay(
                to_email=email,
                password=password,
                username=username,
                login_url=login_url
            )
        except Exception as e:
            messages.warning(self.request, "Comptable créé, mais l'email de bienvenue n'a pas pu être envoyé.")
            
        return response

class ComptableUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    allowed_roles = ['administrateur', 'manager']
    model = Comptable
    form_class = ComptableForm
    template_name = 'comptables/form.html'
    success_url = reverse_lazy('comptables:comptable_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object and self.object.user:
            kwargs['initial'] = {
                'username': self.object.user.username,
            }
        return kwargs

    def form_valid(self, form):
        if 'password' in form.changed_data:
            user = self.object.user
            user.set_password(form.cleaned_data['password'])
            user.save()
        return super().form_valid(form)

class ComptableDeleteView(RoleRequiredMixin, LoginRequiredMixin, DeleteView):
    allowed_roles = ['administrateur', 'manager']
    model = Comptable
    template_name = 'comptables/confirm_delete.html'
    success_url = reverse_lazy('comptables:comptable_list')

    def delete(self, request, *args, **kwargs):
        comptable = self.get_object()
        user = comptable.user
        response = super().delete(request, *args, **kwargs)
        if user:
            user.delete()
        messages.success(request, 'Comptable et utilisateur associé supprimés avec succès.')
        return response

class ComptableTrashListView(ListView):
    model = Comptable
    template_name = 'comptables/list.html'
    context_object_name = 'comptables'

    def get_queryset(self):
        return Comptable.objects.filter(is_deleted=True)
