from django.db import models

from hope.models.country import Country
from hope.models.utils import TimeStampedModel


class FinancialInstitution(TimeStampedModel):
    class FinancialInstitutionType(models.TextChoices):
        BANK = "bank", "Bank"
        TELCO = "telco", "Telco"
        OTHER = "other", "Other"

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=FinancialInstitutionType.choices)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
    swift_code = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.id} {self.name}: {self.type}"  # pragma: no cover

    class Meta:
        app_label = "payment"
