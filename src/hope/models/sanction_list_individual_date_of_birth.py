from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class SanctionListIndividualDateOfBirth(TimeStampedUUIDModel):
    date = models.DateField()
    individual = models.ForeignKey(
        "sanction_list.SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="dates_of_birth",
    )

    class Meta:
        app_label = "sanction_list"
        verbose_name = "Birthday"
        unique_together = ("individual", "date")
