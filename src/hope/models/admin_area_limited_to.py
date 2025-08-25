from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class AdminAreaLimitedTo(TimeStampedUUIDModel):
    """Model to limit the admin area access for a partner.

    Partners with full area access for a certain program will not have any area limits - no record in this model.
    """

    partner = models.ForeignKey("account.Partner", related_name="admin_area_limits", on_delete=models.CASCADE)
    program = models.ForeignKey("program.Program", related_name="admin_area_limits", on_delete=models.CASCADE)
    areas = models.ManyToManyField("geo.Area", related_name="admin_area_limits", blank=True)

    class Meta:
        unique_together = ("partner", "program")

    def clean(self) -> None:
        if self.program.partner_access != self.program.SELECTED_PARTNERS_ACCESS:
            raise ValidationError(f"Area limits cannot be set for programs with {self.program.partner_access} access.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)
