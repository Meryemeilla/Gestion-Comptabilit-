from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime

from comptables.models import Comptable
from dossiers.models import Dossier
from honoraires.models import Honoraire, ReglementHonoraire, HonorairePV, ReglementHonorairePV
from fiscal.models import SuiviTVA, Acompte, CMIR, DepotBilan, SuiviForfaitaire
from reclamations.models import  Reclamation
from juridique.models import JuridiqueCreation, DocumentJuridique, EvenementJuridique

from .serializers import (
    ComptableSerializer, ComptableListSerializer,
    DossierSerializer, DossierListSerializer,
    HonoraireSerializer, ReglementHonoraireSerializer, HonorairePVSerializer, ReglementHonorairePVSerializer,
    SuiviTVASerializer, AcompteSerializer, CMIRSerializer,
    DepotBilanSerializer, SuiviForfaitaireSerializer, ReclamationSerializer,
    JuridiqueCreationSerializer, DocumentJuridiqueSerializer, EvenementJuridiqueSerializer,
    StatistiquesComptableSerializer, StatistiquesCabinetSerializer
)


class ComptableViewSet(viewsets.ModelViewSet):
    queryset = Comptable.objects.all()
    serializer_class = ComptableSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['actif', 'date_creation']
    search_fields = ['immatricule', 'nom', 'prenom', 'email']
    ordering_fields = ['nom', 'prenom', 'date_creation', 'nbre_pm', 'nbre_et']
    ordering = ['nom', 'prenom']

    def get_serializer_class(self):
        if self.action == 'list':
            return ComptableListSerializer
        return ComptableSerializer

    @action(detail=True, methods=['post'])
    def calculer_statistiques(self, request, pk=None):
        """Recalcule les statistiques d'un comptable"""
        comptable = self.get_object()
        comptable.calculer_statistiques()
        return Response({'message': 'Statistiques recalculées avec succès'})

    @action(detail=True, methods=['get'])
    def dossiers(self, request, pk=None):
        """Récupère tous les dossiers d'un comptable"""
        comptable = self.get_object()
        dossiers = comptable.dossiers.filter(actif=True)
        serializer = DossierListSerializer(dossiers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistiques(self, request, pk=None):
        """Récupère les statistiques détaillées d'un comptable"""
        comptable = self.get_object()
        dossiers = comptable.dossiers.filter(actif=True)
        
        stats = {
            'comptable': ComptableListSerializer(comptable).data,
            'total_dossiers': dossiers.count(),
            'dossiers_pm': dossiers.filter(forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'EURL', 'SASU', 'SAS']).count(),
            'dossiers_pp': dossiers.filter(forme_juridique__in=['EI', 'EIRL', 'AUTO']).count(),
            'dossiers_forfaitaires': dossiers.filter(code__in=['F', 'FS']).count(),
            'dossiers_avec_tva': dossiers.filter(declaration_tva__in=['MENSUELLE', 'TRIMESTRIELLE']).count(),
            'dossiers_sans_tva': dossiers.filter(declaration_tva='EXONEREE').count(),
        }
        
        serializer = StatistiquesComptableSerializer(stats)
        return Response(serializer.data)


