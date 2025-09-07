from django.apps import AppConfig


class UserauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userauth'

    def ready(self):
            import userauth.signals  # This line ensures signal handlers get registered


# class UserauthConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'userauth'

#     def ready(self):
#         import userauth.signals  # This line ensures signal handlers get registered