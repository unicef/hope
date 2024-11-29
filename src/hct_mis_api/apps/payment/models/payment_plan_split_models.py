from typing import Optional

from django.db import models

from hct_mis_api.apps.payment.models.financial_service_provider_models import (
    FinancialServiceProvider,
)
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class PaymentPlanSplitPayments(TimeStampedUUIDModel):
    payment_plan_split = models.ForeignKey(
        "payment.PaymentPlanSplit", on_delete=models.CASCADE, related_name="payment_plan_split"
    )
    payment = models.ForeignKey("payment.Payment", on_delete=models.CASCADE, related_name="payment_plan_split_payment")

    class Meta:
        unique_together = ("payment_plan_split", "payment")


class PaymentPlanSplit(TimeStampedUUIDModel):
    MAX_CHUNKS = 50
    MIN_NO_OF_PAYMENTS_IN_CHUNK = 10

    class SplitType(models.TextChoices):
        BY_RECORDS = "BY_RECORDS", "By Records"
        BY_COLLECTOR = "BY_COLLECTOR", "By Collector"
        BY_ADMIN_AREA1 = "BY_ADMIN_AREA1", "By Admin Area 1"
        BY_ADMIN_AREA2 = "BY_ADMIN_AREA2", "By Admin Area 2"
        BY_ADMIN_AREA3 = "BY_ADMIN_AREA3", "By Admin Area 3"

    payment_plan = models.ForeignKey(
        "payment.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="splits",
    )
    split_type = models.CharField(choices=SplitType.choices, max_length=24)
    chunks_no = models.IntegerField(null=True, blank=True)
    payments = models.ManyToManyField(
        "payment.Payment",
        through="PaymentPlanSplitPayments",
        related_name="+",
    )
    sent_to_payment_gateway = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    @property
    def financial_service_provider(self) -> "FinancialServiceProvider":
        return self.payment_plan.delivery_mechanisms.first().financial_service_provider

    @property
    def chosen_configuration(self) -> Optional[str]:
        return self.payment_plan.delivery_mechanisms.first().chosen_configuration

    @property
    def delivery_mechanism(self) -> Optional[str]:
        return self.payment_plan.delivery_mechanisms.first().delivery_mechanism