class DossierViewSet(viewsets.ModelViewSet):
    queryset = Dossier.objects.select_related('comptable_traitant').all()
    serializer_class = DossierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'forme_juridique', 'declaration_tva', 'statut', 'actif', 'comptable_traitant']
    search_fields = ['denomination', 'designation', 'abreviation', 'ice', 'rc', 'if_identifiant']
    ordering_fields = ['denomination', 'date_creation', 'date_creation_dossier']
    ordering = ['denomination']

    def get_serializer_class(self):
        if self.action == 'list':
            return DossierListSerializer
        return DossierSerializer

    @action(detail=True, methods=['get'])
    def honoraires(self, request, pk=None):
        """Récupère les honoraires d'un dossier"""
        dossier = self.get_object()
        try:
            honoraire = dossier.honoraire
            serializer = HonoraireSerializer(honoraire)
            return Response(serializer.data)
        except Honoraire.DoesNotExist:
            return Response({'message': 'Aucun honoraire défini pour ce dossier'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def suivi_tva(self, request, pk=None):
        """Récupère le suivi TVA d'un dossier"""
        dossier = self.get_object()
        annee = request.query_params.get('annee', timezone.now().year)
        try:
            suivi = SuiviTVA.objects.get(dossier=dossier, annee=annee)
            serializer = SuiviTVASerializer(suivi)
            return Response(serializer.data)
        except SuiviTVA.DoesNotExist:
            return Response({'message': f'Aucun suivi TVA pour l\'année {annee}'}, status=status.HTTP_404_NOT_FOUND)


class HonoraireViewSet(viewsets.ModelViewSet):
    queryset = Honoraire.objects.select_related('dossier', 'dossier__comptable_traitant').all()
    serializer_class = HonoraireSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['dossier__comptable_traitant', 'dossier__code']
    search_fields = ['dossier__denomination']

    @action(detail=True, methods=['get'])
    def reglements(self, request, pk=None):
        """Récupère tous les règlements d'un honoraire"""
        honoraire = self.get_object()
        reglements = honoraire.reglements.all()
        serializer = ReglementHonoraireSerializer(reglements, many=True)
        return Response(serializer.data)


class ReglementHonoraireViewSet(viewsets.ModelViewSet):
    queryset = ReglementHonoraire.objects.select_related('honoraire__dossier').all()
    serializer_class = ReglementHonoraireSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type_reglement', 'mode_paiement', 'date_reglement']
    search_fields = ['honoraire__dossier__denomination', 'numero_piece']
    ordering_fields = ['date_reglement', 'montant']
    ordering = ['-date_reglement']


class HonorairePVViewSet(viewsets.ModelViewSet):
    queryset = HonorairePV.objects.all()
    serializer_class = HonorairePVSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['code', 'description']


class ReglementHonorairePVViewSet(viewsets.ModelViewSet):
    queryset = ReglementHonorairePV.objects.all()
    serializer_class = ReglementHonorairePVSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type_reglement', 'date_reglement']
    search_fields = ['honoraire_pv__code', 'reference']
    ordering_fields = ['date_reglement', 'montant']
    ordering = ['-date_reglement']


class SuiviTVAViewSet(viewsets.ModelViewSet):
    queryset = SuiviTVA.objects.select_related('dossier').all()
    serializer_class = SuiviTVASerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['annee', 'dossier__comptable_traitant', 'dossier__declaration_tva']
    search_fields = ['dossier__denomination']

    @action(detail=False, methods=['get'])
    def tableau_bord(self, request):
        """Tableau de bord du suivi TVA"""
        annee = request.query_params.get('annee', timezone.now().year)
        suivis = self.queryset.filter(annee=annee, dossier__actif=True)
        
        stats = {
            'total_dossiers': suivis.count(),
            'dossiers_mensuel_complet': suivis.filter(
                jan=True, fev=True, mars=True, avril=True, mai=True, juin=True,
                juillet=True, aout=True, sep=True, oct=True, nov=True, dec=True
            ).count(),
            'dossiers_trimestriel_complet': suivis.filter(t1=True, t2=True, t3=True, t4=True).count(),
        }
        
        return Response(stats)


class ReclamationViewSet(viewsets.ModelViewSet):
    queryset = Reclamation.objects.select_related('dossier').all()
    serializer_class = ReclamationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['classement', 'priorite', 'type_reclamation', 'date_reception']
    search_fields = ['dossier__denomination', 'type_reclamation']
    ordering_fields = ['date_reception', 'priorite']
    ordering = ['-date_reception']

    @action(detail=False, methods=['get'])
    def en_cours(self, request):
        """Récupère toutes les réclamations en cours"""
        reclamations = self.queryset.filter(classement='EN_COURS')
        serializer = self.get_serializer(reclamations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def urgentes(self, request):
        """Récupère toutes les réclamations urgentes"""
        reclamations = self.queryset.filter(priorite='URGENTE', classement__in=['EN_COURS', 'REPORTE'])
        serializer = self.get_serializer(reclamations, many=True)
        return Response(serializer.data)


class StatistiquesViewSet(viewsets.ViewSet):
    """ViewSet pour les statistiques générales du cabinet"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def cabinet(self, request):
        """Statistiques générales du cabinet"""
        dossiers = Dossier.objects.filter(actif=True)
        
        # Répartition par secteur
        repartition_secteur = dict(
            dossiers.values('secteur_activites')
            .annotate(count=Count('id'))
            .values_list('secteur_activites', 'count')
        )
        
        # Répartition par forme juridique
        repartition_forme = dict(
            dossiers.values('forme_juridique')
            .annotate(count=Count('id'))
            .values_list('forme_juridique', 'count')
        )
        
        stats = {
            'total_comptables': Comptable.objects.filter(actif=True).count(),
            'total_dossiers': dossiers.count(),
            'total_dossiers_actifs': dossiers.filter(statut='EXISTANT').count(),
            'total_pm': dossiers.filter(forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'EURL', 'SASU', 'SAS']).count(),
            'total_pp': dossiers.filter(forme_juridique__in=['EI', 'EIRL', 'AUTO']).count(),
            'total_forfaitaires': dossiers.filter(code__in=['F', 'FS']).count(),
            'total_avec_tva_mensuelle': dossiers.filter(declaration_tva='MENSUELLE').count(),
            'total_avec_tva_trimestrielle': dossiers.filter(declaration_tva='TRIMESTRIELLE').count(),
            'total_exoneres_tva': dossiers.filter(declaration_tva='EXONEREE').count(),
            'repartition_par_secteur': repartition_secteur,
            'repartition_par_forme_juridique': repartition_forme,
        }
        
        serializer = StatistiquesCabinetSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def comptables(self, request):
        """Statistiques par comptable"""
        comptables = Comptable.objects.filter(actif=True)
        stats = []
        
        for comptable in comptables:
            dossiers = comptable.dossiers.filter(actif=True)
            stat = {
                'comptable': ComptableListSerializer(comptable).data,
                'total_dossiers': dossiers.count(),
                'dossiers_pm': dossiers.filter(forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'EURL', 'SASU', 'SAS']).count(),
                'dossiers_pp': dossiers.filter(forme_juridique__in=['EI', 'EIRL', 'AUTO']).count(),
                'dossiers_forfaitaires': dossiers.filter(code__in=['F', 'FS']).count(),
                'dossiers_avec_tva': dossiers.filter(declaration_tva__in=['MENSUELLE', 'TRIMESTRIELLE']).count(),
                'dossiers_sans_tva': dossiers.filter(declaration_tva='EXONEREE').count(),
            }
            stats.append(stat)
        
        serializer = StatistiquesComptableSerializer(stats, many=True)
        return Response(serializer.data)

