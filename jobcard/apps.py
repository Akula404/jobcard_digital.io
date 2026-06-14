from django.apps import AppConfig


class JobcardConfig(AppConfig):
    name = 'jobcard'

# jobcard/apps.py
def ready(self):
    import jobcard.signals