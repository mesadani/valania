from django.apps import AppConfig
import os

class ValappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'valApp'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':  # evita que se ejecute dos veces con runserver
            from valApp import scheduler
            scheduler.start()
