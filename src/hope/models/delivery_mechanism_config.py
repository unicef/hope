from django.contrib.postgres.fields import ArrayField
from django.db import models

from hope.models.country import Country
from hope.models.delivery_mechanism import DeliveryMechanism
from hope.models.financial_service_provider import FinancialServiceProvider


class DeliveryMechanismConfig(models.Model):
    delivery_mechanism = models.ForeignKey(DeliveryMechanism, on_delete=models.PROTECT)
    fsp = models.ForeignKey(FinancialServiceProvider, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True)
    required_fields = ArrayField(default=list, base_field=models.CharField(max_length=255))

    def __str__(self) -> str:
        return f"{self.delivery_mechanism.code} - {self.fsp.name}"  # pragma: no cover

    class Meta:
        app_label = "payment"
