from django.apps import AppConfig


class AccountabilityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hope.apps.accountability"

    def ready(self) -> None:
        import hope.models  # noqa
