"""
Module applicatif.

Fichier: evenements/tasks_update_dates.py
"""

# ==================== Imports ====================
from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import date
import holidays
from evenements.models import Evenement

logger = get_task_logger(__name__)

@shared_task
# ==================== Fonctions ====================
def update_event_dates_annually():
    logger.info("Starting annual event dates update task...")
    current_year = date.today().year
    next_year = current_year + 1

    # Calculate Gregorian holidays for next year
    fr_holidays = holidays.FR(years=next_year)
    for holiday_date, holiday_name in fr_holidays.items():
        Evenement.objects.get_or_create(
            nom=holiday_name,
            date=holiday_date,
            type_evenement='GREGORIEN',
            defaults={'description': f'Fête grégorienne: {holiday_name}'}
        )
        logger.info(f"Added/Updated Gregorian holiday: {holiday_name} on {holiday_date}")

    # Calculate Islamic holidays for next year (using a common country for example, e.g., Morocco)
    # Note: Islamic holidays can vary based on moon sighting and region.
    # This is an approximation and might need adjustment based on specific requirements.
    ma_holidays = holidays.MA(years=next_year)
    for holiday_date, holiday_name in ma_holidays.items():
        Evenement.objects.get_or_create(
            nom=holiday_name,
            date=holiday_date,
            type_evenement='ISLAMIQUE',
            defaults={'description': f'Fête islamique: {holiday_name}'}
        )
        logger.info(f"Added/Updated Islamic holiday: {holiday_name} on {holiday_date}")

    logger.info("Annual event dates update task completed.")