from django.db import models

from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


class SanctionListIndividualCountries(TimeStampedUUIDModel):
    country = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="countries",
    )

    class Meta:
        app_label = "sanction_list"
        verbose_name = "Sanction List Individual/Country"
        verbose_name_plural = "Sanction List Individual/Countries"
        ordering = ("id",)
        indexes = [
            LongNameIndex(fields=["created_at"], name="sanction_list_sanctionlist_created_at_b4a02be4"),
            LongNameIndex(fields=["updated_at"], name="sanction_list_sanctionlist_updated_at_a6c935f2"),
        ]
