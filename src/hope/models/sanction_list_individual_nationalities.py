from django.db import models

from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


class SanctionListIndividualNationalities(TimeStampedUUIDModel):
    nationality = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="nationalities",
    )

    class Meta:
        app_label = "sanction_list"
        verbose_name = "Nationality"
        verbose_name_plural = "Nationalities"
        unique_together = ("individual", "nationality")
        ordering = ("id",)
        indexes = [
            LongNameIndex(fields=["created_at"], name="sanction_list_sanctionlist_created_at_6f9dffc3"),
            LongNameIndex(fields=["updated_at"], name="sanction_list_sanctionlist_updated_at_330fb903"),
        ]
