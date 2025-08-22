from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import os
# Ajoute MSYS2 aux variables d'environnement
os.environ['PATH'] = r'C:\msys64\mingw64\bin;' + os.environ['PATH']
os.environ['FONTCONFIG_PATH'] = r'C:\msys64\mingw64\etc\fonts'


logger = logging.getLogger(__name__)


class EmailService:
    """Service pour l'envoi d'emails"""
    
    def __init__(self):
        self.from_email = settings.EMAIL_HOST_USER or 'noreply@cabinet-comptable.com'
    
    def send_email(self, to_emails, subject, message, html_message=None, attachments=None):
        """
        Envoie un email
        
        Args:
            to_emails (list): Liste des adresses email destinataires
            subject (str): Sujet de l'email
            message (str): Message en texte brut
            html_message (str, optional): Message en HTML
            attachments (list, optional): Liste des fichiers à joindre
        
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            if not to_emails:
                logger.error("Aucune adresse email destinataire fournie")
                return False
            
            # Créer l'email
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=self.from_email,
                to=to_emails,
            )
            
            # Ajouter le contenu HTML si fourni
            if html_message:
                email.content_subtype = "html"
                email.body = html_message
            
            # Ajouter les pièces jointes
            if attachments:
                for attachment in attachments:
                    if isinstance(attachment, dict):
                        email.attach(
                            attachment.get('filename', 'attachment'),
                            attachment.get('content', ''),
                            attachment.get('mimetype', 'application/octet-stream')
                        )
                    elif isinstance(attachment, str):
                        email.attach_file(attachment)
            
            # Envoyer l'email
            email.send()
            logger.info(f"Email envoyé avec succès à {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
            return False

        
    
    def send_template_email(self, to_emails, subject, template_name, context, attachments=None):
        """
        Envoie un email basé sur un template
        
        Args:
            to_emails (list): Liste des adresses email destinataires
            subject (str): Sujet de l'email
            template_name (str): Nom du template (sans extension)
            context (dict): Contexte pour le template
            attachments (list, optional): Liste des fichiers à joindre
        
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            # Rendre le template HTML
            html_message = render_to_string(f'emails/{template_name}.html', context)
            
            # Créer la version texte
            text_message = strip_tags(html_message)
            
            return self.send_email(
                to_emails=to_emails,
                subject=subject,
                message=text_message,
                html_message=html_message,
                attachments=attachments
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email template: {str(e)}")
            return False
    
    def send_notification_reclamation(self, reclamation):
        """Envoie des emails selon qui a créé la réclamation (client ou staff)"""
        from comptables.models import Comptable

        auteur = reclamation.created_by
        dossier = reclamation.dossier
        context = {
            'reclamation': reclamation,
            'dossier': dossier,
        }

        client = dossier.client
        client_email = getattr(client, 'email', None)

        # Vérifie si l’auteur est un client (via profil client lié au user)
        if auteur.role == 'client':

            # Cas 1 : Client crée une réclamation
            # Email au comptable
            comptable_traitant = dossier.comptable_traitant
            if comptable_traitant and comptable_traitant.email:
                self.send_template_email(
                    to_emails=[comptable_traitant.email],
                    subject=f'Nouvelle réclamation - {dossier.denomination}',
                    template_name='notification_reclamation',
                    context=context
                )

            # Accusé de réception au client
            if client_email:
                self.send_template_email(
                    to_emails=[client_email],
                    subject=f'Votre réclamation a bien été reçue - {dossier.denomination}',
                    template_name='notification_reclamation_client',
                    context=context
                )

        else:
            # Cas 2 : Comptable/Admin envoie une réclamation vers le client

            # Email au client
            if client_email:
                self.send_template_email(
                    to_emails=[client_email],
                    subject=f'Réclamation concernant votre dossier : {dossier.denomination}',
                    template_name='reclamation_envoyee_au_client',
                    context=context
                )

            # Accusé d’envoi à l’auteur
            if auteur.email:
                self.send_template_email(
                    to_emails=[auteur.email],
                    subject=f'Votre réclamation a bien été envoyée au client - {dossier.denomination}',
                    template_name='notification_reclamation_staff',
                    context=context
                )

        return True

    def send_welcome_email_to_client(self, user, raw_password):
        """
        Envoie un email de bienvenue au client avec ses identifiants
        """
        try:
            context = {
                'user': user,
                'username': user.username,
                'password': raw_password,
                'login_url': 'http://127.0.0.1:8000/login/',  # à adapter en production
            }
            return self.send_template_email(
                to_emails=[user.email],
                subject='Bienvenue sur votre espace client',
                template_name='bienvenue_client',  # emails/bienvenue_client.html
                context=context
            )
        except Exception as e:
            logger.error(f"Erreur envoi email de bienvenue: {str(e)}")
            return False



    
    def send_rappel_tva(self, dossiers_en_retard):
        """Envoie un rappel pour les déclarations TVA en retard"""
        if not dossiers_en_retard:
            return False
        
        # Grouper par comptable
        comptables_dossiers = {}
        for dossier in dossiers_en_retard:
            comptable = dossier.comptable_traitant
            if comptable.email:
                if comptable not in comptables_dossiers:
                    comptables_dossiers[comptable] = []
                comptables_dossiers[comptable].append(dossier)
        
        success_count = 0
        for comptable, dossiers in comptables_dossiers.items():
            context = {
                'comptable': comptable,
                'dossiers': dossiers,
                'nb_dossiers': len(dossiers),
            }
            
            if self.send_template_email(
                to_emails=[comptable.email],
                subject=f'Rappel TVA - {len(dossiers)} dossier(s) en retard',
                template_name='rappel_tva',
                context=context
            ):
                success_count += 1
        
        return success_count > 0
    
    def send_rapport_mensuel(self, comptable, stats):
        """Envoie le rapport mensuel à un comptable"""
        if not comptable.email:
            return False
        
        context = {
            'comptable': comptable,
            'stats': stats,
            'mois': stats.get('mois', ''),
            'annee': stats.get('annee', ''),
        }
        
        return self.send_template_email(
            to_emails=[comptable.email],
            subject=f'Rapport mensuel - {stats.get("mois", "")} {stats.get("annee", "")}',
            template_name='rapport_mensuel',
            context=context
        )
    
    def send_emails_globaux(self, subject, message, dossier_codes=None, comptable_ids=None):
        """
        Envoie des emails globaux selon les critères spécifiés
        
        Args:
            subject (str): Sujet de l'email
            message (str): Message de l'email
            dossier_codes (list, optional): Codes des dossiers concernés
            comptable_ids (list, optional): IDs des comptables concernés
        
        Returns:
            dict: Résultat de l'envoi avec statistiques
        """
        from dossiers.models import Dossier
        from comptables.models import Comptable
        
        emails = set()
        
        # Récupérer les emails selon les critères
        if dossier_codes:
            # Emails des dossiers spécifiés
            dossier_emails = Dossier.objects.filter(
                code__in=dossier_codes,
                actif=True,
                email__isnull=False
            ).values_list('email', flat=True)
            emails.update(dossier_emails)
            
            # Emails des comptables de ces dossiers
            comptable_emails = Comptable.objects.filter(
                dossiers__code__in=dossier_codes,
                dossiers__actif=True,
                email__isnull=False
            ).distinct().values_list('email', flat=True)
            emails.update(comptable_emails)
        
        if comptable_ids:
            # Emails des comptables spécifiés
            comptable_emails = Comptable.objects.filter(
                id__in=comptable_ids,
                actif=True,
                email__isnull=False
            ).values_list('email', flat=True)
            emails.update(comptable_emails)
        
        # Si aucun critère spécifié, envoyer à tous les comptables actifs
        if not dossier_codes and not comptable_ids:
            comptable_emails = Comptable.objects.filter(
                actif=True,
                email__isnull=False
            ).values_list('email', flat=True)
            emails.update(comptable_emails)
        
        # Envoyer l'email
        emails_list = list(emails)
        if emails_list:
            success = self.send_email(
                to_emails=emails_list,
                subject=subject,
                message=message
            )
            
            return {
                'success': success,
                'nb_emails': len(emails_list),
                'emails': emails_list
            }
        else:
            return {
                'success': False,
                'nb_emails': 0,
                'emails': [],
                'error': 'Aucune adresse email trouvée'
            }

