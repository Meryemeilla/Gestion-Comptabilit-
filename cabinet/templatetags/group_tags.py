"""
Module applicatif.

Fichier: cabinet/templatetags/group_tags.py
"""

# ==================== Imports ====================
from django import template
register = template.Library()

@register.filter(name='has_group')
# ==================== Fonctions ====================
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()