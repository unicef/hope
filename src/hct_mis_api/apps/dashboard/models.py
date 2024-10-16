from django.db import models
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class DashReport(TimeStampedUUIDModel):
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    STATUSES = (
        (IN_PROGRESS, _("Processing")),
        (COMPLETED, _("Generated")),
        (FAILED, _("Failed")),
    )

    business_area = models.OneToOneField("core.BusinessArea", related_name="dashreports", on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=IN_PROGRESS)
    file = models.FileField(blank=True, null=True, upload_to="dashreports/")

    def __str__(self) -> str:
        return f"Report for {self.business_area} (Status: {self.get_status_display()})"

    class Meta:
        ordering = ["-created_at"]
