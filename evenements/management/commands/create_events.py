"""
Module applicatif.

Fichier: evenements/management/commands/create_events.py
"""

# ==================== Imports ====================
from django.core.management.base import BaseCommand
from evenements.models import Evenement
from datetime import date

# ==================== Classes ====================
class Command(BaseCommand):
    help = 'Crée les événements par défaut avec leurs messages prédéfinis.'

    def handle(self, *args, **options):
        events_data = [
            {
                'nom': 'عيد الأضحى',
                'message': "عيد أضحى مبارك 🌙🐑 أعاده الله عليكم بالخير واليمن والبركات، وكل عام وأنتم بخير."
            },
            {
                'nom': 'عيد الفطر',
                'message': "عيد فطر مبارك سعيد 🎉🌙 تقبل الله منا ومنكم صالح الأعمال، وكل عام وأنتم بخير وصحة وسعادة."
            },
            {
                'nom': 'رمضان',
                'message': "رمضان مبارك كريم 🌙✨ أعاده الله عليكم بالصحة والعافية، ونسأل الله أن يتقبل صيامكم وقيامكم وصالح أعمالكم."
            },
            {
                'nom': 'ذكرى المولد النبوي الشريف',
                'message': "بمناسبة ذكرى المولد النبوي الشريف 🌟 نتمنى لكم مناسبة سعيدة مليئة بالنور والسكينة، وكل عام وأنتم بخير."
            },
            {
                'nom': 'السنة الميلادية',
                'message': "سنة ميلادية سعيدة 🎆🎉 نتمنى لكم سنة جديدة مليئة بالنجاح والفرح والإنجازات."
            },
            {
                'nom': 'السنة الهجرية',
                'message': "سنة هجرية مباركة 🌙📅 نسأل الله أن يجعلها سنة خير وبركة عليكم وعلى ذويكم."
            },
        ]

        for event_data in events_data:
            event, created = Evenement.objects.get_or_create(
                nom=event_data['nom'],
                defaults={
                    'date': date.today(), # La date sera mise à jour manuellement ou via un script ultérieur
                    'message': event_data['message'],
                    'actif': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Événement '{event.nom}' créé avec succès."))
            else:
                self.stdout.write(self.style.WARNING(f"Événement '{event.nom}' existe déjà. Mise à jour du message."))
                event.message = event_data['message']
                event.save()
                self.stdout.write(self.style.SUCCESS(f"Événement '{event.nom}' mis à jour avec succès."))