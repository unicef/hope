from django.db import models

from hope.models.financial_institution import FinancialInstitution
from hope.models.financial_service_provider import FinancialServiceProvider
from hope.models.utils import TimeStampedModel


class FinancialInstitutionMapping(TimeStampedModel):
    financial_service_provider = models.ForeignKey(FinancialServiceProvider, on_delete=models.CASCADE)
    financial_institution = models.ForeignKey(FinancialInstitution, on_delete=models.CASCADE)
    code = models.CharField(max_length=30)

    class Meta:
        app_label = "payment"
        unique_together = ("financial_service_provider", "financial_institution")

    def __str__(self) -> str:
        return f"{self.financial_institution} to {self.financial_service_provider}: {self.code}"
