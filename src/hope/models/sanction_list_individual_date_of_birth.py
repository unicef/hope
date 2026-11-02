from django.db import models

from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


class SanctionListIndividualDateOfBirth(TimeStampedUUIDModel):
    date = models.DateField()
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="dates_of_birth",
    )

    class Meta:
        app_label = "sanction_list"
        verbose_name = "Birthday"
        unique_together = ("individual", "date")
        ordering = ("-created_at",)
        indexes = [
            LongNameIndex(fields=["created_at"], name="sanction_list_sanctionlist_created_at_fe1aae1c"),
            LongNameIndex(fields=["updated_at"], name="sanction_list_sanctionlist_updated_at_b0324dfd"),
        ]
