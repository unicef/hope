from django.db import models
from django.db.models import UniqueConstraint

from hope.models.utils import TimeStampedUUIDModel


class ProgramPartnerThrough(TimeStampedUUIDModel):  # TODO: remove after migration to RoleAssignment
    program = models.ForeignKey(
        "Program",
        on_delete=models.CASCADE,
        related_name="program_partner_through",
    )
    partner = models.ForeignKey(
        "account.Partner",
        on_delete=models.CASCADE,
        related_name="program_partner_through",
    )
    areas = models.ManyToManyField("geo.Area", related_name="program_partner_through", blank=True)
    full_area_access = models.BooleanField(default=False)

    class Meta:
        app_label = "program"
        constraints = [
            UniqueConstraint(
                fields=["program", "partner"],
                name="unique_program_partner",
            )
        ]
