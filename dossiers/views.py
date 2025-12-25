"""
Django views (gestion des requêtes HTTP).

Fichier: dossiers/views.py
"""

# ==================== Imports ====================
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from .models import Dossier
from comptables.models import Comptable
from honoraires.models import Honoraire
from reclamations.models import Reclamation
from fiscal.models import Acompte, CMIR, DepotBilan, SuiviForfaitaire, SuiviTVA
from django.db.models import Q
from cabinet.forms import DossierForm
from django.core.paginator import Paginator
from django.apps import apps






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

def restore_dossier(request, pk):
    dossier = get_object_or_404(Dossier.all_objects, pk=pk)
    dossier.is_deleted = False
    dossier.save()
    return redirect('cabinet:dossier_list')

def delete_dossier(request, pk):
    dossier = get_object_or_404(Dossier.objects, pk=pk)
    dossier.is_deleted = True
    dossier.save()
    return redirect('cabinet:dossier_list')


def corbeille_generique(request, model_name=None):
    deleted_items = []
    model_map = {
        'dossier': Dossier,
        'honoraire': Honoraire,
        'reclamation': Reclamation,
        'comptable': Comptable,
        'acompte': Acompte,
        'cmir': CMIR,
        'tva': SuiviTVA,
        'depotbilan': DepotBilan,
        'suiviforfaitaire': SuiviForfaitaire,
    }

    if model_name and model_name in model_map:
        Model = model_map[model_name]
        if hasattr(Model, 'all_objects'): # Check if soft-delete manager exists
            deleted_items = Model.all_objects.filter(is_deleted=True)
        else:
            deleted_items = Model.objects.filter(is_deleted=True)
    else:
        # If no specific model is requested, list all models with deleted items
        for name, Model in model_map.items():
            if hasattr(Model, 'all_objects'):
                items = Model.all_objects.filter(is_deleted=True)
            else:
                items = Model.objects.filter(is_deleted=True)
            if items.exists():
                deleted_items.append({'model_name': name, 'items': items})

    context = {
        'deleted_items': deleted_items,
        'model_name': model_name,
        'model_map': model_map,
    }
    return render(request, 'dossiers/corbeille.html', context)

def restore_item(request, model_name, pk):
    model_map = {
        'dossier': Dossier,
        'honoraire': Honoraire,
        'reclamation': Reclamation,
        'comptable': Comptable,
        'acompte': Acompte,
        'cmir': CMIR,
        'tva': SuiviTVA,
        'depotbilan': DepotBilan,
        'suiviforfaitaire': SuiviForfaitaire,
    }
    Model = model_map.get(model_name)
    if not Model:
        # Handle error: model not found
        return redirect('dossiers:corbeille_generique')

    if hasattr(Model, 'all_objects'):
        item = get_object_or_404(Model.all_objects, pk=pk)
    else:
        item = get_object_or_404(Model, pk=pk)

    item.is_deleted = False
    item.save()
    if model_name == 'dossier':
        return redirect('cabinet:dossier_list')
    elif model_name == 'honoraire':
        return redirect('honoraires:honoraire_list')
    elif model_name == 'reclamation':
        return redirect('reclamations:reclamation_list')
    elif model_name == 'comptable':
        return redirect('comptables:comptable_list')
    elif model_name == 'acompte':
        return redirect('fiscal:acompte_list')
    elif model_name == 'cmir':
        return redirect('fiscal:cmir_list')
    elif model_name == 'tva':
        return redirect('fiscal:suivitva_list')
    elif model_name == 'depotbilan':
        return redirect('fiscal:depotbilan_list')
    elif model_name == 'suiviforfaitaire':
        return redirect('fiscal:suiviforfaitaire_list')
    return redirect('dossiers:corbeille_generique_model', model_name=model_name)

