"""
PHARMACIST APP CONFIGURATION
Django app configuration with signal registration
"""

from django.apps import AppConfig


class PharmacistAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pharmacist_app'
    verbose_name = 'Pharmacy Management System'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import pharmacist_app.signals
        except ImportError:
            pass
