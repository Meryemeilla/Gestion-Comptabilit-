from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from .models import Dossier

from django.shortcuts import render, get_object_or_404
from .models import Dossier
from comptables.models import Comptable
from django.db.models import Q
from cabinet.forms import DossierForm
from django.core.paginator import Paginator






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
from django.shortcuts import get_object_or_404, render

def client_dossiers(request):
    dossiers = Dossier.objects.none()

    if request.user.is_authenticated:
        if request.user.is_client():
            dossiers = Dossier.objects.filter(client=request.user)
        elif request.user.is_comptable():
            try:
                comptable_profile = request.user.comptable_profile
                dossiers = Dossier.objects.filter(comptable_traitant=comptable_profile)
            except Comptable.DoesNotExist:
                dossiers = Dossier.objects.none()
        else:
            assign_to_comptable_id = request.GET.get('assign_to_comptable')
            if assign_to_comptable_id:
                comptable = get_object_or_404(Comptable, pk=assign_to_comptable_id)
                dossiers = Dossier.objects.filter(comptable_traitant=comptable)
            else:
                dossiers = Dossier.objects.all()

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
    }
    return render(request, 'dossiers/list.html', context)

