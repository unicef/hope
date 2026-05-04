from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from hope.models.utils import AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel


class PaymentPlanGroup(TimeStampedUUIDModel, UnicefIdentifiedModel, AdminUrlMixin):
    cycle = models.ForeignKey(
        "program.ProgramCycle",
        on_delete=models.CASCADE,
        related_name="payment_plan_groups",
        verbose_name=_("Programme Cycle"),
    )
    name = models.CharField(max_length=255, default="Default Group")

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
        return self.name
