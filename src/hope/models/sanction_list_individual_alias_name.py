from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class SanctionListIndividualAliasName(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    individual = models.ForeignKey(
        "sanction_list.SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="alias_names",
    )

    class Meta:
        app_label = "sanction_list"
        unique_together = ("individual", "name")
        verbose_name = "Alias"
        verbose_name_plural = "Aliases"
