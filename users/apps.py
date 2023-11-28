from django.apps import AppConfig
from .db_connection import check_db_connect


class PatientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        check_db_connect()
