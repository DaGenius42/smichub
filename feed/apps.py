from django.apps import AppConfig


class FeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feed'
    
    def ready(self):
        # import signals so Django loads them on startup
        import feed.signals