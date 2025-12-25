"""
Fonctions utilitaires et helpers techniques.

Fichier: cabinet/utils/pdf_export.py
"""

# ==================== Imports ====================
from django.http import HttpResponse
from django.template.loader import render_to_string
# WeasyPrint import rendu paresseux au niveau des méthodes
# from weasyprint import HTML, CSS
from datetime import datetime
import io

from comptables.models import Comptable
from dossiers.models import Dossier
from honoraires.models import Honoraire
import os

# Ajoute MSYS2 aux variables d'environnement
os.environ['PATH'] = r'C:\msys64\mingw64\bin;' + os.environ['PATH']
os.environ['FONTCONFIG_PATH'] = r'C:\msys64\mingw64\etc\fonts'



# ==================== Classes ====================
class ExportPDF:
    """Classe pour gérer les exports PDF"""
    
    def __init__(self):
        self.css_style_string = '''
            @page {
                size: A4;
                margin: 2cm;
            }
            
            body {
                font-family: Arial, sans-serif;
                font-size: 12px;
                line-height: 1.4;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #366092;
                padding-bottom: 10px;
            }
            
            .header h1 {
                color: #366092;
                margin: 0;
                font-size: 24px;
            }
            
            .header .date {
                color: #666;
                font-size: 14px;
                margin-top: 5px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
            }
            
            .stat-card .number {
                font-size: 24px;
                font-weight: bold;
                color: #366092;
            }
            
            .stat-card .label {
                color: #666;
                margin-top: 5px;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            
            table th {
                background-color: #366092;
                color: white;
                padding: 10px;
                text-align: left;
                font-weight: bold;
            }
            
            table td {
                padding: 8px 10px;
                border-bottom: 1px solid #ddd;
            }
            
            table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            
            .section-title {
                color: #366092;
                font-size: 18px;
                font-weight: bold;
                margin: 30px 0 15px 0;
                border-bottom: 1px solid #366092;
                padding-bottom: 5px;
            }
            
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #666;
                font-size: 10px;
            }
        ''')
    
    def export_rapport_comptables(self):
        """Génère un rapport PDF des comptables"""
        comptables = Comptable.objects.filter(actif=True).order_by('nom', 'prenom')
        
        # Calcul des statistiques
        total_comptables = comptables.count()
        total_dossiers = sum(c.nbre_pm + c.nbre_et for c in comptables)
        moyenne_dossiers = total_dossiers / total_comptables if total_comptables > 0 else 0
        
        context = {
            'title': 'Rapport des Comptables',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'comptables': comptables,
            'stats': {
                'total_comptables': total_comptables,
                'total_dossiers': total_dossiers,
                'moyenne_dossiers': round(moyenne_dossiers, 1),
            }
        }
        
        try:
            from weasyprint import HTML, CSS
        except Exception:
            return HttpResponse(
                "Export PDF indisponible: dépendances WeasyPrint manquantes ou non chargées.",
                status=503
            )
        css_style = CSS(string=self.css_style_string)
        html_content = render_to_string('pdf/rapport_comptables.html', context)
        html = HTML(string=html_content)
        try:
            pdf = html.write_pdf(stylesheets=[css_style])
        except Exception:
            return HttpResponse(
                "Export PDF indisponible: erreur d’exécution WeasyPrint/GTK (write_pdf).",
                status=503
            )
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="rapport_comptables_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    
    def export_rapport_dossiers(self):
        """Génère un rapport PDF des dossiers"""
        dossiers = Dossier.objects.select_related('comptable_traitant').filter(actif=True).order_by('denomination')
        
        # Calcul des statistiques
        total_dossiers = dossiers.count()
        dossiers_pm = dossiers.filter(forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'EURL', 'SASU', 'SAS']).count()
        dossiers_pp = dossiers.filter(forme_juridique__in=['EI', 'EIRL', 'AUTO']).count()
        dossiers_avec_tva = dossiers.filter(declaration_tva__in=['MENSUELLE', 'TRIMESTRIELLE']).count()
        
        # Répartition par comptable
        from django.db.models import Count
        repartition_comptable = list(
            dossiers.values('comptable_traitant__nom', 'comptable_traitant__prenom')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Répartition par forme juridique
        repartition_forme = list(
            dossiers.values('forme_juridique')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        context = {
            'title': 'Rapport des Dossiers',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'dossiers': dossiers[:50],  # Limiter à 50 pour le PDF
            'stats': {
                'total_dossiers': total_dossiers,
                'dossiers_pm': dossiers_pm,
                'dossiers_pp': dossiers_pp,
                'dossiers_avec_tva': dossiers_avec_tva,
                'pourcentage_pm': round((dossiers_pm / total_dossiers * 100), 1) if total_dossiers > 0 else 0,
                'pourcentage_pp': round((dossiers_pp / total_dossiers * 100), 1) if total_dossiers > 0 else 0,
            },
            'repartition_comptable': repartition_comptable[:10],
            'repartition_forme': repartition_forme,
        }
        
        try:
            from weasyprint import HTML, CSS
        except Exception:
            return HttpResponse(
                "Export PDF indisponible: dépendances WeasyPrint manquantes ou non chargées.",
                status=503
            )
        css_style = CSS(string=self.css_style_string)
        html_content = render_to_string('pdf/rapport_dossiers.html', context)
        html = HTML(string=html_content)
        try:
            pdf = html.write_pdf(stylesheets=[css_style])
        except Exception:
            return HttpResponse(
                "Export PDF indisponible: erreur d’exécution WeasyPrint/GTK (write_pdf).",
                status=503
            )
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="rapport_dossiers_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    
    def export_rapport_honoraires(self):
        """Génère un rapport PDF des honoraires"""
        honoraires = Honoraire.objects.select_related('dossier', 'dossier__comptable_traitant').all()
        
        # Calcul des statistiques
        total_honoraires = honoraires.count()
        total_mensuel = sum(h.montant_mensuel for h in honoraires)
        total_trimestriel = sum(h.montant_trimestriel for h in honoraires)
        total_annuel = sum(h.montant_annuel for h in honoraires)
        
        total_regle_mensuel = sum(h.total_reglements_mensuel for h in honoraires)
        total_regle_trimestriel = sum(h.total_reglements_trimestriel for h in honoraires)
        total_regle_annuel = sum(h.total_reglements_annuel for h in honoraires)
        
        context = {
            'title': 'Rapport des Honoraires',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'honoraires': honoraires,
            'stats': {
                'total_honoraires': total_honoraires,
                'total_mensuel': total_mensuel,
                'total_trimestriel': total_trimestriel,
                'total_annuel': total_annuel,
                'total_regle_mensuel': total_regle_mensuel,
                'total_regle_trimestriel': total_regle_trimestriel,
                'total_regle_annuel': total_regle_annuel,
                'taux_recouvrement_mensuel': round((total_regle_mensuel / total_mensuel * 100), 1) if total_mensuel > 0 else 0,
                'taux_recouvrement_trimestriel': round((total_regle_trimestriel / total_trimestriel * 100), 1) if total_trimestriel > 0 else 0,
                'taux_recouvrement_annuel': round((total_regle_annuel / total_annuel * 100), 1) if total_annuel > 0 else 0,
            }
        }
        
        try:
            from weasyprint import HTML, CSS
        except Exception:
            return HttpResponse(
                "Export PDF indisponible: dépendances WeasyPrint manquantes ou non chargées.",
                status=503
            )
        css_style = CSS(string=self.css_style_string)
        html_content = render_to_string('pdf/rapport_honoraires.html', context)
        html = HTML(string=html_content)
        try:
            pdf = html.write_pdf(stylesheets=[css_style])
        except Exception:
            return HttpResponse(
                "Export PDF indisponible: erreur d’exécution WeasyPrint/GTK (write_pdf).",
                status=503
            )
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="rapport_honoraires_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    
    def export_suivi_tva_pdf(self, annee=None):
        """Génère un rapport PDF du suivi TVA"""
        if not annee:
            annee = datetime.now().year
        
        from fiscal.models import SuiviTVA
        suivis = SuiviTVA.objects.select_related('dossier', 'dossier__comptable_traitant').filter(annee=annee)
        
        # Calcul des statistiques
        total_dossiers = suivis.count()
        dossiers_mensuel_complet = suivis.filter(
            jan=True, fev=True, mars=True, avril=True, mai=True, juin=True,
            juillet=True, aout=True, sep=True, oct=True, nov=True, dec=True
        ).count()

        # Préparer le rendu et gérer l'import WeasyPrint paresseux
        try:
            from weasyprint import HTML, CSS
        except Exception:
            return HttpResponse(
                "Export PDF indisponible: dépendances WeasyPrint manquantes ou non chargées.",
                status=503
            )
        css_style = CSS(string=self.css_style_string)
        dossiers_trimestriel_complet = suivis.filter(t1=True, t2=True, t3=True, t4=True).count()
        
        context = {
            'title': f'Suivi TVA {annee}',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'annee': annee,
            'suivis': suivis,
            'stats': {
                'total_dossiers': total_dossiers,
                'dossiers_mensuel_complet': dossiers_mensuel_complet,
                'dossiers_trimestriel_complet': dossiers_trimestriel_complet,
                'taux_completion_mensuel': round((dossiers_mensuel_complet / total_dossiers * 100), 1) if total_dossiers > 0 else 0,
                'taux_completion_trimestriel': round((dossiers_trimestriel_complet / total_dossiers * 100), 1) if total_dossiers > 0 else 0,
            }
        }
        
        html_content = render_to_string('pdf/suivi_tva.html', context)
        html = HTML(string=html_content)
        try:
            pdf = html.write_pdf(stylesheets=[css_style])
        except Exception:
            return HttpResponse(
                "Export PDF indisponible: erreur d’exécution WeasyPrint/GTK (write_pdf).",
                status=503
            )
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="suivi_tva_{annee}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        return response

