from django.apps import AppConfig


class SanctionListConfig(AppConfig):
    name = "hope.apps.sanction_list"

    def ready(self) -> None:
        import hope.models  # noqa

        from .strategies.eu import EUSanctionList
        from .strategies.registry import registry
        from .strategies.un import UNSanctionList

        registry.register(UNSanctionList)
        registry.register(EUSanctionList)
