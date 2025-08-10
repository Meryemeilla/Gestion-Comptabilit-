from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from utilisateurs.models import RoleRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from .models import Honoraire, ReglementHonoraire, HonorairePV, ReglementHonorairePV
from .forms import HonoraireForm, HonorairePVForm, ReglementHonoraireForm, ReglementHonorairePVForm
from django.contrib import messages
from django.db.models import Q

class HonoraireCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['comptable', 'administrateur']
    model = Honoraire
    form_class = HonoraireForm
    template_name = 'honoraires/honoraire_form.html'
    success_url = reverse_lazy('honoraires:reglement_list')

    def form_valid(self, form):
        messages.success(self.request, "Honoraire créé avec succès.")
        return super().form_valid(form)



class ReglementHonoraireCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['comptable', 'administrateur']
    model = ReglementHonoraire
    form_class = ReglementHonoraireForm
    template_name = 'honoraires/reglement_form.html'
    success_url = reverse_lazy('honoraires:reglement_list')

    def form_valid(self, form):
        # The custom save method in the form handles setting honoraire or honoraire_pv
        reglement = form.save()
        messages.success(self.request, "Règlement d'honoraire créé avec succès.")
        return super().form_valid(form)



class HonoraireListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['comptable', 'administrateur']
    model = Honoraire
    template_name = 'honoraires/honoraire_list.html'
    context_object_name = 'honoraires'

    def get_queryset(self):
        queryset = super().get_queryset()
        filtre = self.request.GET.get('filtre')
        
        if filtre == 'pv':
            # Filtrer par HonorairePV liés, par exemple dossiers ayant un honoraire_pv
            queryset = queryset.filter(dossier__honoraire_pvs__isnull=False).distinct()
        elif filtre == 'mensuel':
            queryset = queryset.filter(montant_mensuel__gt=0)
        elif filtre == 'trimestriel':
            queryset = queryset.filter(montant_trimestriel__gt=0)
        elif filtre == 'annuel':
            queryset = queryset.filter(montant_annuel__gt=0)

        return queryset


class ReglementHonoraireListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['comptable', 'administrateur']
    model = ReglementHonoraire
    template_name = 'honoraires/reglement_list.html'
    context_object_name = 'reglements'


class HonorairePVCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['comptable', 'administrateur']
    model = HonorairePV
    form_class = HonorairePVForm
    template_name = 'honoraires/honoraire_pv_form.html'
    success_url = reverse_lazy('honoraires:honoraire_pv_list')



from django.views.generic import DetailView, UpdateView, DeleteView

class HonoraireDetailView(RoleRequiredMixin, LoginRequiredMixin, DetailView):
    allowed_roles = ['comptable', 'administrateur']
    model = Honoraire
    template_name = 'honoraires/honoraire_detail.html'
    context_object_name = 'honoraire'


class HonorairePVDetailView(RoleRequiredMixin, LoginRequiredMixin, DetailView):
    allowed_roles = ['comptable', 'administrateur']
    model = HonorairePV
    template_name = 'honoraires/honoraire_pv_detail.html'
    context_object_name = 'honoraire_pv'


class HonorairePVUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    allowed_roles = ['comptable', 'administrateur']
    model = HonorairePV
    form_class = HonorairePVForm
    template_name = 'honoraires/honoraire_pv_form.html'
    success_url = reverse_lazy('honoraires:honoraire_pv_list')


class HonorairePVDeleteView(RoleRequiredMixin, LoginRequiredMixin, DeleteView):
    allowed_roles = ['comptable', 'administrateur']
    model = HonorairePV
    template_name = 'honoraires/honoraire_pv_confirm_delete.html'
    success_url = reverse_lazy('honoraires:honoraire_pv_list')
    allowed_roles = ['comptable', 'administrateur']
   

class HonoraireUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    allowed_roles = ['comptable', 'administrateur']
    model = Honoraire
    form_class = HonoraireForm
    template_name = 'honoraires/honoraire_form.html'
    success_url = reverse_lazy('honoraires:honoraire_list')

    def form_valid(self, form):
        messages.success(self.request, "Honoraire mis à jour avec succès.")
        return super().form_valid(form)

class HonoraireDeleteView(RoleRequiredMixin, LoginRequiredMixin, DeleteView):
    allowed_roles = ['comptable', 'administrateur']
    model = Honoraire
    template_name = 'honoraires/honoraire_confirm_delete.html'
    success_url = reverse_lazy('honoraires:honoraire_list')

    def form_valid(self, form):
        messages.success(self.request, "Honoraire supprimé avec succès.")
        return super().form_valid(form)


from django.views.generic import TemplateView

class ReglementHonorairePVCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['comptable', 'administrateur']
    model = ReglementHonorairePV
    form_class = ReglementHonorairePVForm
    template_name = 'honoraires/reglement_pv_form.html'
    success_url = reverse_lazy('honoraires:honoraire_pv_list') # Changed success_url to honoraire_pv_list

    def form_valid(self, form):
        messages.success(self.request, "Règlement d'honoraire PV créé avec succès.")
        return super().form_valid(form)


class HonorairePVListView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['comptable', 'administrateur']
    model = HonorairePV
    template_name = 'honoraires/honoraire_pv_list.html'
    context_object_name = 'honoraires_pv'
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        
        if search_query:
            queryset = queryset.filter(
                Q(dossier__denomination__icontains=search_query) |
                Q(code__icontains=search_query)
            )
       
        return queryset


class HonoraireDashboardView(RoleRequiredMixin, LoginRequiredMixin, TemplateView):
    allowed_roles = ['comptable', 'administrateur']
    template_name = 'honoraires/dashboard.html'
