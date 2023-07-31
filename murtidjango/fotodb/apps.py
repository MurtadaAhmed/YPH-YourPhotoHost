from django.apps import AppConfig

import murtidjango.settings


class FotodbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fotodb'

    def ready(self):
        import fotodb.signals
