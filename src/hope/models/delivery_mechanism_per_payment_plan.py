from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class DeliveryMechanismPerPaymentPlan(TimeStampedUUIDModel):
    payment_plan = models.OneToOneField(
        "payment.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="delivery_mechanism_per_payment_plan",
    )
    financial_service_provider = models.ForeignKey(
        "payment.FinancialServiceProvider",
        on_delete=models.PROTECT,
        related_name="delivery_mechanisms_per_payment_plan",
        null=True,
    )
    delivery_mechanism = models.ForeignKey("models.delivery_mechanism.DeliveryMechanism", on_delete=models.SET_NULL, null=True)
    delivery_mechanism_order = models.PositiveIntegerField()
    sent_to_payment_gateway = models.BooleanField(default=False)

    class Meta:
        app_label = "payment"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "payment_plan",
                    "delivery_mechanism",
                    "delivery_mechanism_order",
                ],
                name="unique payment_plan_delivery_mechanism",
            ),
        ]
