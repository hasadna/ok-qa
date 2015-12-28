from django.apps import AppConfig

class Config(AppConfig):
    name = "user"
    def ready(self):
        import signals
