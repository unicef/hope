from django.db import models

from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


class SanctionListIndividualAliasName(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="alias_names",
    )

    class Meta:
        app_label = "sanction_list"
        unique_together = ("individual", "name")
        verbose_name = "Alias"
        verbose_name_plural = "Aliases"
        ordering = ("name",)
        indexes = [
            LongNameIndex(fields=["created_at"], name="sanction_list_sanctionlist_created_at_f103fe15"),
            LongNameIndex(fields=["updated_at"], name="sanction_list_sanctionlist_updated_at_c863d190"),
        ]
