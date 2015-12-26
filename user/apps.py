from django.apps import AppConfig

class Config(AppConfig):
    name = "oshot"
    def ready(self):
        import signals
