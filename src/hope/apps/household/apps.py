from django.apps import AppConfig


class HouseholdConfig(AppConfig):
    name = "hope.apps.household"

    def ready(self) -> None:
        import hope.models  # noqa
