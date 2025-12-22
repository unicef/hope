from django.db import models

from hope.models.utils import TimeStampedUUIDModel


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

    def __str__(self) -> str:
        return self.name
