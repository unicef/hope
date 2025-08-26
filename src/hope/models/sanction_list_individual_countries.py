from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class SanctionListIndividualCountries(TimeStampedUUIDModel):
    country = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    individual = models.ForeignKey(
        "models.sanction_list_individual.SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="countries",
    )

    class Meta:
        app_label = "sanction_list"
        verbose_name = "Country"
        verbose_name_plural = "Countries"
