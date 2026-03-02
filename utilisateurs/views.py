"""
Django views (gestion des requêtes HTTP).

Fichier: utilisateurs/views.py
"""

# ==================== Imports ====================
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import ClientRegisterForm, ComptableRegisterForm
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from comptables.models import Comptable # Import Comptable model

# ==================== Handlers ====================
def home(request):
    return render(request, 'home.html')

@login_required
def profile(request):
    return render(request, 'registration/profile.html')

def role_based_redirect(request, user):
    if request.user.is_authenticated:
        debug_info = {
            'username': user.username,
            'is_comptable': user.is_comptable,
            'is_client': user.is_client,
            'is_superuser': user.is_superuser,
            'is_administrateur': user.is_administrateur,
            'comptable_profile_exists': False,
            'comptable_is_approved': False,
            'redirect_path': 'N/A'
        }

        if user.is_administrateur():
            debug_info['redirect_path'] = 'cabinet:dashboard'
            print(f"DEBUG REDIRECT: {debug_info}")
            return reverse_lazy('cabinet:dashboard')
        elif user.is_comptable():
            try:
                comptable_profile = user.comptable_profile
                debug_info['comptable_profile_exists'] = True
                debug_info['comptable_is_approved'] = comptable_profile.is_approved
                if comptable_profile.is_approved:
                    debug_info['redirect_path'] = 'cabinet:comptable_list'
                    print(f"DEBUG REDIRECT: {debug_info}")
                    return reverse_lazy('cabinet:comptable_list')
                else:
                    debug_info['redirect_path'] = 'login (not approved)'
                    messages.error(request, "Votre compte comptable n'a pas encore été approuvé. Veuillez contacter l'administrateur.")
                    logout(request)
                    print(f"DEBUG REDIRECT: {debug_info}")
                    return reverse_lazy('login')
            except Comptable.DoesNotExist:
                debug_info['redirect_path'] = 'login (profile missing)'
                messages.error(request, "Votre profil comptable est incomplet ou n'existe pas. Veuillez contacter l'administrateur.")
                logout(request)
                print(f"DEBUG REDIRECT: {debug_info}")
                return reverse_lazy('login')
        elif user.is_client():
            debug_info['redirect_path'] = 'cabinet:dashboard'
            print(f"DEBUG REDIRECT: {debug_info}")
            return reverse_lazy('cabinet:dashboard')
        
        debug_info['redirect_path'] = 'login (no role match)'
        print(f"DEBUG REDIRECT: {debug_info}")
        return reverse_lazy('login')

class CustomLoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = False

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            if user.is_comptable() and not user.comptable_profile.is_approved:
                messages.error(self.request, "Votre compte n'a pas encore été approuvé par un administrateur.")
                return self.form_invalid(form)
            auth_login(self.request, user)
            return super().form_valid(form)
        else:
            messages.error(self.request, "Nom d'utilisateur ou mot de passe incorrect.")
            return self.form_invalid(form)

    def get_success_url(self):
        return role_based_redirect(self.request, self.request.user)

class CustomLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('home')

def client_register(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Votre compte client a été créé avec succès et vous êtes maintenant connecté.")
            return redirect(role_based_redirect(request, user))
    else:
        form = ClientRegisterForm()
    return render(request, 'registration/client_register.html', {'form': form})

def comptable_register(request):
    if request.method == 'POST':
        form = ComptableRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre inscription a été soumise. Un administrateur doit valider votre compte avant que vous puissiez vous connecter.")
            return redirect('login')
    else:
        form = ComptableRegisterForm()
    return render(request, 'registration/comptable_register.html', {'form': form})

from .models import Client
from .forms import ClientCreationForm, ClientUpdateForm
from django.contrib.auth.decorators import user_passes_test
from django.db.models import ProtectedError, Q
from django.http import Http404
from .tasks import envoyer_email_creation_client

def est_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(est_admin)
def ajouter_client_par_admin(request):
    if request.method == 'POST':
        form = ClientCreationForm(request.POST)
        if form.is_valid():
            client = form.save()
            
            raw_password = form.cleaned_data.get('password1')
            login_url = request.build_absolute_uri('/accounts/login/')

            try:
                envoyer_email_creation_client.delay(
                    to_email=client.email,
                    password=raw_password,
                    nom_client=client.nom_entreprise,
                    prenom=client.user.first_name,
                    username=client.user.username,
                    login_url=login_url
                )
            except Exception as e:
                messages.warning(request, f"Le client a été créé, mais l'email n'a pas pu être envoyé : {e}")

            messages.success(request, "Client ajouté avec succès.")
            return redirect('utilisateurs:liste_clients')
    else:
        form = ClientCreationForm()

    return render(request, 'cabinet/ajouter_client_admin.html', {
        'form': form,
        'admin_creation': True,
    })

@login_required
@user_passes_test(est_admin)
def supprimer_client(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        raise Http404("Client non trouvé")

    if request.method == "POST":
        try:
            user = client.user
            client.delete()
            if user:
                user.delete()
            messages.success(request, "Le client a été supprimé avec succès.")
        except ProtectedError:
            messages.error(request, "Impossible de supprimer ce client car il est lié à d'autres données.")
        return redirect('utilisateurs:liste_clients')
    return redirect('utilisateurs:liste_clients')

@login_required
@user_passes_test(est_admin)
def detail_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    dossier = client.dossiers_client.order_by('-id').first()
    return render(request, 'cabinet/detail_clients.html', {'client': client,'dossier': dossier,}) 

@login_required
@user_passes_test(est_admin)
def liste_clients(request):
    search = request.GET.get('search', '')
    clients = Client.objects.all()
    
    if search:
        clients = clients.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(email__icontains=search) |
            Q(telephone__icontains=search)
        )

    return render(request, 'cabinet/liste_clients.html', {
        'clients': clients,
    })

@user_passes_test(est_admin)
def modifier_client_par_admin(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    user = client.user

    if request.method == 'POST':
        form = ClientUpdateForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client modifié avec succès.")
            return redirect('utilisateurs:liste_clients')
    else:
        # Initialize form with data from BOTH models
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        form = ClientUpdateForm(instance=client, initial=initial_data)

    return render(request, 'cabinet/ajouter_client_admin.html', {
        'form': form,
        'client': client,
        'modification': True,
    })


