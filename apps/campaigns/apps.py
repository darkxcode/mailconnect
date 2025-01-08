from django.apps import AppConfig

class CampaignsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.campaigns'

    def ready(self):
        import apps.campaigns.signals
