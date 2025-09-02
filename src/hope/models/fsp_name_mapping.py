from django.db import models

from hope.models.financial_service_provider import FinancialServiceProvider


class FspNameMapping(models.Model):
    class SourceModel(models.TextChoices):
        INDIVIDUAL = "Individual"
        HOUSEHOLD = "Household"
        ACCOUNT = "Account"

    external_name = models.CharField(max_length=255)
    # this is a python attribute / db field name of source model (possibly mixin with all FSP names mapping attributes):
    hope_name = models.CharField(max_length=255)  # default copy of external name
    source = models.CharField(max_length=30, choices=SourceModel.choices, default=SourceModel.ACCOUNT)
    fsp = models.ForeignKey(
        FinancialServiceProvider,
        on_delete=models.CASCADE,
        related_name="names_mappings",
    )

    class Meta:
        app_label = "payment"

    def __str__(self) -> str:
        return self.external_name  # pragma: no cover
