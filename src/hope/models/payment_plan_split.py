from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class PaymentPlanSplit(TimeStampedUUIDModel):
    MAX_CHUNKS = 50
    MIN_NO_OF_PAYMENTS_IN_CHUNK = 10

    class SplitType(models.TextChoices):
        NO_SPLIT = "NO_SPLIT", "No Split"
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
    split_type = models.CharField(choices=SplitType.choices, max_length=24, default=SplitType.NO_SPLIT)
    chunks_no = models.IntegerField(null=True, blank=True)
    sent_to_payment_gateway = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        app_label = "payment"
        ordering = ("-created_at",)
