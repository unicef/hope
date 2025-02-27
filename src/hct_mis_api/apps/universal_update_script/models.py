from django.contrib.postgres.fields import ArrayField
from django.core.cache import cache
from django.db import models

from hct_mis_api.apps.household.models import DocumentType
from hct_mis_api.apps.payment.models import DeliveryMechanism
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.models import CeleryEnabledModel, TimeStampedModel


class UniversalUpdate(
    TimeStampedModel,
    CeleryEnabledModel,
):
    individual_fields = ArrayField(base_field=models.CharField(max_length=255), default=list)
    individual_flex_fields_fields = ArrayField(base_field=models.CharField(max_length=255), default=list)
    household_fields = ArrayField(base_field=models.CharField(max_length=255), default=list)
    household_flex_fields_fields = ArrayField(base_field=models.CharField(max_length=255), default=list)
    document_types = models.ManyToManyField(DocumentType, blank=True)
    delivery_mechanisms = models.ManyToManyField(DeliveryMechanism, blank=True)
    template_file = models.FileField(blank=True, null=True)
    update_file = models.FileField(blank=True, null=True)

    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    backup_snapshot = models.FileField(blank=True, null=True)
    saved_logs = models.TextField(blank=True, null=True, default="")
    unicef_ids = models.TextField(blank=True, null=True)

    @property
    def logs(self) -> str:
        if cache.get(f"{self.id}_logs"):
            return cache.get(f"{self.id}_logs")
        return self.saved_logs

    def save_logs(self, log: str) -> None:
        self.saved_logs += f"{log}\n"
        cache.set(f"{self.id}_logs", self.saved_logs)
        self.save()

    def clear_logs(self) -> None:
        self.saved_logs = ""
        cache.delete(f"{self.id}_logs")
        self.save()
