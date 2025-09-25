from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class DeliveryMechanism(TimeStampedUUIDModel):
    class TransferType(models.TextChoices):
        CASH = "CASH", "Cash"
        VOUCHER = "VOUCHER", "Voucher"
        DIGITAL = "DIGITAL", "Digital"

    payment_gateway_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    transfer_type = models.CharField(max_length=255, choices=TransferType.choices, default=TransferType.CASH)
    account_type = models.ForeignKey(
        "payment.AccountType",
        on_delete=models.PROTECT,
        related_name="delivery_mechanisms",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        app_label = "payment"
        ordering = ["code"]
        verbose_name = "Delivery Mechanism"
        verbose_name_plural = "Delivery Mechanisms"

    @classmethod
    def get_choices(cls, only_active: bool = True) -> list[tuple[str, str]]:
        dms = cls.objects.all().values_list("code", "name")
        if only_active:
            dms.filter(is_active=True)
        return list(dms)
