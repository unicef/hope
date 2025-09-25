from django.apps import AppConfig


class PaymentConfig(AppConfig):
    name = "hope.apps.payment"

    def ready(self) -> None:
        import hope.apps.payment.signals  # noqa

        import hope.models  # noqa
