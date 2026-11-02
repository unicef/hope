from django.db import models

from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


class BeneficiaryGroup(TimeStampedUUIDModel):
    name = models.CharField(max_length=255, unique=True)
    group_label = models.CharField(max_length=255)
    group_label_plural = models.CharField(max_length=255)
    member_label = models.CharField(max_length=255)
    member_label_plural = models.CharField(max_length=255)
    master_detail = models.BooleanField(default=True)

    class Meta:
        app_label = "program"
        verbose_name = "Beneficiary Group"
        verbose_name_plural = "Beneficiary Groups"
        ordering = ("name",)
        permissions = (("reset_sync_date", "Can reset sync date"),)
        indexes = [
            LongNameIndex(fields=["created_at"], name="program_beneficiarygroup_created_at_b78ee65a"),
            LongNameIndex(fields=["updated_at"], name="program_beneficiarygroup_updated_at_c80e3d34"),
        ]

    def __str__(self) -> str:
        return self.name
