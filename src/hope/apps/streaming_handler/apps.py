from django.apps import AppConfig


class StreamingHandlerConfig(AppConfig):
    name = "hope.apps.streaming_handler"

    def ready(self) -> None:
        import hope.apps.streaming_handler.handlers  # noqa: F401
