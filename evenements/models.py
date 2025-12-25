"""
Modèles Django et logique d’accès aux données.

Fichier: evenements/models.py
"""

# ==================== Imports ====================
from django.db import models

# ==================== Classes ====================
class Evenement(models.Model):
    NOM_EVENEMENT_CHOICES = [
        ('AID_AL_ADHA', 'عيد الأضحى'),
        ('AID_AL_FITR', 'عيد الفطر'),
        ('RAMADAN', 'رمضان'),
        ('MAWLID_NABAWI', 'ذكرى المولد النبوي الشريف'),
        ('NEW_YEAR_GREGORIAN', 'السنة الميلادية'),
        ('NEW_YEAR_ISLAMIC', 'السنة الهجرية'),
    ]

    DEFAULT_MESSAGES = {
        'AID_AL_ADHA': "عيد أضحى مبارك 🌙🐑 أعاده الله عليكم بالخير واليمن والبركات، وكل عام وأنتم بخير.",
        'AID_AL_FITR': "عيد فطر مبارك سعيد 🎉🌙 تقبل الله منا ومنكم صالح الأعمال، وكل عام وأنتم بخير وصحة وسعادة.",
        'RAMADAN': "رمضان مبارك كريم 🌙✨ أعاده الله عليكم بالصحة والعافية، ونسأل الله أن يتقبل صيامكم وقيامكم وصالح أعمالكم.",
        'MAWLID_NABAWI': "بمناسبة ذكرى المولد النبوي الشريف 🌟 نتمنى لكم مناسبة سعieuse مليئة بالنور والسكينة، وكل عام وأنتم بخير.",
        'NEW_YEAR_GREGORIAN': "سنة ميلadie سعيدة 🎆🎉 نتمنى لكم سنة nouvelle مليئة بالنجاح والفرح والإنجazements.",
        'NEW_YEAR_ISLAMIC': "سنة hijri مباركة 🌙📅 نسأل الله أن يجعلها سنة خير وبركة عليكم وعلى ذويكم.",
    }

    nom = models.CharField(max_length=50, choices=NOM_EVENEMENT_CHOICES, unique=True)
    date = models.DateField()
    message = models.TextField(default="")
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"

    def __str__(self):
        return self.get_nom_display()

    def save(self, *args, **kwargs):
        if not self.message:
            self.message = self.DEFAULT_MESSAGES.get(self.nom, "")
        super().save(*args, **kwargs)
