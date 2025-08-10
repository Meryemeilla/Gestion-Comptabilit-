from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from cabinet.forms import ClientRegisterForm
from .forms import ComptableRegisterForm
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from comptables.models import Comptable # Import Comptable model

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

        if user.is_superuser or user.is_administrateur:
            debug_info['redirect_path'] = 'cabinet:dashboard'
            print(f"DEBUG REDIRECT: {debug_info}")
            return reverse_lazy('cabinet:dashboard')
        elif user.is_comptable:
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
        elif user.is_client:
            debug_info['redirect_path'] = 'cabinet:dashboard'
            print(f"DEBUG REDIRECT: {debug_info}")
            return reverse_lazy('cabinet:dashboard')
        
        debug_info['redirect_path'] = 'login (no role match)'
        print(f"DEBUG REDIRECT: {debug_info}")
        return reverse_lazy('login')

class CustomLoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

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
        return role_based_redirect(self.request.user, self.request)

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


