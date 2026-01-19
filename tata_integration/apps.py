from django.apps import AppConfig

class TataIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tata_integration'
    
    def ready(self):
        # Start auto sync scheduler when Django starts
        from .scheduler import scheduler
        scheduler.start()