from django.apps import AppConfig


class SchedulersConfig(AppConfig):
    name = 'schedulers'

    def ready(self):
        import schedulers.signals