from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from hope.models.utils import AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel


class PaymentPlanGroup(TimeStampedUUIDModel, UnicefIdentifiedModel, AdminUrlMixin):
    class BackgroundActionStatus(models.TextChoices):
        XLSX_EXPORTING = "XLSX_EXPORTING", "Exporting XLSX file"
        XLSX_EXPORT_ERROR = "XLSX_EXPORT_ERROR", "Export XLSX file Error"

    cycle = models.ForeignKey(
        "program.ProgramCycle",
        on_delete=models.CASCADE,
        related_name="payment_plan_groups",
        verbose_name=_("Programme Cycle"),
    )
    name = models.CharField(max_length=255, default="Default Group")
    export_file = models.ForeignKey(
        "core.FileTemp",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Merged XLSX export file [sys]",
    )
    background_action_status = models.CharField(
        max_length=50,
        default=None,
        db_index=True,
        blank=True,
        null=True,
        choices=BackgroundActionStatus.choices,
        help_text="Background Action Status for celery task [sys]",
    )

    class Meta:
        app_label = "payment"
        verbose_name = "Payment Plan Group"
        unique_together = ("cycle", "name")
        ordering = ["created_at"]

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict]:
        if self.cycle.payment_plan_groups.count() == 1:
            raise ValidationError("Cannot delete the last group in a cycle.")
        return super().delete(*args, **kwargs)  # type: ignore

    def __str__(self) -> str:
        return f"{self.name} for {self.cycle}"
