from django.apps import AppConfig


class ChangelogConfig(AppConfig):
    name = "hope.apps.changelog"

    def ready(self) -> None:
        import hope.models  # noqa
