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
    individual_fields = ArrayField(
        base_field=models.CharField(max_length=255),
        default=list,
        help_text="Selected Individual Fields which can be updated",
    )
    individual_flex_fields_fields = ArrayField(
        base_field=models.CharField(max_length=255),
        default=list,
        help_text="Selected Individual Flex Fields which can be updated",
    )
    household_fields = ArrayField(
        base_field=models.CharField(max_length=255),
        default=list,
        help_text="Selected Household Fields which can be updated",
    )
    household_flex_fields_fields = ArrayField(
        base_field=models.CharField(max_length=255),
        default=list,
        help_text="Selected Household Flex Fields which can be updated",
    )
    document_types = models.ManyToManyField(
        DocumentType, blank=True, help_text="Selected Document Types of which Documents can be updated"
    )
    delivery_mechanisms = models.ManyToManyField(
        DeliveryMechanism, blank=True, help_text="Selected Delivery Mechanisms of which Wallets data can be updated"
    )
    template_file = models.FileField(
        blank=True,
        null=True,
        help_text="Generated Template XLSX File, contains columns for data to be updated. Contains also rows for unicef_ids to be updated",
    )
    update_file = models.FileField(
        blank=True,
        null=True,
        help_text="Uploaded File, contains data to be updated. After clicking a button to update, data will be updated",
    )

    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    backup_snapshot = models.FileField(
        blank=True,
        null=True,
        help_text="Backup Snapshot File, contains data before update. File updated on each start of update process.",
    )
    saved_logs = models.TextField(
        blank=True, null=True, default="", help_text="Logs of the update process, saved in db"
    )
    unicef_ids = models.TextField(blank=True, null=True, help_text="Unicef IDs used only to generate template file")

    class Meta:
        permissions = [
            ("can_run_universal_update", "Can run universal update"),
            ("can_generate_universal_update_template", "Can generate universal update template"),
        ]

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
