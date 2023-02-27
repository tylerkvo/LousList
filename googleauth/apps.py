from django.apps import AppConfig


class GoogleauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'googleauth'

    def ready(self):
        import googleauth.signals
        
# Django - User Profile
# https://dev.to/earthcomfy/django-user-profile-3hik