from django.db import models

from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


class BeneficiaryGroup(TimeStampedUUIDModel):
    name = models.CharField(max_length=255, unique=True)
    group_label = models.CharField(max_length=255)
    group_label_plural = models.CharField(max_length=255)
    member_label = models.CharField(max_length=255)
    member_label_plural = models.CharField(max_length=255)
    payee_type = models.ForeignKey(
        "core.PayeeType",
        on_delete=models.PROTECT,
        null=True,
        related_name="payee_labels",
    )
    data_collecting_types = models.ManyToManyField(
        "core.DataCollectingType",
        blank=True,
        related_name="payee_labels",
        help_text="Leave empty to allow every Data Collecting Type of the Payee Type",
    )
    active = models.BooleanField(default=True, help_text="Inactive Payee Labels cannot be used in new programs")

    class Meta:
        app_label = "program"
        verbose_name = "Payee Label"
        verbose_name_plural = "Payee Labels"
        ordering = ("name",)
        permissions = (("reset_sync_date", "Can reset sync date"),)
        indexes = [
            LongNameIndex(fields=["created_at"], name="program_beneficiarygroup_created_at_b78ee65a"),
            LongNameIndex(fields=["updated_at"], name="program_beneficiarygroup_updated_at_c80e3d34"),
        ]

    def __str__(self) -> str:
        return self.name
