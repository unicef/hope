from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class SanctionListIndividualNationalities(TimeStampedUUIDModel):
    nationality = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    individual = models.ForeignKey(
        "models.sanction_list_individual.SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="nationalities",
    )

    class Meta:
        app_label = "sanction_list"
        verbose_name = "Nationality"
        verbose_name_plural = "Nationalities"
        unique_together = ("individual", "nationality")
