from django.apps import AppConfig


class PaymentConfig(AppConfig):
    name = "hct_mis_api.apps.payment"

    def ready(self) -> None:
        import hct_mis_api.apps.payment.signals  # noqa
