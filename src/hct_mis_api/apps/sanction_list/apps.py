from django.apps import AppConfig


class SanctionListConfig(AppConfig):
    name = "hct_mis_api.apps.sanction_list"

    def ready(self) -> None:
        from .strategies.eu import EUSanctionList
        from .strategies.registry import registry
        from .strategies.un import UNSanctionList

        registry.register(UNSanctionList)
        registry.register(EUSanctionList)
