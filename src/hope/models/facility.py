from django.db import models
from django.db.models import UniqueConstraint

from hope.models.utils import (
    TimeStampedUUIDModel,
)


class Facility(TimeStampedUUIDModel):
    name = models.CharField(max_length=255, help_text="Facility or Organization name")
    business_area = models.ForeignKey("core.BusinessArea", related_name="facilities", on_delete=models.CASCADE, help_text="Business area")
    admin_area = models.ForeignKey("geo.Area", related_name="facilities", on_delete=models.PROTECT, help_text="Admin area")

    class Meta:
        app_label = "core"
        constraints = [
            UniqueConstraint(
                fields=["name", "business_area", "admin_area"],
                name="unique_for_ba_name_and_admin_area",
            ),
        ]
        ordering = ["business_area", "name"]
        verbose_name_plural = "Facilities"
