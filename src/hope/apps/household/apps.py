from django.apps import AppConfig


class HouseholdConfig(AppConfig):
    name = "hope.apps.household"

    def ready(self):
        from hope.apps.household.signals import register_bulk_signals

        register_bulk_signals()
