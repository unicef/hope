from django.db import models

from hope.models.financial_institution import FinancialInstitution
from hope.models.financial_service_provider import FinancialServiceProvider
from hope.models.utils import LongNameIndex, TimeStampedModel


class FinancialInstitutionMapping(TimeStampedModel):
    financial_service_provider = models.ForeignKey(FinancialServiceProvider, on_delete=models.CASCADE)
    financial_institution = models.ForeignKey(FinancialInstitution, on_delete=models.CASCADE)
    code = models.CharField(max_length=30)

    class Meta:
        app_label = "payment"
        ordering = ("id",)
        unique_together = ("financial_service_provider", "financial_institution")
        indexes = [
            LongNameIndex(fields=["created_at"], name="payment_financialinstitutionmapping_created_at_f136c2dc"),
            LongNameIndex(fields=["updated_at"], name="payment_financialinstitutionmapping_updated_at_e681b3d7"),
        ]

    def __str__(self) -> str:
        return f"{self.financial_institution} to {self.financial_service_provider}: {self.code}"
