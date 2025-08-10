from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from cabinet.util import extract_text_from_pdf, extraire_infos_dossier
from django.http import JsonResponse
from fiscal.models import SuiviTVA
@csrf_exempt
def analyser_document_view(request):
    if request.method == 'POST' and request.FILES.get('document'):
        file = request.FILES['document']
        text = extract_text_from_pdf(file)
        infos = extraire_infos_dossier(text)
        return JsonResponse(infos)
    return JsonResponse({'error': 'Invalid request'}, status=400)



def get_tva_for_dossier(request, dossier_id):
    try:
        tva = SuiviTVA.objects.get(dossier__id=dossier_id)
        data = {
            "annee": tva.annee,
            "janvier": tva.janvier,
            "fevrier": tva.fevrier,
            "mars": tva.mars,
            "avril": tva.avril,
            "mai": tva.mai,
            "juin": tva.juin,
            "juillet": tva.juillet,
            "aout": tva.aout,
            "septembre": tva.septembre,
            "octobre": tva.octobre,
            "novembre": tva.novembre,
            "decembre": tva.decembre,
            "t1": tva.t1,
            "t2": tva.t2,
            "t3": tva.t3,
            "t4": tva.t4,
        }
        return JsonResponse(data)
    except SuiviTVA.DoesNotExist:
        return JsonResponse({"error": "Aucune info TVA trouvée pour ce dossier"}, status=404)
